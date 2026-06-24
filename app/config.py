import os

class Settings:
    PROJECT_NAME: str = "Deneb AI Chatbot Platform"
    PROJECT_VERSION: str = "1.0.0"
    
    # SQLite Database connection URL.
    # sqlite:///deneb.db will create the file in the project's root folder.
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///deneb.db")
    
    # API key for endpoint security
    API_KEY: str = os.getenv("API_KEY", "deneb-secret-key")

    # API key for xAI Grok completions
    GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")

settings = Settings()
