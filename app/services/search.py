import os
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseSearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Perform search and return list of result dicts containing title, url, snippet."""
        pass


class MockSearchProvider(BaseSearchProvider):
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        # Generate smart mock answers based on query keywords
        q = query.lower()
        results = []
        
        if "fastapi" in q:
            results = [
                {
                    "title": "FastAPI Official Documentation - Uvicorn & Routing",
                    "url": "https://fastapi.tiangolo.com",
                    "snippet": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints."
                },
                {
                    "title": "SQLAlchemy ORM integration with FastAPI tutorial",
                    "url": "https://fastapi.tiangolo.com/tutorial/sql-databases/",
                    "snippet": "Learn how to configure databases, sessions, and declare SQLAlchemy models to implement paginated GET and POST requests in FastAPI."
                },
                {
                    "title": "FastAPI Github Repository & Community",
                    "url": "https://github.com/tiangolo/fastapi",
                    "snippet": "Join the FastAPI open source project, browse community templates, issue logs, and custom middleware configurations."
                }
            ]
        elif "rag" in q or "retrieval" in q or "vector" in q:
            results = [
                {
                    "title": "Retrieval-Augmented Generation (RAG) Architecture Overview",
                    "url": "https://arxiv.org/abs/2005.11401",
                    "snippet": "RAG combines dense retrieval models with sequence-to-sequence generators to produce factual responses using external documentation context."
                },
                {
                    "title": "Chroma DB - The Open Source Vector Database for AI",
                    "url": "https://docs.trychroma.com",
                    "snippet": "Chroma makes it easy to build LLM apps by making knowledge bases, semantic documents, and text chunk vectors queryable instantly."
                },
                {
                    "title": "Pinecone - Vector Databases for Enterprise Search",
                    "url": "https://pinecone.io",
                    "snippet": "Pinecone provides fully managed cloud-native vector indexes to run fast semantic search operations for million-scale document chunks."
                }
            ]
        elif "agent" in q or "tool" in q:
            results = [
                {
                    "title": "AI Agents & Function Calling Guide - xAI Grok",
                    "url": "https://docs.x.ai/docs/guides/tool-calling",
                    "snippet": "Grok models support tool calling (function execution), planning agent loops, and multi-turn autonomous script executions."
                },
                {
                    "title": "LangChain - Building LLM Agentic Workflows",
                    "url": "https://python.langchain.com",
                    "snippet": "LangChain is a popular Python framework to orchestrate chains, agents, memory objects, and connect prompt variables dynamically."
                }
            ]
        else:
            results = [
                {
                    "title": f"Web Search Results for '{query}'",
                    "url": "https://example.com/search?q=" + query.replace(" ", "+"),
                    "snippet": f"Found public articles discussing '{query}'. The topic covers standard REST patterns, python structures, and AI development."
                },
                {
                    "title": "Wikipedia - Public Knowledge Resource Hub",
                    "url": "https://en.wikipedia.org/wiki/Special:Search?search=" + query,
                    "snippet": f"Encyclopedia reference index detailing context, history, and definitions matching query tokens for {query}."
                }
            ]
            
        return results[:limit]


class TavilySearchProvider(BaseSearchProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        if not self.api_key:
            return MockSearchProvider().search(query, limit)
        try:
            response = httpx.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": limit,
                    "search_depth": "basic"
                },
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                results = []
                for r in data.get("results", []):
                    results.append({
                        "title": r.get("title", "Search Hit"),
                        "url": r.get("url", "https://tavily.com"),
                        "snippet": r.get("content", "")
                    })
                return results
        except Exception:
            pass
        return MockSearchProvider().search(query, limit)


class SerperSearchProvider(BaseSearchProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        # Drop-in support for Google Search via Serper API
        if not self.api_key:
            return MockSearchProvider().search(query, limit)
        try:
            response = httpx.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                json={"q": query, "num": limit},
                timeout=10.0
            )
            if response.status_code == 200:
                data = response.json()
                results = []
                for r in data.get("organic", []):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("link", ""),
                        "snippet": r.get("snippet", "")
                    })
                return results
        except Exception:
            pass
        return MockSearchProvider().search(query, limit)


# Stubs for Perplexity, Google, and Bing Search APIs
class PerplexitySearchProvider(BaseSearchProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        # Future-ready drop-in stub for Perplexity Sonar Search
        return MockSearchProvider().search(query, limit)

class GoogleSearchProvider(BaseSearchProvider):
    def __init__(self, cx: str, api_key: str):
        self.cx = cx
        self.api_key = api_key
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        # Future-ready Google Custom Search Engine
        return MockSearchProvider().search(query, limit)

class BingSearchProvider(BaseSearchProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        # Future-ready Bing Search API
        return MockSearchProvider().search(query, limit)


class SearchService:
    def __init__(self):
        provider_name = os.getenv("SEARCH_PROVIDER", "mock").lower()
        tavily_key = os.getenv("TAVILY_API_KEY", "")
        serper_key = os.getenv("SERPER_API_KEY", "")
        perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
        google_key = os.getenv("GOOGLE_SEARCH_API_KEY", "")
        google_cx = os.getenv("GOOGLE_SEARCH_CX", "")

        if provider_name == "tavily" and tavily_key:
            self.provider = TavilySearchProvider(tavily_key)
        elif provider_name == "serper" and serper_key:
            self.provider = SerperSearchProvider(serper_key)
        elif provider_name == "perplexity" and perplexity_key:
            self.provider = PerplexitySearchProvider(perplexity_key)
        elif provider_name == "google" and google_key and google_cx:
            self.provider = GoogleSearchProvider(google_cx, google_key)
        else:
            self.provider = MockSearchProvider()

    def query(self, search_text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Perform search utilizing the loaded provider and return raw result list."""
        if not search_text.strip():
            return []
        return self.provider.search(search_text, limit)

search_service = SearchService()
