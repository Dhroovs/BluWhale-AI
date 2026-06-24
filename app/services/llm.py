import httpx
from typing import List, Dict, Any, Optional
from app.config import settings

class LLMService:
    @staticmethod
    def call_grok(
        messages: List[Dict[str, str]],
        model: str = "grok-beta",
        temperature: float = 0.7,
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call xAI Grok API completions endpoint.
        Falls back to a structured simulation if api_key is missing or fails.
        """
        # Resolve API Key: prioritizes client override header, then server settings
        active_key = api_key if api_key else settings.GROK_API_KEY
        
        # Ensure we use an active grok model name
        target_model = model if (model and model.startswith("grok")) else "grok-beta"
        
        if not active_key:
            return {
                "text": "",
                "is_mock": True,
                "warning": "Grok API access key is missing. Set xAI token in Settings."
            }

        try:
            headers = {
                "Authorization": f"Bearer {active_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "messages": messages,
                "model": target_model,
                "temperature": temperature,
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
                content = completion_data["choices"][0]["message"]["content"]
                return {
                    "text": content,
                    "is_mock": False,
                    "warning": None
                }
            else:
                return {
                    "text": "",
                    "is_mock": True,
                    "warning": f"Grok API returned error code {response.status_code}: {response.text}"
                }
        except Exception as e:
            return {
                "text": "",
                "is_mock": True,
                "warning": f"Failed to connect to Grok API: {str(e)}"
            }

llm_service = LLMService()
