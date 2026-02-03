
#this file merges both local and online llm clients
import os
from typing import Dict, Any, Optional

from .base_llm import BaseLLMClient


class LocalLLMClient(BaseLLMClient):
    """
    LLM client for local Ollama server.
    Phi-3 Mini model running locally via Ollama.
    """
    
    #default configuration
    DEFAULT_MODEL = "phi3:mini"
    DEFAULT_BASE_URL = "http://local_llm:11434"
    DEFAULT_TIMEOUT = 300  #longer timeout for local inference
    
    def __init__(
        self, 
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: Optional[int] = None
    ):
        """
        Initialize the Local LLM client (Ollama with Phi-3 Mini).
        
        Args:
            model: Model identifier (default: phi3:mini)
            base_url: Ollama server URL (default: http://local_llm:11434)
            max_retries: Maximum number of retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 300 for local inference)
        """
        super().__init__(
            model=model or os.getenv("LOCAL_LLM_MODEL", self.DEFAULT_MODEL),
            base_url=base_url or os.getenv("LOCAL_LLM_URL", self.DEFAULT_BASE_URL),
            max_retries=max_retries,
            timeout=timeout or self.DEFAULT_TIMEOUT
        )
    
    def _format_and_send(self, prompt: str, bundle: Dict[str, Any]) -> str:
        """
        Format Ollama-specific payload and send request.
        
        Args:
            prompt: The complete prompt text
            bundle: Topic vector bundle data
            
        Returns:
            Generated summary as a plain string
        """
        url = f"{self.base_url}/api/generate"
        
        #build the complete user content
        user_content = self._build_user_content(prompt, bundle)
        
        #construct ollama-specific payload
        payload = {
            "model": self.model,
            "prompt": user_content,
            "stream": False  #get complete response at once
        }
        
        try:
            response = self._execute_request(url, payload)
            # Parse Ollama response format
            return response.get("response", "").strip()
        except Exception as e:
            #add context for connection errors specific to local LLM
            if "Connection" in str(e):
                print("Make sure the local_llm container is running: docker-compose up local_llm")
            raise


class OnlineLLMClient(BaseLLMClient):
    """
    LLM client for OpenRouter API.
    
    Uses GPT-4o-mini model via OpenRouter.
    Requires API key via constructor or OPENROUTER_API_KEY environment variable.
    """
    
    #default configuration
    DEFAULT_MODEL = "openai/gpt-4o-mini"
    DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
    DEFAULT_TIMEOUT = 30
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: Optional[int] = None
    ):
        """
        Initialize the Online LLM API client.
        
        Args:
            api_key: OpenRouter API key (reads from OPENROUTER_API_KEY env if not given)
            model: Model identifier (default: openai/gpt-4o-mini)
            base_url: API base URL (default: https://openrouter.ai/api/v1)
            max_retries: Maximum number of retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 30)
            
        Raises:
            ValueError: If API key is not provided and not found in environment
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. "
                "Please set OPENROUTER_API_KEY environment variable "
                "or pass api_key to the constructor."
            )
        
        super().__init__(
            model=model or os.getenv("OPENROUTER_MODEL", self.DEFAULT_MODEL),
            base_url=base_url or os.getenv("OPENROUTER_URL", self.DEFAULT_BASE_URL),
            max_retries=max_retries,
            timeout=timeout or self.DEFAULT_TIMEOUT
        )
    
    def _format_and_send(self, prompt: str, bundle: Dict[str, Any]) -> str:
        """
        Format OpenRouter-specific payload and send request.
        
        Args:
            prompt: The complete prompt text
            bundle: Topic vector bundle data
            
        Returns:
            Generated summary as a plain string
        """
        url = f"{self.base_url}/chat/completions"
        
        #build the complete user content
        user_content = self._build_user_content(prompt, bundle)
        
        #set up headers with API key
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        #construct OpenRouter/OpenAI-specific payload
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": user_content
                }
            ]
        }
        
        response = self._execute_request(url, payload, headers=headers)
        
        #validate and parse OpenRouter response format
        try:
            content = response["choices"][0]["message"]["content"]
            return content.strip()
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Unexpected API response structure: {response}") from e
