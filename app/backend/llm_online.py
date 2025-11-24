import os
import time
import requests
from typing import Dict, Any, Optional

#we can either pass the key into the constructor or set it as environment var OPENROUTER_API_KEY
#to add it as env var:
#powershell: $env:OPENROUTER_API_KEY = "sk-or-your-key"
#cmd: set OPENROUTER_API_KEY=sk-or-your-key
class OnlineLLMClient:
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        """
        Initialize the Online LLM API client
        
        Args:
            api_key: OpenRouter API key (reads from env if not given)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. "
                "Please set OPENROUTER_API_KEY environment variable."
            )
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "openai/gpt-4o-mini"
        self.max_retries = max_retries
    
    def send_request(
        self, 
        prompt: str, 
        data_bundle: str
    ) -> Dict[str, Any]:
        """
        Send prompt + data bundle to LLM API and return response with automatic retry
        
        Args:
            prompt: The instruction/question to send
            data_bundle: JSON string from stats_cache.collect_stats()
            
        Returns:
            Raw API response as dictionary
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        #construct user message
        user_content = prompt
        if data_bundle:
            user_content = f"{prompt}\n\n--- Project Data ---\n{data_bundle}"
        
        #build request payload
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": user_content
                }
            ]
        }
        
        #retry loop with exponential backoff
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                
                #validate response structure
                resp_json = response.json()
                try:
                    content = resp_json["choices"][0]["message"]["content"]
                except (KeyError, IndexError, TypeError) as e:
                    raise ValueError(f"Unexpected API response structure: {resp_json}") from e
                
                return resp_json
                
            except requests.Timeout as e:
                last_exception = e
                print(f"Request timed out (attempt {attempt + 1}/{self.max_retries})")
                
            except requests.ConnectionError as e:
                last_exception = e
                print(f"Connection error (attempt {attempt + 1}/{self.max_retries}): {e}")
                
            except requests.HTTPError as e:
                #don't retry on 4xx client errors (except 429 rate limit)
                if e.response is not None and 400 <= e.response.status_code < 500 and e.response.status_code != 429:
                    #client error, wait for raising
                    raise
                last_exception = e
                print(f"HTTP error {e.response.status_code if e.response else 'unknown'} (attempt {attempt + 1}/{self.max_retries})")
                
            except requests.RequestException as e:
                last_exception = e
                print(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
            
            #if not last attempt, wait with exponential backoff
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt 
                print(f"Retrying after {wait_time}s...")
                time.sleep(wait_time)
        

        if last_exception:
            raise last_exception
        else:
            #would probably never reach here, but just in case
            raise requests.RequestException("All retry attempts failed with unknown error")
    
    def generate_short_summary(self, data_bundle: str) -> str:
        """
        Generate a short resume ready summary
        
        Args: data_bundle: JSON string from stats_cache.collect_stats()
            
        Returns: Short summary string with 2-3 bullet points
        """
        prompt = """Using the data provided, generate a concise LinkedIn-style summary as a bullet-point list (2-3 points).
• Start with one line summarizing the work's goal and overall outcome (if multiple projects are present, provide a high-level overview).
• Highlight the most significant achievement(s): what was done, which technologies/tools were used, and what measurable results or improvements were achieved.
• Optionally include key skills developed or strengthened through this work.

Use action-oriented, professional language that is easy to scan. No extra text, greetings, or emojis."""
#         prompt = """Using the topic vectors provided, generate a concise LinkedIn-style summary of the project as a bullet-point list (2-3 points).
# • Start with one line summarizing the project's goal and overall outcome.
# • Then capture your most significant achievement: what you did, which technologies/tools you used, and what measurable result or improvement you drove.
# • Optionally include a line about the key skill you developed or strengthened.

# Use action-oriented, professional language that is easy to scan. No extra text, greetings, or emojis."""
        
        response = self.send_request(prompt=prompt, data_bundle=data_bundle)
        return response["choices"][0]["message"]["content"].strip()
    
    def generate_summary(self, data_bundle: str) -> str:
        """
        Generate a standard resume ready professional summary
        
        Args:
            data_bundle: JSON string from stats_cache.collect_stats()
        
        Returns:
            Standard summary string with 4-5 bullet points
        """
        prompt = """Using the data provided, generate a LinkedIn-ready professional summary as a bullet-point list (4-5 points).
• First bullet: provide a clear, concise overview of the work's purpose and scope (if multiple projects are present, summarize the breadth of work).
• Subsequent bullets: highlight specific contributions (what was done), skills applied, and technologies/tools used — frame each as an accomplishment (not just a responsibility) and, where possible, quantify outcomes.
• Final bullet: describe the key professional and technical skills gained through this work, emphasizing development and growth.

Use strong action verbs (e.g., "developed", "optimized", "designed"), maintain an active and confident tone, and tailor the language for LinkedIn. Avoid redundancy; keep each bullet impactful and easy to scan. Do not include greetings, emojis, extraneous text, or anything outside the bullet list."""

#         prompt = """Using the topic vectors provided, generate a LinkedIn-ready professional summary of the project as a bullet-point list (4-5 points).
# • First bullet: provide a clear, concise overview of the project's purpose and scope.
# • Subsequent bullets: highlight your specific contributions (what you did), the skills you applied, and the technologies/tools you used — frame each as an accomplishment (not just a responsibility) and, where possible, quantify the outcome.
# • Final bullet: describe the key professional and technical skills you gained through the project, emphasizing how you developed them.

# Use strong action verbs (e.g., "spearheaded", "developed", "optimized"), maintain an active and confident tone, and tailor the language for LinkedIn. Avoid redundancy; keep each bullet impactful and easy to scan. Do not include greetings, emojis, extraneous text, or anything outside the bullet list."""
        
        response = self.send_request(prompt=prompt, data_bundle=data_bundle)
        return response["choices"][0]["message"]["content"].strip()
    
    def generate_long_summary(self, data_bundle: str) -> str:
        """
        Generate a comprehensive resume ready summary
        
        Args:
            data_bundle: JSON string from stats_cache.collect_stats()
        
        Returns:
            Long summary string with 5-7 bullet points
        """

        prompt = """Using the data provided, generate a comprehensive LinkedIn-ready professional summary as a bullet-point list (5-7 points).
• First bullet: succinct overview of the work's objectives, context, and impact (if multiple projects are present, provide a cohesive narrative).
• Middle bullets (3-4): detailed accomplishments — each bullet should state what was done using strong action verbs, the tools/technologies/methodologies applied, and the outcomes or benefits achieved (ideally quantified).
• Next bullet: highlight collaboration, leadership, cross-functional aspects, or how meaningful challenges were overcome.
• Final bullet: describe the advanced skills gained or deepened through this work (both technical and professional).

Maintain an active, confident, growth-oriented tone, tailor for LinkedIn, avoid redundancy, keep bullets crisp and skimmable. Do not include introductory or closing text, salutations, or emojis."""
#         prompt = """Using the topic vectors provided, generate a comprehensive LinkedIn-ready professional summary of the project as a bullet-point list (5-7 points).
# • First bullet: succinct overview of the project's objectives, context and impact.
# • Middle bullets (3-4): detailed accomplishments — each bullet should state what you did using strong action verbs, the tools/technologies/methodologies you applied, and the outcome or benefit you achieved (ideally quantified).
# • Next bullet: highlight any collaboration or leadership you provided, cross-functional aspects, or how you overcame a meaningful challenge.
# • Final bullet: describe the advanced skills you gained or deepened through the project (both technical and professional).

# Maintain an active, confident, growth-oriented tone, tailor for LinkedIn, avoid redundancy, keep bullets crisp and skimmable. Do not include introductory or closing text, salutations, or emojis."""
        
        response = self.send_request(prompt=prompt, data_bundle=data_bundle)
        return response["choices"][0]["message"]["content"].strip()