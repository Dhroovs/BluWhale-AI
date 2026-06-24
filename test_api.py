import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app import models
from main import app

# Use a separate test database file.
TEST_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fixture to build and tear down database tables.
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Clean up the file test.db after testing completes.
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except PermissionError:
            pass


# Fixture to provide a clean database session per test.
@pytest.fixture
def db():
    # Clear tables to start with a fresh state.
    db = TestingSessionLocal()
    db.query(models.KnowledgeBaseChunk).delete()
    db.query(models.KnowledgeBase).delete()
    db.query(models.Chatbot).delete()
    db.commit()
    try:
        yield db
    finally:
        db.close()


# Fixture to override FastAPI's get_db dependency.
@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, headers={"X-API-Key": "deneb-secret-key"}) as c:
        yield c
    app.dependency_overrides.clear()


# --- TEST CASES ---

def test_create_chatbot(client):
    payload = {
        "name": "Deneb Navigator",
        "description": "Guides systems",
        "system_prompt": "Persona test",
        "model": "deneb-core-v1",
        "temperature": 0.5,
        "is_active": True
    }
    response = client.post("/api/v1/chatbots/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Deneb Navigator"
    assert data["id"] is not None
    assert "created_at" in data


def test_create_chatbot_invalid_temp(client):
    payload = {
        "name": "Invalid Temp Bot",
        "model": "deneb-core-v1",
        "temperature": 1.2,  # Must be between 0.0 and 1.0
        "is_active": True
    }
    response = client.post("/api/v1/chatbots/", json=payload)
    assert response.status_code == 422  # Validation Error


def test_create_chatbot_invalid_model(client):
    payload = {
        "name": "Invalid Model Bot",
        "model": "gpt-99",  # Not supported model type
        "temperature": 0.5,
        "is_active": True
    }
    response = client.post("/api/v1/chatbots/", json=payload)
    assert response.status_code == 422  # Validation Error


def test_get_chatbot_details(client):
    # Setup test bot
    payload = {
        "name": "Search Target",
        "model": "deneb-core-v1",
        "temperature": 0.7
    }
    create_resp = client.post("/api/v1/chatbots/", json=payload)
    bot_id = create_resp.json()["id"]

    # Test GET
    response = client.get(f"/api/v1/chatbots/{bot_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Search Target"

    # Test GET non-existent
    response = client.get("/api/v1/chatbots/99999")
    assert response.status_code == 404


def test_update_chatbot_details(client):
    # Setup
    payload = {"name": "Old Name", "model": "deneb-core-v1", "temperature": 0.5}
    bot_id = client.post("/api/v1/chatbots/", json=payload).json()["id"]

    # Test update
    update_payload = {"name": "New Name", "temperature": 0.9}
    response = client.put(f"/api/v1/chatbots/{bot_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["temperature"] == 0.9
    assert data["model"] == "deneb-core-v1"  # Retains old value


def test_delete_chatbot(client):
    # Setup
    bot_id = client.post("/api/v1/chatbots/", json={"name": "Delete Me"}).json()["id"]

    # Test DELETE
    response = client.delete(f"/api/v1/chatbots/{bot_id}")
    assert response.status_code == 204

    # Confirm it is gone
    response = client.get(f"/api/v1/chatbots/{bot_id}")
    assert response.status_code == 404


def test_list_chatbots_pagination_and_search(client):
    # Seed 3 chatbots
    client.post("/api/v1/chatbots/", json={"name": "Alpha Coder", "model": "grok-2", "is_active": True})
    client.post("/api/v1/chatbots/", json={"name": "Beta Creative", "model": "grok-2-1212", "is_active": True})
    client.post("/api/v1/chatbots/", json={"name": "Gamma Helper", "model": "grok-beta", "is_active": False})

    # Test List Pagination (page=1, size=2)
    response = client.get("/api/v1/chatbots/?page=1&size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 3
    assert len(data["items"]) == 2
    assert data["total_pages"] == 2
    assert data["page"] == 1
    assert data["size"] == 2

    # Test List Search
    response = client.get("/api/v1/chatbots/?search=Coder")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 1
    assert data["items"][0]["name"] == "Alpha Coder"

    # Test List Filter status
    response = client.get("/api/v1/chatbots/?is_active=false")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 1
    assert data["items"][0]["name"] == "Gamma Helper"


def test_create_knowledge_base(client):
    # Setup chatbot first
    bot_id = client.post("/api/v1/chatbots/", json={"name": "Owner Bot"}).json()["id"]

    # Create KB
    kb_payload = {
        "name": "System Handbook",
        "description": "Rules of engagement",
        "data_source": "text",
        "content": "Line 1. Line 2.",
        "chatbot_id": bot_id
    }
    response = client.post("/api/v1/knowledge-bases/", json=kb_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "System Handbook"
    assert data["chatbot_id"] == bot_id


def test_create_kb_invalid_chatbot(client):
    kb_payload = {
        "name": "Orphan KB",
        "data_source": "text",
        "content": "No parent",
        "chatbot_id": 99999  # Non-existent ID
    }
    response = client.post("/api/v1/knowledge-bases/", json=kb_payload)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]


def test_delete_chatbot_cascades_kb(client):
    # Setup bot and attach KB
    bot_id = client.post("/api/v1/chatbots/", json={"name": "Target Bot"}).json()["id"]
    kb_id = client.post("/api/v1/knowledge-bases/", json={
        "name": "Linked Doc",
        "data_source": "text",
        "content": "Will be deleted",
        "chatbot_id": bot_id
    }).json()["id"]

    # Assert KB is reachable
    assert client.get(f"/api/v1/knowledge-bases/{kb_id}").status_code == 200

    # Delete Chatbot
    assert client.delete(f"/api/v1/chatbots/{bot_id}").status_code == 204

    # Assert KB is deleted automatically via DB cascade
    assert client.get(f"/api/v1/knowledge-bases/{kb_id}").status_code == 404


def test_api_key_verification(db):
    # Test client without correct API key
    with TestClient(app) as no_key_client:
        response = no_key_client.get("/api/v1/chatbots/")
        assert response.status_code == 401
        
    with TestClient(app, headers={"X-API-Key": "wrong-key"}) as wrong_key_client:
        response = wrong_key_client.get("/api/v1/chatbots/")
        assert response.status_code == 401


def test_knowledge_base_auto_chunking(client):
    # Setup chatbot first
    bot_id = client.post("/api/v1/chatbots/", json={"name": "Owner Bot"}).json()["id"]

    # Create KB with content longer than chunk size (500)
    long_content = (
        "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints. "
        "The key features are: "
        "Very high performance, on par with NodeJS and Go (thanks to Starlette and Pydantic). One of the fastest Python frameworks available. "
        "Fast to code: Increase the speed to develop features by about 200% to 300%. "
        "Fewer bugs: Reduce about 40% of human (developer) induced errors. "
        "Intuitive: Great editor support. Completion everywhere. Less time debugging. "
        "Easy: Designed to be easy to use and learn. Less time reading documentation. "
        "Short: Minimize code duplication. Multiple features from each parameter declaration. Fewer bugs. "
        "Robust: Get production-ready code. With automatic interactive documentation. "
        "Standards-based: Based on (and fully compatible with) the open standards for APIs: OpenAPI and JSON Schema. "
        "It is built on top of Starlette and Pydantic, making it extremely robust and efficient. "
        "We are adding content chunks to the database to support building vector search and RAG in future development phases."
    )
    kb_payload = {
        "name": "Long Guide",
        "description": "Guides systems with extensive detail",
        "data_source": "text",
        "content": long_content,
        "chatbot_id": bot_id
    }
    response = client.post("/api/v1/knowledge-bases/", json=kb_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["chunks"] is not None
    assert len(data["chunks"]) >= 2
    # Verify chunks are in the db by getting the KB details
    get_resp = client.get(f"/api/v1/knowledge-bases/{data['id']}")
    assert get_resp.status_code == 200
    assert len(get_resp.json()["chunks"]) >= 2


def test_file_upload_txt(client):
    bot_id = client.post("/api/v1/chatbots/", json={"name": "File Bot"}).json()["id"]
    
    file_content = b"This is content uploaded from a text file. It is used to test Deneb AI text ingestion."
    files = {"file": ("test_doc.txt", file_content, "text/plain")}
    data = {
        "chatbot_id": bot_id,
        "name": "Uploaded TXT Doc",
        "description": "From txt file upload"
    }
    
    response = client.post("/api/v1/knowledge-bases/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["data_source"] == "file"
    assert "text file" in res_data["content"]
    assert len(res_data["chunks"]) == 1


def test_file_upload_pdf(client, monkeypatch):
    bot_id = client.post("/api/v1/chatbots/", json={"name": "PDF Bot"}).json()["id"]
    
    # Mock PdfReader behavior
    class MockPage:
        def extract_text(self):
            return "This is text extracted from a mocked PDF document."
            
    class MockPdfReader:
        def __init__(self, stream):
            self.pages = [MockPage()]
            
    monkeypatch.setattr("app.utils.extractor.PdfReader", MockPdfReader)
    
    files = {"file": ("test_doc.pdf", b"%PDF-1.4 mock bytes", "application/pdf")}
    data = {
        "chatbot_id": bot_id,
        "name": "Uploaded PDF Doc",
        "description": "From pdf file upload"
    }
    
    response = client.post("/api/v1/knowledge-bases/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["data_source"] == "file"
    assert "mocked PDF" in res_data["content"]
    assert len(res_data["chunks"]) == 1


def test_url_scraping_and_auto_scraping(client, monkeypatch):
    bot_id = client.post("/api/v1/chatbots/", json={"name": "Scraper Bot"}).json()["id"]
    
    # Mock extract_text_from_url
    monkeypatch.setattr("app.utils.extractor.extract_text_from_url", lambda url: f"Mocked text from URL: {url}")
    
    # Test auto-scrape on creation
    kb_payload = {
        "name": "Auto Scraped",
        "data_source": "url",
        "content": "https://example.com/roadmap",
        "chatbot_id": bot_id
    }
    response = client.post("/api/v1/knowledge-bases/", json=kb_payload)
    assert response.status_code == 201
    assert response.json()["content"] == "Mocked text from URL: https://example.com/roadmap"
    
    # Test dedicated scrape endpoint
    scrape_payload = {
        "url": "https://example.com/about",
        "chatbot_id": bot_id,
        "name": "Dedicated Scraping",
        "description": "Scraped from web page"
    }
    response = client.post("/api/v1/knowledge-bases/scrape", json=scrape_payload)
    assert response.status_code == 201
    assert response.json()["content"] == "Mocked text from URL: https://example.com/about"


def test_chat_simulation(client):
    # Setup
    bot_id = client.post("/api/v1/chatbots/", json={
        "name": "Deneb Assistant",
        "system_prompt": "You are the deneb AI Assistant."
    }).json()["id"]
    
    client.post("/api/v1/knowledge-bases/", json={
        "name": "FastAPI Milestones",
        "data_source": "text",
        "content": "FastAPI milestone 1 covers route setups, pagination, and database validation.",
        "chatbot_id": bot_id
    })
    
    # Simulate chat query
    # With matching token
    response = client.post(f"/api/v1/chatbots/{bot_id}/simulate?query=FastAPI%20milestone&top_k=1")
    assert response.status_code == 200
    data = response.json()
    assert data["chatbot_name"] == "Deneb Assistant"
    assert len(data["retrieved_context"]) == 1
    assert "FastAPI milestone 1" in data["retrieved_context"][0]["content"]
    assert "final_constructed_prompt" in data
    assert "simulated_response" in data
    
    # Simulate chat query with no match
    response = client.post(f"/api/v1/chatbots/{bot_id}/simulate?query=unrelated&top_k=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["retrieved_context"]) == 0
    assert "No relevant knowledge" in data["final_constructed_prompt"]


def test_chat_with_grok_fallback(client):
    # Setup chatbot first
    bot_id = client.post("/api/v1/chatbots/", json={
        "name": "Fallback Bot",
        "model": "grok-beta",
        "system_prompt": "Helpful chatbot."
    }).json()["id"]

    # Call /chat without Grok key (will fall back to mock response)
    payload = {
        "messages": [
            {"role": "user", "content": "What is the secret?"}
        ],
        "top_k": 2
    }
    response = client.post(f"/api/v1/chatbots/{bot_id}/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["chatbot_name"] == "Fallback Bot"
    assert data["is_mock"] is True
    assert "Simulated response" in data["response"]
    assert len(data["retrieved_context"]) == 0


def test_chat_with_grok_mocked(client, monkeypatch):
    bot_id = client.post("/api/v1/chatbots/", json={
        "name": "Grok Bot",
        "model": "grok-2",
        "system_prompt": "Grok helper."
    }).json()["id"]

    client.post("/api/v1/knowledge-bases/", json={
        "name": "Project Deneb Codebase",
        "data_source": "text",
        "content": "Phase 2 contains the chat control center interface and Grok API integration.",
        "chatbot_id": bot_id
    })

    # Mock the httpx post call to simulate Grok response
    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self.json_data = json_data
            self.status_code = status_code
            self.text = "Error detail string"

        def json(self):
            return self.json_data

    def mock_post(url, headers, json, timeout):
        # Verify headers
        assert headers["Authorization"] == "Bearer test-grok-key"
        # Verify system prompt has context injected
        system_msg = json["messages"][0]
        assert system_msg["role"] == "system"
        assert "Phase 2 contains the chat control center" in system_msg["content"]
        
        # Return mocked completion
        return MockResponse({
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Successfully matched context for Phase 2."
                    }
                }
            ]
        })

    monkeypatch.setattr("httpx.post", mock_post)

    payload = {
        "messages": [
            {"role": "user", "content": "What is in Phase 2?"}
        ],
        "top_k": 1
    }
    # Pass Grok key via custom header
    headers = {"X-Grok-API-Key": "test-grok-key"}
    response = client.post(f"/api/v1/chatbots/{bot_id}/chat", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_mock"] is False
    assert data["response"] == "Successfully matched context for Phase 2."
    assert len(data["retrieved_context"]) == 1
    assert data["retrieved_context"][0]["knowledge_base_name"] == "Project Deneb Codebase"

