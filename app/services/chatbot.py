from sqlalchemy.orm import Session
from app import models, schemas

def get_chatbot(db: Session, chatbot_id: int) -> models.Chatbot:
    """Retrieve a single chatbot by its ID."""
    return db.query(models.Chatbot).filter(models.Chatbot.id == chatbot_id).first()


def get_chatbots(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str = None,
    model: str = None,
    is_active: bool = None
):
    """
    Retrieve chatbots with optional searching (by name/description), 
    filtering (by model engine or active status), and pagination.
    Returns a tuple of (items, total_count).
    """
    query = db.query(models.Chatbot)

    # Search filter (case-insensitive substring matching on name/description)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.Chatbot.name.ilike(search_filter)) |
            (models.Chatbot.description.ilike(search_filter))
        )

    # Model engine filter
    if model:
        query = query.filter(models.Chatbot.model == model)

    # Status filter
    if is_active is not None:
        query = query.filter(models.Chatbot.is_active == is_active)

    # Calculate total count of matching records (before pagination)
    total_count = query.count()

    # Apply pagination and fetch items
    items = query.offset(skip).limit(limit).all()
    
    return items, total_count


def create_chatbot(db: Session, chatbot: schemas.ChatbotCreate) -> models.Chatbot:
    """Create a new chatbot agent."""
    db_chatbot = models.Chatbot(**chatbot.model_dump())
    db.add(db_chatbot)
    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot


def update_chatbot(db: Session, db_chatbot: models.Chatbot, chatbot_update: schemas.ChatbotUpdate) -> models.Chatbot:
    """Perform a partial update on an existing chatbot."""
    update_data = chatbot_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_chatbot, key, value)
    
    db.commit()
    db.refresh(db_chatbot)
    return db_chatbot


def delete_chatbot(db: Session, db_chatbot: models.Chatbot) -> None:
    """Delete a chatbot. Cascade deletes linked knowledge bases."""
    db.delete(db_chatbot)
    db.commit()


def simulate_chat_response(db: Session, chatbot_id: int, query: str, top_k: int = 2):
    """
    Simulate chatbot execution with knowledge base retrieval.
    Searches across all chunks linked to the chatbot using keyword/token overlap.
    """
    chatbot = get_chatbot(db=db, chatbot_id=chatbot_id)
    if not chatbot:
        return None

    # Retrieve all chunks across knowledge bases owned by this chatbot
    chunks = db.query(models.KnowledgeBaseChunk).join(
        models.KnowledgeBase, models.KnowledgeBaseChunk.knowledge_base_id == models.KnowledgeBase.id
    ).filter(
        models.KnowledgeBase.chatbot_id == chatbot_id
    ).all()

    # Score chunks based on keyword token overlap and substring match
    query_tokens = set(query.lower().split())
    scored_chunks = []

    for chunk in chunks:
        chunk_content_lower = chunk.content.lower()
        score = sum(1 for token in query_tokens if token in chunk_content_lower)
        if query.lower() in chunk_content_lower:
            score += 10
        scored_chunks.append((score, chunk))

    # Sort chunks by score descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    # Gather top_k chunks that have a positive overlap score
    retrieved_chunks = []
    for score, chunk in scored_chunks[:top_k]:
        if score > 0:
            retrieved_chunks.append(chunk)

    # Format the retrieved context block
    if retrieved_chunks:
        context_parts = []
        for chunk in retrieved_chunks:
            kb_name = chunk.knowledge_base.name if chunk.knowledge_base else "Document"
            context_parts.append(f"Source: {kb_name} (Chunk #{chunk.chunk_index})\nContent: {chunk.content}")
        context_str = "\n---\n".join(context_parts)
    else:
        context_str = "No relevant knowledge base context found."

    final_prompt = (
        f"System Prompt:\n{chatbot.system_prompt}\n\n"
        f"Retrieved Context:\n---\n{context_str}\n---\n\n"
        f"User Query:\n{query}"
    )

    if retrieved_chunks:
        simulated_response = (
            f"[Simulated Response using {len(retrieved_chunks)} context chunk(s) from model '{chatbot.model}']\n"
            f"Based on the retrieved context from your knowledge base, here is the answer: "
            f"I found matching information regarding '{query}' in our database. "
            f"Here is a summary: {retrieved_chunks[0].content[:150]}..."
        )
    else:
        simulated_response = (
            f"[Simulated Response with no context from model '{chatbot.model}']\n"
            f"I couldn't find any relevant facts in my knowledge base matching '{query}'. "
            f"Relying on default prompt instructions: {chatbot.system_prompt[:80]}..."
        )

    return {
        "chatbot_id": chatbot.id,
        "chatbot_name": chatbot.name,
        "model": chatbot.model,
        "temperature": chatbot.temperature,
        "query": query,
        "retrieved_context": [
            {
                "knowledge_base_id": chunk.knowledge_base_id,
                "knowledge_base_name": chunk.knowledge_base.name,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content
            } for chunk in retrieved_chunks
        ],
        "final_constructed_prompt": final_prompt,
        "simulated_response": simulated_response
    }


def chat_with_chatbot(db: Session, chatbot_id: int, messages: list, top_k: int = 2, override_grok_key: str = None):
    """
    Execute chat completion for the chatbot.
    Retrieves relevant knowledge base chunks, builds the compiled prompt, and 
    invokes Grok's chat completions API. Falls back to simulation if no key is configured.
    """
    import httpx
    from app.config import settings

    chatbot = get_chatbot(db=db, chatbot_id=chatbot_id)
    if not chatbot:
        return None

    # Get the latest user query from messages to use for context retrieval
    query = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            query = msg.get("content", "")
            break

    # Retrieve and score relevant chunks
    retrieved_chunks = []
    if query:
        chunks = db.query(models.KnowledgeBaseChunk).join(
            models.KnowledgeBase, models.KnowledgeBaseChunk.knowledge_base_id == models.KnowledgeBase.id
        ).filter(
            models.KnowledgeBase.chatbot_id == chatbot_id
        ).all()

        query_tokens = set(query.lower().split())
        scored_chunks = []

        for chunk in chunks:
            chunk_content_lower = chunk.content.lower()
            score = sum(1 for token in query_tokens if token in chunk_content_lower)
            if query.lower() in chunk_content_lower:
                score += 10
            scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        for score, chunk in scored_chunks[:top_k]:
            if score > 0:
                retrieved_chunks.append(chunk)

    # Format the retrieved context block
    if retrieved_chunks:
        context_parts = []
        for chunk in retrieved_chunks:
            kb_name = chunk.knowledge_base.name if chunk.knowledge_base else "Document"
            context_parts.append(f"Source: {kb_name} (Chunk #{chunk.chunk_index})\nContent: {chunk.content}")
        context_str = "\n---\n".join(context_parts)
    else:
        context_str = "No relevant knowledge base context found."

    # Prepend context to the chatbot's system prompt
    system_instruction = chatbot.system_prompt or "You are a helpful assistant."
    if retrieved_chunks:
        system_instruction += (
            f"\n\nUse the following retrieved context documents to help answer the user query:\n"
            f"---\n{context_str}\n---"
        )

    # Build the full messages array for the completion model
    api_messages = [{"role": "system", "content": system_instruction}]
    for msg in messages:
        if msg.get("role") != "system":
            api_messages.append({"role": msg.get("role"), "content": msg.get("content", "")})

    api_key = override_grok_key if override_grok_key else settings.GROK_API_KEY
    model_name = chatbot.model if (chatbot.model and chatbot.model.startswith("grok")) else "grok-beta"
    
    is_mock = True
    warning_msg = None
    assistant_response = ""

    if api_key:
        try:
            # Call Grok (xAI) completions API
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "messages": api_messages,
                "model": model_name,
                "temperature": chatbot.temperature,
                "stream": False
            }
            response = httpx.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                completion_data = response.json()
                assistant_response = completion_data["choices"][0]["message"]["content"]
                is_mock = False
            else:
                warning_msg = f"Grok API returned error code {response.status_code}: {response.text}"
                assistant_response = f"[Grok API Error: Status {response.status_code}]\nFailed to execute Grok completion. Showing simulated RAG response instead."
        except Exception as e:
            warning_msg = f"Failed to connect to Grok API: {str(e)}"
            assistant_response = f"[Grok API Connection Error]\nFailed to connect to the xAI endpoint: {str(e)}"
    else:
        warning_msg = "GROK_API_KEY is not configured on the server or provided in the UI header settings."

    # If we are mocking / falling back, synthesize a response using the context chunks
    if is_mock and not assistant_response:
        if retrieved_chunks:
            assistant_response = (
                f"[Simulated response with {len(retrieved_chunks)} RAG context chunk(s)]\n"
                f"Based on the retrieved context, here is the simulated answer: "
                f"Reference documents indicate: '{retrieved_chunks[0].content[:150]}...'"
            )
        else:
            assistant_response = (
                f"[Simulated response with no context]\n"
                f"Since no Grok API key is configured, I am returning a simulated answer using prompt instructions: "
                f"'{chatbot.system_prompt[:80]}...'"
            )

    return {
        "chatbot_id": chatbot.id,
        "chatbot_name": chatbot.name,
        "model": chatbot.model,
        "temperature": chatbot.temperature,
        "retrieved_context": [
            {
                "knowledge_base_id": chunk.knowledge_base_id,
                "knowledge_base_name": chunk.knowledge_base.name,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content
            } for chunk in retrieved_chunks
        ],
        "final_constructed_prompt": system_instruction,
        "response": assistant_response,
        "is_mock": is_mock,
        "warning": warning_msg
    }


