import requests
import pytest

from llm.llm_clients import LocalLLMClient

class MockResponse:
    """Mock of requests.Response for Ollama API"""

    def __init__(self, payload, status_code=200, raise_on_status=False):
        self._payload = payload
        self.status_code = status_code
        self._raise = raise_on_status

    def raise_for_status(self):
        if self._raise or self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_local_client_initialization():
    """LocalLLMClient should initialize without API key"""
    client = LocalLLMClient()
    assert client.base_url == "http://local_llm:11434"
    assert client.model == "phi3:mini"
    assert client.max_retries == 3


def test_generate_summary_uses_ollama_format(monkeypatch):
    """generate_summary should use Ollama's /api/generate endpoint with correct format"""
    client = LocalLLMClient()
    captured = {}

    def fake_post(url, json=None, timeout=None, headers=None):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return MockResponse({"response": "Local LLM response"})

    monkeypatch.setattr(requests, "post", fake_post)

    topic_vector_bundle = {
        "doc_topic_vectors": [[0.5, 0.5]],
        "topic_term_vectors": [[0.3, 0.7]]
    }
    
    result = client.generate_summary(topic_vector_bundle, summary_type="standard")

    assert captured["url"].endswith("/api/generate")
    assert captured["timeout"] == 300  #we want longer timout for local
    assert captured["json"]["model"] == "phi3:mini"
    assert captured["json"]["stream"] == False
    assert "prompt" in captured["json"]
    assert result == "Local LLM response"


def test_generate_short_summary_returns_response(monkeypatch):
    """generate_short_summary should work with local LLM"""
    client = LocalLLMClient()

    def fake_post(url, json=None, timeout=None, headers=None):
        return MockResponse({"response": "• Local bullet 1\n• Local bullet 2"})

    monkeypatch.setattr(requests, "post", fake_post)

    topic_vector_bundle = {
        "doc_topic_vectors": [[0.5, 0.5]],
        "topic_term_vectors": [[0.3, 0.7]]
    }
    
    out = client.generate_short_summary(topic_vector_bundle)
    assert "Local bullet" in out


def test_generate_summary_throws_on_connection_error(monkeypatch):
    """generate_summary should raise exception when local LLM is unreachable"""
    client = LocalLLMClient(max_retries=1)  #we reduce the amount of retries for speed

    def fake_post_error(url, json=None, timeout=None, headers=None):
        raise requests.ConnectionError("Cannot connect to local_llm")

    monkeypatch.setattr(requests, "post", fake_post_error)

    with pytest.raises(Exception) as exc_info:
        client.generate_summary({}, summary_type="standard")
    
    assert "failed after" in str(exc_info.value).lower()