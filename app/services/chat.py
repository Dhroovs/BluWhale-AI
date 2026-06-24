import re
import json
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app import models, schemas
from app.services.llm import llm_service
from app.services.search import search_service
from app.services.memory import memory_service

class ChatService:
    @staticmethod
    def process_chat_message(
        db: Session,
        conversation_id: int,
        user_message_text: str,
        user_id: str = "default_user",
        override_grok_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process user message inside a conversation:
        1. Fetch conversation history, project, and assistant settings.
        2. Auto-extract profile facts and save to Memory database.
        3. Retrieve relevant User Memories and inject into system prompt.
        4. Fetch RAG documents linked to assistant and score semantic overlap.
        5. Execute Web Search (SearchService) if chat_mode is 'web_search'.
        6. Invoke LLMService for Grok completions (or simulated fallback).
        7. Parse generated responses for code/SQL blocks, saving them as Canvas Artifacts.
        8. Persist messages and return response payload.
        """
        # 1. Fetch Conversation & Assistant
        conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
        if not conv:
            return None

        assistant = conv.assistant
        if not assistant:
            return None

        # 2. Extract memory from current user input (automated memory extraction)
        memory_service.extract_and_save_memories(db, user_message_text, user_id=user_id)

        # 3. Retrieve User Memories to inject into prompt context
        db_memories, _ = memory_service.get_memories(db, user_id=user_id, limit=10)
        memory_str = ""
        if db_memories:
            mem_parts = []
            for mem in db_memories:
                mem_parts.append(f"- Category [{mem.category.upper()}]: {mem.memory_text}")
            memory_str = "\n".join(mem_parts)

        # 4. Fetch RAG Context (Knowledge Base chunks linked to the Assistant)
        retrieved_chunks = []
        chunks = db.query(models.KnowledgeBaseChunk).join(
            models.KnowledgeBase, models.KnowledgeBaseChunk.knowledge_base_id == models.KnowledgeBase.id
        ).filter(
            models.KnowledgeBase.assistant_id == assistant.id
        ).all()

        if chunks and user_message_text:
            query_tokens = set(user_message_text.lower().split())
            scored_chunks = []
            for chunk in chunks:
                chunk_content_lower = chunk.content.lower()
                score = sum(1 for token in query_tokens if token in chunk_content_lower)
                if user_message_text.lower() in chunk_content_lower:
                    score += 10
                scored_chunks.append((score, chunk))

            scored_chunks.sort(key=lambda x: x[0], reverse=True)
            for score, chunk in scored_chunks[:2]:
                if score > 0:
                    retrieved_chunks.append(chunk)

        rag_context_str = ""
        if retrieved_chunks:
            context_parts = []
            for chunk in retrieved_chunks:
                kb_name = chunk.knowledge_base.name if chunk.knowledge_base else "Doc"
                context_parts.append(f"Source: {kb_name} (Chunk #{chunk.chunk_index})\nContent: {chunk.content}")
            rag_context_str = "\n---\n".join(context_parts)

        # 5. Execute Web Search Mode if configured
        search_hits = []
        search_context_str = ""
        if conv.chat_mode == "web_search":
            search_hits = search_service.query(user_message_text, limit=3)
            if search_hits:
                search_parts = []
                for idx, hit in enumerate(search_hits):
                    search_parts.append(f"Search Source #{idx+1}: {hit['title']} ({hit['url']})\nSnippet: {hit['snippet']}")
                search_context_str = "\n---\n".join(search_parts)

        # 6. Build Consolidated System Prompt
        system_instruction = assistant.system_prompt or "You are a helpful assistant."
        
        # Inject Memories Context
        if memory_str:
            system_instruction += (
                f"\n\nYou have the following remembered details about this user:\n"
                f"===\n{memory_str}\n===\n"
                f"Personalize your answers based on this context only if relevant."
            )
            
        # Inject RAG Database Context
        if rag_context_str:
            system_instruction += (
                f"\n\nUse these semantic database documents to help verify facts and answer the query:\n"
                f"---\n{rag_context_str}\n---"
            )

        # Inject Web Search Results Context
        if search_context_str:
            system_instruction += (
                f"\n\nUse these web search results to answer the query with fresh facts. "
                f"Ensure you reference sources where appropriate:\n"
                f"---\n{search_context_str}\n---"
            )

        # 7. Gather Conversation History
        # Retrieve last 15 messages from DB for continuity
        db_messages = db.query(models.Message).filter(
            models.Message.conversation_id == conversation_id
        ).order_by(models.Message.created_at.asc()).limit(15).all()

        api_messages = [{"role": "system", "content": system_instruction}]
        for msg in db_messages:
            api_messages.append({"role": msg.role, "content": msg.content})

        # Append new user message to compiler list
        api_messages.append({"role": "user", "content": user_message_text})

        # Save user message to database
        db_user_msg = models.Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message_text
        )
        db.add(db_user_msg)
        db.commit()

        # 8. Call LLM Service
        # We try to use the assistant model name, mapping custom ones to grok-beta
        llm_model = "grok-beta"
        llm_temp = 0.7
        # Fetch configurations from a mock mapping if custom assistant
        if assistant.name == "Backend Architect":
            llm_model = "grok-2"
            llm_temp = 0.2
        elif assistant.name == "Product Manager":
            llm_model = "grok-beta"
            llm_temp = 0.8

        llm_response = llm_service.call_grok(
            messages=api_messages,
            model=llm_model,
            temperature=llm_temp,
            api_key=override_grok_key
        )

        assistant_response = llm_response["text"]
        is_mock = llm_response["is_mock"]
        warning_msg = llm_response["warning"]

        # If call is mocked, synthesize a clean mock response using search & RAG context
        if is_mock:
            mock_text = ""
            if search_hits:
                mock_text += (
                    f"**[Web Search Answer]**\nBased on web search results for *'{user_message_text}'*, here is the summary:\n"
                    f"I found relevant web entries at {', '.join([h['title'] for h in search_hits])}. "
                    f"Sources point out that: {search_hits[0]['snippet'][:200]}...\n\n"
                )
            if retrieved_chunks:
                mock_text += (
                    f"**[Semantic RAG Context]**\nAdditionally, matching documents in our memory store suggest:\n"
                    f"'{retrieved_chunks[0].content[:200]}...'\n\n"
                )
            if not mock_text:
                mock_text = (
                    f"[Simulated response from {assistant.name}]\n"
                    f"Thank you for your message: '{user_message_text}'. Since Grok is in offline mode, "
                    f"I am relying on my system instructions: '{assistant.system_prompt[:150]}...'"
                )
            
            # If user asks to generate a script/code, ensure we outputs an artifact format for canvas testing
            if "write" in user_message_text.lower() or "code" in user_message_text.lower() or "program" in user_message_text.lower() or "script" in user_message_text.lower():
                mock_text += (
                    "\nHere is a python script implementing that request:\n"
                    "```python\n"
                    "def process_data(data):\n"
                    "    # Automated code script template\n"
                    "    print('Processing database inputs in deneb AI...')\n"
                    "    parsed = [x.strip() for x in data if x]\n"
                    "    return parsed\n"
                    "\n"
                    "# Execution block\n"
                    "result = process_data(['FastAPI', 'RAG', 'PostgreSQL'])\n"
                    "print(result)\n"
                    "```"
                )

            assistant_response = mock_text

        # 9. Extract Artifacts (Canvas files) from response
        cleaned_response, db_artifact = ChatService._extract_artifacts(conversation_id, assistant_response, db)

        # 10. Save assistant response to database
        sources_str = json.dumps(search_hits) if search_hits else None
        db_assistant_msg = models.Message(
            conversation_id=conversation_id,
            role="assistant",
            content=cleaned_response,
            sources=sources_str
        )
        db.add(db_assistant_msg)
        db.commit()
        db.refresh(db_assistant_msg)

        # 11. Package payload
        artifact_res = None
        if db_artifact:
            artifact_res = schemas.ArtifactResponse.model_validate(db_artifact)

        return {
            "response": cleaned_response,
            "message_id": db_assistant_msg.id,
            "conversation_id": conversation_id,
            "chat_mode": conv.chat_mode,
            "sources": search_hits if search_hits else None,
            "retrieved_context_count": len(retrieved_chunks),
            "artifact": artifact_res,
            "warning": warning_msg
        }

    @staticmethod
    def _extract_artifacts(conversation_id: int, response_text: str, db: Session) -> Tuple[str, Optional[models.Artifact]]:
        """Parse markdown blocks to create structured Artifact Canvas entities."""
        # Matches ```[language]\n[content]\n```
        pattern = r"```(\w+)?\n([\s\S]+?)\n```"
        match = re.search(pattern, response_text)
        
        if match:
            lang = (match.group(1) or "text").lower()
            
            # Map to standard Feature 5 types: code, markdown, json, sql, text
            if lang in ["python", "javascript", "js", "html", "css", "cpp", "c", "java", "rust", "go", "bash", "sh"]:
                doc_type = "code"
            elif lang in ["sql"]:
                doc_type = "sql"
            elif lang in ["json"]:
                doc_type = "json"
            elif lang in ["markdown", "md"]:
                doc_type = "markdown"
            else:
                doc_type = "text"

            content = match.group(2).strip()

            # Create and save artifact
            db_artifact = models.Artifact(
                conversation_id=conversation_id,
                type=doc_type,
                content=content
            )
            db.add(db_artifact)
            db.commit()
            db.refresh(db_artifact)

            # Format in-chat display summary
            cleaned_text = re.sub(
                pattern,
                f"\n\n*(I have generated a `{doc_type}` document. You can view, copy, and download the full output in the Artifact Canvas panel on the right.)*",
                response_text,
                count=1
            )
            return cleaned_text, db_artifact
            
        return response_text, None

chat_service = ChatService()
