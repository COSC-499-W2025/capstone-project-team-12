from typing import Dict, Any
import json
import time
import requests

class LocalLLMClient:
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize the Local LLM client (Ollama with Phi-3 Mini)
        
        Args:
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.base_url = "http://local_llm:11434"
        self.model = "phi3:mini"
        self.max_retries = max_retries
    
    def send_request(
        self, 
        prompt: str, 
        topic_vector_bundle: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send prompt + keywords bundle to local Ollama API and return response with automatic retry
        
        Args:
            prompt: The instruction/question to send
            data_bundle: JSON string from stats_cache.collect_stats()
            
        Returns:
            Normalized API response as dictionary (matches online format)
        """
        url = f"{self.base_url}/api/generate"
        
        #construct user message
        user_content = prompt
        if topic_vector_bundle:
            # bundle is now topic keywords + doc top topics (plain strings/floats)
            try:
                vector_data = json.dumps(topic_vector_bundle, indent=2)
            except TypeError:
                # as a safeguard, coerce any non-serializable values to str
                def sanitize(obj):
                    if isinstance(obj, dict):
                        return {k: sanitize(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [sanitize(x) for x in obj]
                    else:
                        return obj if isinstance(obj, (str, int, float, bool)) else str(obj)
                vector_data = json.dumps(sanitize(topic_vector_bundle), indent=2)
            user_content = f"{prompt}\n\n--- Topic Keywords ---\n{vector_data}"

        payload = {
            "model": self.model,
            "prompt": user_content,
            "stream": False  # Get complete response at once
        }
        
        #retry loop with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, json=payload, timeout=300)  # Longer timeout for local inference
                response.raise_for_status()
                
                #convert Ollama format to OpenRouter-like format for consistency
                ollama_response = response.json()
                
                #normalize to match online API format
                return {
                    "choices": [
                        {
                            "message": {
                                "content": ollama_response.get("response", "")
                            }
                        }
                    ]
                }
                
            except requests.Timeout as e:
                last_exception = e
                print(f"Local LLM request timed out (attempt {attempt + 1}/{self.max_retries})")
                
            except requests.ConnectionError as e:
                last_exception = e
                print(f"Cannot connect to local LLM (attempt {attempt + 1}/{self.max_retries}): {e}")
                print("Make sure the local_llm container is running: docker-compose up local_llm")
                
            except requests.HTTPError as e:
                last_exception = e
                print(f"Local LLM HTTP error {e.response.status_code if e.response else 'unknown'} (attempt {attempt + 1}/{self.max_retries})")
                
            except requests.RequestException as e:
                last_exception = e
                print(f"Local LLM request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
            
            #if not last attempt, wait with exponential backoff
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retrying after {wait_time}s...")
                time.sleep(wait_time)
        
        if last_exception:
            raise Exception(f"Local LLM failed after {self.max_retries} attempts: {str(last_exception)}")
        else:
            raise requests.RequestException("All retry attempts failed with unknown error")
    
    def generate_short_summary(self, topic_vector_bundle: Dict[str, Any]) -> str:
        """
        Generate a short summary using local Ollama (optimized for Phi-3 Mini)
        
        Args: data_bundle: JSON string from stats_cache.collect_stats()
            
        Returns: Short summary string
        """
        prompt = (
            "Create a concise professional summary using the topic keywords and doc top topics. "
            "Use 2-3 bullet points."
        )
        
        response = self.send_request(prompt=prompt, topic_vector_bundle=topic_vector_bundle)
        return response["choices"][0]["message"]["content"].strip()
    
    def generate_summary(self, topic_vector_bundle: Dict[str, Any]) -> str:
        """
        Generate a standard summary using local Ollama (optimized for Phi-3 Mini)
        
        Args:
            data_bundle: JSON string from stats_cache.collect_stats()
        
        Returns:
            Standard summary string
        """
        prompt = (
            "Generate a professional summary from the topic keywords and document top topics. "
            "Use 4-5 bullet points highlighting strengths."
        )
        
        response = self.send_request(prompt=prompt, topic_vector_bundle=topic_vector_bundle)
        return response["choices"][0]["message"]["content"].strip()
    
    def generate_long_summary(self, topic_vector_bundle: Dict[str, Any]) -> str:
        """
        Generate a detailed summary using local Ollama (optimized for Phi-3 Mini)
        
        Args:
            data_bundle: JSON string from stats_cache.collect_stats()
        
        Returns:
            Long summary string
        """
        prompt = (
            "Generate a detailed professional summary from the topic keywords and doc top topics. "
            "Use 5-7 bullet points and include notable themes."
        )
        
        response = self.send_request(prompt=prompt, topic_vector_bundle=topic_vector_bundle)
        return response["choices"][0]["message"]["content"].strip()