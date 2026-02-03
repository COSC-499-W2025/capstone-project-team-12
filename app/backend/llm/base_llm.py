
#merged both llm_online.py and the local one into one to remove the duplicate code
#this will be our central class for the llm stuff

import json
import time
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from .prompts import get_prompt, format_skill_highlight


class BaseLLMClient(ABC):
    """
    Abstract Base Class for LLM clients.
    
    Handles shared logic such as data sanitization, retry logic,
    and prompt construction. Subclasses must implement _format_and_send
    for API-specific payload formatting.
    """
    
    def __init__(
        self, 
        model: str, 
        base_url: str, 
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize the LLM client.
        
        Args:
            model: The model identifier to use
            base_url: Base URL for the API endpoint
            max_retries: Maximum number of retry attempts (default: 3)
            timeout: Request timeout in seconds (default: 30)
        """
        self.model = model
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
    
    def _sanitize_bundle(self, bundle: Dict[str, Any]) -> str:
        """
        Sanitize and serialize the topic vector bundle to JSON.
        
        Recursively converts non-serializable objects (e.g., numpy types)
        to their string representations to prevent JSON serialization crashes.
        
        Args:
            bundle: Dictionary containing topic data
            
        Returns:
            JSON-formatted string of the sanitized bundle
        """
        def sanitize(obj: Any) -> Any:
            """Recursively sanitize objects for JSON serialization."""
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize(x) for x in obj]
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            else:
                #convert non-serializable types (numpy, etc.) to string
                return str(obj)
        
        try:
            return json.dumps(bundle, indent=2)
        except TypeError:
            #fallback: sanitize and try again
            sanitized_bundle = sanitize(bundle)
            return json.dumps(sanitized_bundle, indent=2)
    
    def _execute_request(
        self, 
        url: str, 
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Execute HTTP POST request with retry logic and exponential backoff.
        
        Args:
            url: Full URL for the API endpoint
            payload: JSON payload to send
            headers: Optional HTTP headers
            
        Returns:
            Parsed JSON response from the API
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_exception: Optional[Exception] = None
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=payload, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.Timeout as e:
                last_exception = e
                print(f"Request timed out (attempt {attempt + 1}/{self.max_retries})")
                
            except requests.ConnectionError as e:
                last_exception = e
                print(f"Connection error (attempt {attempt + 1}/{self.max_retries}): {e}")
                
            except requests.HTTPError as e:
                #don't retry on 4xx client errors (except 429 rate limit)
                if (e.response is not None and 
                    400 <= e.response.status_code < 500 and 
                    e.response.status_code != 429):
                    raise
                last_exception = e
                status_code = e.response.status_code if e.response else 'unknown'
                print(f"HTTP error {status_code} (attempt {attempt + 1}/{self.max_retries})")
                
            except requests.RequestException as e:
                last_exception = e
                print(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
            
            #if not last attempt, wait with exponential backoff
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retrying after {wait_time}s...")
                time.sleep(wait_time)
        
        #all attempts failed
        if last_exception:
            raise Exception(
                f"LLM request failed after {self.max_retries} attempts: {str(last_exception)}"
            )
        else:
            raise requests.RequestException("All retry attempts failed with unknown error")
    
    def _build_user_content(self, prompt: str, bundle: Dict[str, Any]) -> str:
        """
        Build the complete user content string with prompt and topic data.
        
        Args:
            prompt: The instruction/prompt text
            bundle: Topic vector bundle data
            
        Returns:
            Complete user content string
        """
        if not bundle:
            return prompt
        
        vector_data = self._sanitize_bundle(bundle)
        return f"{prompt}\n\n--- Topic Keywords ---\n{vector_data}"
    
    def generate_summary(
        self, 
        topic_vector_bundle: Dict[str, Any], 
        summary_type: str = "standard"
    ) -> str:
        """
        Generate a project summary using the LLM.

        Fetches the correct prompt template based on summary_type, Appends skill highlighting instruction if user_highlights present, 
        Delegates to _format_and_send for API-specific handling
        
        Args:
            topic_vector_bundle: Dictionary containing topic keywords and data
            summary_type: One of "short", "standard", or "long" (default: "standard")
            
        Returns:
            Generated summary as a plain string
        """
        #get the base prompt for the requested summary type
        prompt = get_prompt(summary_type)
        
        #check for user-selected skill highlights
        highlights = topic_vector_bundle.get('user_highlights', [])
        if highlights:
            prompt += format_skill_highlight(highlights)
        
        #delegate to subclass for API-specific formatting and sending
        return self._format_and_send(prompt, topic_vector_bundle)
    
    #convenience methods for backward compatibility
    def generate_short_summary(self, topic_vector_bundle: Dict[str, Any]) -> str:
        """Generate a short (2-3 bullet) summary."""
        return self.generate_summary(topic_vector_bundle, summary_type="short")
    
    def generate_long_summary(self, topic_vector_bundle: Dict[str, Any]) -> str:
        """Generate a long (5-7 bullet) summary."""
        return self.generate_summary(topic_vector_bundle, summary_type="long")
    
    @abstractmethod
    def _format_and_send(self, prompt: str, bundle: Dict[str, Any]) -> str:
        """
        Format the API-specific payload and send the request.
        
        Subclasses must implement this method to:
        1. Construct the API-specific JSON payload
        2. Call self._execute_request with the payload
        3. Parse the API-specific response format
        4. Return the clean summary string
        
        Args:
            prompt: The complete prompt with any skill highlighting
            bundle: Topic vector bundle data
            
        Returns:
            Generated summary as a plain string
        """
        pass
