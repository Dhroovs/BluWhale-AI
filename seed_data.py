from app import models, database
from app.database import engine

def seed_database():
    db = database.SessionLocal()
    
    try:
        # Clear old database records for a clean reload
        db.query(models.KnowledgeBaseChunk).delete()
        db.query(models.KnowledgeBase).delete()
        db.query(models.Artifact).delete()
        db.query(models.Message).delete()
        db.query(models.Conversation).delete()
        db.query(models.Project).delete()
        db.query(models.Assistant).delete()
        db.query(models.Memory).delete()
        db.query(models.Chatbot).delete()
        db.commit()

        print("Seeding database with DENEB AI Enterprise Chatbot Platform configurations...")

        # 1. Create Default Assistants
        deneb_assistant = models.Assistant(
            name="deneb AI Assistant",
            description="Official coordinator and support agent for the DENEB AI Enterprise Chatbot platform roadmap.",
            system_prompt=(
                "You are the deneb AI Assistant, the primary coordinator for the DENEB AI enterprise chatbot platform. "
                "You help developers build production-grade FastAPI web services, configure database connections, "
                "and design semantic Retrieval-Augmented Generation (RAG) pipelines. Speak with confidence, "
                "be technical and concise, and refer to our development roadmap milestones."
            ),
            avatar="fa-solid fa-robot"
        )

        backend_architect = models.Assistant(
            name="Backend Architect",
            description="Senior architect specializing in FastAPI validation, SQLAlchemy models, and high-performance system design.",
            system_prompt=(
                "You are a senior backend architect specializing in Python, FastAPI, and PostgreSQL. "
                "Provide clean, type-safe, and structured code snippets using Pydantic, database connection pools, "
                "and clean modular architecture guidelines. Be rigorous and focus on database and api design."
            ),
            avatar="fa-solid fa-server"
        )

        product_manager = models.Assistant(
            name="Product Manager",
            description="Agile PM expert helping you write specifications, structure features, and draft roadmap releases.",
            system_prompt=(
                "You are a tech product manager. You help developers write clean product requirements documents (PRDs), "
                "structure product backlogs, plan feature releases, and define clear user stories with acceptance criteria."
            ),
            avatar="fa-solid fa-clipboard-list"
        )

        db.add_all([deneb_assistant, backend_architect, product_manager])
        db.commit()

        # Refresh database session to get auto-generated IDs
        db.refresh(deneb_assistant)
        db.refresh(backend_architect)
        db.refresh(product_manager)

        print(f"Assistants seeded! deneb AI Assistant ID: {deneb_assistant.id}")

        # 2. Create Default Projects
        proj_onboarding = models.Project(
            name="Onboarding & Setup",
            description="DENEB AI platform developer setup and internship roadmap materials."
        )
        proj_startup = models.Project(
            name="Startup Ideas",
            description="Brainstorming software tools and business roadmaps."
        )
        db.add_all([proj_onboarding, proj_startup])
        db.commit()
        db.refresh(proj_onboarding)
        db.refresh(proj_startup)

        # 3. Create Default Conversations
        conv_fastapi = models.Conversation(
            project_id=proj_onboarding.id,
            assistant_id=deneb_assistant.id,
            title="FastAPI Routing & Database Setup",
            chat_mode="normal"
        )
        conv_prd = models.Conversation(
            project_id=proj_startup.id,
            assistant_id=product_manager.id,
            title="Product Requirements Document",
            chat_mode="normal"
        )
        db.add_all([conv_fastapi, conv_prd])
        db.commit()
        db.refresh(conv_fastapi)
        db.refresh(conv_prd)

        # 4. Create Seed Message exchanges
        msg1 = models.Message(
            conversation_id=conv_fastapi.id,
            role="user",
            content="What are the key learning topics for FastAPI?"
        )
        msg2 = models.Message(
            conversation_id=conv_fastapi.id,
            role="assistant",
            content=(
                "Key learning topics for Phase 1: \n"
                "1. Request validation using Pydantic models.\n"
                "2. Standard REST status codes: 200 OK, 201 Created, 204 No Content, 422 Unprocessable.\n"
                "3. Database integration using SQLAlchemy ORM (engine, sessions, and transaction rollbacks).\n"
                "4. Query-based paginated listings and text filtering."
            )
        )
        db.add_all([msg1, msg2])
        db.commit()

        # 5. Create Default User Memories
        mem1 = models.Memory(
            user_id="default_user",
            memory_text="User is a junior full-stack developer on the Deneb AI team.",
            category="professional"
        )
        mem2 = models.Memory(
            user_id="default_user",
            memory_text="User prefers using Python, FastAPI, and PostgreSQL for database backends.",
            category="preferences"
        )
        db.add_all([mem1, mem2])
        db.commit()

        # 6. Create Knowledge Base articles linked to deneb AI Assistant
        kb1 = models.KnowledgeBase(
            name="FastAPI & REST API Guidelines",
            description="Reference study guide for building compliant REST APIs in FastAPI.",
            data_source="text",
            content=(
                "FastAPI is a modern web framework for building APIs with Python 3.8+. "
                "Key learning topics: 1. Request body validation using Pydantic models. "
                "2. Standard REST status codes: 201 Created (POST success), 200 OK (GET/PUT success), "
                "204 No Content (DELETE success), 422 Unprocessable Entity (input validation errors). "
                "3. Query-based list controls: always implement limit-based pagination and search/filtering."
            ),
            assistant_id=deneb_assistant.id
        )

        kb2 = models.KnowledgeBase(
            name="Retrieval-Augmented Generation (RAG)",
            description="Introduction to RAG architecture, vector databases, and semantic search.",
            data_source="text",
            content=(
                "Retrieval-Augmented Generation (RAG) is a technique that references external knowledge "
                "sources before an LLM synthesizes a response. The workflow includes: "
                "- Parsing & Chunking: Dividing long text documents into smaller semantically cohesive segments. "
                "- Vector Embeddings: Converting text segments into numeric vectors. "
                "- Indexing: Storing vectors in databases like Chroma or pgvector. "
                "- Semantic Search: Finding the top matching document chunks to inject into the system prompt."
            ),
            assistant_id=deneb_assistant.id
        )

        kb3 = models.KnowledgeBase(
            name="AI Agents & Tool Calling Workflows",
            description="Guide to orchestrating LLM agents with external function capabilities.",
            data_source="text",
            content=(
                "An AI Agent is an autonomous loop that uses an LLM to plan tasks, reflect on inputs, "
                "and execute tools. Tool Calling (Function Calling) allows the model to output a structured "
                "JSON block representing a function call. The runtime environment executes the function, "
                "collects the string output, and passes it back to the model. This is the core foundation "
                "for building complex multi-step workflows."
            ),
            assistant_id=deneb_assistant.id
        )

        kb4 = models.KnowledgeBase(
            name="DENEB AI Internship Roadmap",
            description="The four structured phases of our enterprise AI chatbot developer internship.",
            data_source="text",
            content=(
                "Deneb AI Internship Milestones:\n"
                "- Phase 1: API Development (FastAPI REST endpoints, SQLite ORM database integration, search/filter, and paginated lists).\n"
                "- Phase 2: LLMs & Prompt Engineering (Cloud-hosted and self-hosted models, system instructions, temperature, and context windows).\n"
                "- Phase 3: RAG & Vector Databases (Chunking engines, semantic index searches, and knowledge injections).\n"
                "- Phase 4: AI Agents & Tool Calling (Integrating external APIs, function mappings, and multi-agent loops)."
            ),
            assistant_id=deneb_assistant.id
        )

        db.add_all([kb1, kb2, kb3, kb4])
        db.commit()

        # Generate database chunks for the seeded documents
        from app.utils.text_splitter import split_text
        for kb in [kb1, kb2, kb3, kb4]:
            db.refresh(kb)
            chunks = split_text(kb.content)
            for idx, chunk_content in enumerate(chunks):
                db_chunk = models.KnowledgeBaseChunk(
                    knowledge_base_id=kb.id,
                    chunk_index=idx,
                    content=chunk_content
                )
                db.add(db_chunk)
        db.commit()
        print("Knowledge bases for deneb AI Assistant seeded and chunked successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    database.Base.metadata.create_all(bind=engine)
    seed_database()
