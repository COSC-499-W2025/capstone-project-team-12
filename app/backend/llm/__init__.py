"""
LLM Client Module

This module provides LLM client implementations for generating project summaries.
It includes both local (Ollama) and online (OpenRouter) clients with a shared
abstract base class for common functionality.
"""

from .llm_clients import LocalLLMClient, OnlineLLMClient
from .base_llm import BaseLLMClient
from .prompts import PROMPTS, SKILL_HIGHLIGHT_TEMPLATE

__all__ = [
    "LocalLLMClient",
    "OnlineLLMClient",
    "BaseLLMClient",
    "PROMPTS",
    "SKILL_HIGHLIGHT_TEMPLATE",
]
