"""
Ollama Integration Service
Handles communication with local Ollama API for LLM-based predictions
"""
import os
import json
import logging
import requests
from typing import Dict, Optional, List, Any
from datetime import datetime, date

logger = logging.getLogger(__name__)


class OllamaService:
    """
    Service class to interact with Ollama API
    Ollama is a local LLM runtime (similar to running ChatGPT locally)
    """
    
    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout: int = 120
    ):
        """
        Initialize Ollama service
        
        Args:
            base_url: Ollama API endpoint (default: http://localhost:11434)
            model: Model name (default: llama3.1)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1")
        self.timeout = timeout
        logger.info(f"🤖 Ollama Service initialized: {self.base_url} | Model: {self.model}")
    
    def check_health(self) -> bool:
        """
        Check if Ollama server is running and accessible
        
        Returns:
            bool: True if Ollama is running, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                logger.info(f"✅ Ollama is running. Available models: {[m['name'] for m in models]}")
                return True
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ollama connection failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        List all available Ollama models
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response using Ollama
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Creativity (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum response length
            stream: Whether to stream response
        
        Returns:
            Dict with 'response', 'model', 'created_at', 'done'
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            logger.debug(f"📤 Sending request to Ollama: {len(prompt)} chars")
            start_time = datetime.now()
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Ollama response received ({elapsed_ms:.0f}ms)")
                result["execution_time_ms"] = int(elapsed_ms)
                return result
            else:
                logger.error(f"❌ Ollama API error: {response.status_code} - {response.text}")
                return {
                    "error": f"HTTP {response.status_code}",
                    "message": response.text,
                    "execution_time_ms": int(elapsed_ms)
                }
        
        except requests.exceptions.Timeout:
            logger.error("❌ Ollama request timeout")
            return {"error": "timeout", "message": "Request timed out"}
        except Exception as e:
            logger.error(f"❌ Ollama generation failed: {e}")
            return {"error": "exception", "message": str(e)}
    
    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        expected_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate a structured response (attempts to parse JSON)
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            expected_format: Expected format (currently only 'json')
        
        Returns:
            Parsed JSON dict or error dict
        """
        # Add format instruction to prompt
        if expected_format == "json":
            format_instruction = (
                "\n\nIMPORTANT: Respond ONLY with valid JSON. "
                "Do not include any explanation before or after the JSON."
            )
            prompt = prompt + format_instruction
        
        result = self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3  # Lower temperature for more consistent formatting
        )
        
        if "error" in result:
            return result
        
        # Try to parse JSON from response
        response_text = result.get("response", "")
        
        try:
            # Extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            parsed = json.loads(response_text)
            result["parsed"] = parsed
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}")
            result["error"] = "json_parse_error"
            result["message"] = str(e)
            result["raw_response"] = response_text
            return result


# Singleton instance
_ollama_service = None

def get_ollama_service() -> OllamaService:
    """
    Get or create Ollama service instance (singleton pattern)
    """
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
    return _ollama_service
