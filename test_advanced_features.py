import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app import models
from main import app

TEST_DATABASE_URL = "sqlite:///test_advanced.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_advanced.db"):
        try:
            os.remove("test_advanced.db")
        except PermissionError:
            pass

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    # Clean new tables
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
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# Authentication Headers
HEADERS = {"X-API-Key": "deneb-secret-key"}


# ----------------- ASSISTANTS TESTS -----------------

def test_assistant_crud(client):
    # 1. Create
    payload = {
        "name": "Backend Guru",
        "description": "FastAPI specialist",
        "system_prompt": "You are a backend guru.",
        "avatar": "fa-solid fa-server"
    }
    response = client.post("/api/v1/assistants/", json=payload, headers=HEADERS)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Backend Guru"
    assert "id" in data
    assistant_id = data["id"]

    # 2. Get Single
    response = client.get(f"/api/v1/assistants/{assistant_id}", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["system_prompt"] == "You are a backend guru."

    # 3. List & Filter
    response = client.get("/api/v1/assistants/?search=Guru", headers=HEADERS)
    assert response.status_code == 200
    res_list = response.json()
    assert res_list["total_items"] == 1
    assert res_list["items"][0]["id"] == assistant_id

    # 4. Update
    update_payload = {"name": "Senior Backend Guru"}
    response = client.put(f"/api/v1/assistants/{assistant_id}", json=update_payload, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["name"] == "Senior Backend Guru"

    # 5. Delete
    response = client.delete(f"/api/v1/assistants/{assistant_id}", headers=HEADERS)
    assert response.status_code == 204
    
    # Verify deleted
    response = client.get(f"/api/v1/assistants/{assistant_id}", headers=HEADERS)
    assert response.status_code == 404


# ----------------- MEMORIES TESTS -----------------

def test_memory_crud(client):
    # 1. Create
    payload = {
        "memory_text": "User is building a web scraper in python.",
        "category": "professional"
    }
    response = client.post("/api/v1/memories/", json=payload, headers=HEADERS)
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "professional"
    assert "id" in data
    memory_id = data["id"]

    # 2. List Memories
    response = client.get("/api/v1/memories/?category=professional", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["total_items"] == 1

    # 3. Update
    response = client.put(f"/api/v1/memories/{memory_id}", json={"memory_text": "User uses Python 3.12"}, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["memory_text"] == "User uses Python 3.12"

    # 4. Delete
    response = client.delete(f"/api/v1/memories/{memory_id}", headers=HEADERS)
    assert response.status_code == 204


# ----------------- PROJECTS & CONVERSATIONS TESTS -----------------

def test_project_and_conversation_workflow(client):
    # 1. Create Project
    proj_response = client.post("/api/v1/projects", json={"name": "scraping project", "description": "web scraper files"}, headers=HEADERS)
    assert proj_response.status_code == 201
    project_id = proj_response.json()["id"]

    # 2. Create Assistant
    ast_response = client.post("/api/v1/assistants/", json={"name": "Coder", "system_prompt": "You write clean code."}, headers=HEADERS)
    assert ast_response.status_code == 201
    assistant_id = ast_response.json()["id"]

    # 3. Create Conversation inside Project
    conv_payload = {
        "project_id": project_id,
        "assistant_id": assistant_id,
        "title": "Initial Scraper Setup",
        "chat_mode": "normal"
    }
    conv_response = client.post("/api/v1/conversations", json=conv_payload, headers=HEADERS)
    assert conv_response.status_code == 201
    conversation_id = conv_response.json()["id"]
    assert conv_response.json()["project_id"] == project_id

    # 4. List Projects (and check count)
    response = client.get("/api/v1/projects", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["items"][0]["conversations_count"] == 1

    # 5. Send message inside conversation (simulate normal response)
    msg_response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"content": "Suggest a scraping library"},
        headers=HEADERS
    )
    assert msg_response.status_code == 200
    msg_data = msg_response.json()
    assert "response" in msg_data
    assert msg_data["conversation_id"] == conversation_id

    # 6. Verify message logs saved in DB
    logs_response = client.get(f"/api/v1/conversations/{conversation_id}/messages", headers=HEADERS)
    assert logs_response.status_code == 200
    assert len(logs_response.json()) == 2  # User message and assistant message
    assert logs_response.json()[0]["role"] == "user"
    assert logs_response.json()[1]["role"] == "assistant"


# ----------------- WEB SEARCH & CANVAS ARTIFACT TESTS -----------------

def test_web_search_and_canvas_extraction(client):
    # Setup Assistant
    ast_response = client.post("/api/v1/assistants/", json={"name": "Helper", "system_prompt": "You are a coding tutor."}, headers=HEADERS)
    assistant_id = ast_response.json()["id"]

    # Create Conversation in Web Search Mode
    conv_payload = {
        "assistant_id": assistant_id,
        "title": "Search Query thread",
        "chat_mode": "web_search"
    }
    conv_response = client.post("/api/v1/conversations", json=conv_payload, headers=HEADERS)
    conversation_id = conv_response.json()["id"]

    # 1. Send Query in Web Search Mode
    # Query contains "fastapi" to trigger mock search hit
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"content": "how does fastapi routing work?"},
        headers=HEADERS
    )
    assert response.status_code == 200
    data = response.json()
    assert data["chat_mode"] == "web_search"
    assert len(data["sources"]) > 0  # Sources retrieved
    assert "fastapi.tiangolo.com" in data["sources"][0]["url"]

    # 2. Trigger Canvas Artifact Generation
    # Sending a message requesting python code
    code_response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        json={"content": "write python script for routing"},
        headers=HEADERS
    )
    assert code_response.status_code == 200
    code_data = code_response.json()
    
    # Artifact must be parsed out
    assert code_data["artifact"] is not None
    assert code_data["artifact"]["type"] == "code"
    assert "def process_data" in code_data["artifact"]["content"]
    # Chat message text replaced with summary link note
    assert "Artifact Canvas" in code_data["response"]

    # 3. Retrieve Artifacts list
    art_list_response = client.get(f"/api/v1/conversations/{conversation_id}/artifacts", headers=HEADERS)
    assert art_list_response.status_code == 200
    assert len(art_list_response.json()) == 1
    assert art_list_response.json()[0]["id"] == code_data["artifact"]["id"]
