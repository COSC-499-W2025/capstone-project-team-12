import os
import requests
import pytest

from llm_online import OnlineLLMClient

#mock replacement for requests
class MockResponse:
    """Mock of requests.Response with raise_for_status() and json()."""

    def __init__(self, payload, status_code=200, raise_on_status=False):
        self._payload = payload
        self.status_code = status_code
        self._raise = raise_on_status

    def raise_for_status(self):
        """Simulate requests.HTTPError on bad status responses."""
        if self._raise or self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        """Return the configured JSON payload."""
        return self._payload  #return mocked payload


def test_reads_api_key_from_env_var(monkeypatch):
    """Client reads OPENROUTER_API_KEY from the environment when no arg given."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-test-key")
    client = OnlineLLMClient()
    assert client.api_key == "env-test-key"


def test_constructor_uses_api_key_argument(monkeypatch):
    """Explicit api_key argument should override the environment variable."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
    client = OnlineLLMClient(api_key="param-key")
    assert client.api_key == "param-key"
    assert client.api_key != "env-key"


def test_raises_error_when_no_api_key(monkeypatch):
    """Constructor raises ValueError if no API key is available."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ValueError):
        OnlineLLMClient()


def test_send_request_builds_and_posts_payload(monkeypatch):
    """send_request should construct the correct URL, headers, timeout and JSON body."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    client = OnlineLLMClient()
    captured = {}

    #capture post
    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return MockResponse({"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(requests, "post", fake_post)

    topic_vector_bundle = {
        "doc_topic_vectors": [[0.5, 0.5]],
        "topic_term_vectors": [[0.3, 0.7]]
    }
    resp = client.send_request(prompt="Hello", topic_vector_bundle=topic_vector_bundle)

    #check headers and payload
    assert captured["url"].endswith("/chat/completions")
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["timeout"] == 30
    assert isinstance(captured["json"], dict)
    assert captured["json"]["model"] == client.model
    assert "messages" in captured["json"]
    assert resp["choices"][0]["message"]["content"] == "ok"


def test_data_bundle_is_appended_to_message(monkeypatch):
    """The topic_vector_bundle should be present in the message content sent to the API."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    client = OnlineLLMClient()

    def fake_post(url, headers=None, json=None, timeout=None):
        content = json["messages"][0]["content"]
        assert "doc_topic_vectors" in content
        return MockResponse({"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(requests, "post", fake_post)

    topic_vector_bundle = {
        "doc_topic_vectors": [[0.5, 0.5]],
        "topic_term_vectors": [[0.3, 0.7]]
    }
    client.send_request(prompt="Summarize", topic_vector_bundle=topic_vector_bundle)


def test_generate_short_summary_returns_response(monkeypatch):
    """generate_short_summary should use send_request and return the LLM text."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    client = OnlineLLMClient()

    def fake_send(self, prompt, topic_vector_bundle):
        return {"choices": [{"message": {"content": "• Short bullet 1\n• Short bullet 2"}}]}

    monkeypatch.setattr(OnlineLLMClient, "send_request", fake_send)

    topic_vector_bundle = {
        "doc_topic_vectors": [[0.5, 0.5]],
        "topic_term_vectors": [[0.3, 0.7]]
    }
    out = client.generate_short_summary(topic_vector_bundle)
    assert "Short bullet 1" in out
    assert out.count("•") >= 1


def test_send_request_throws_on_http_error(monkeypatch):
    """send_request should raise requests.HTTPError when response.raise_for_status() signals an error."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    client = OnlineLLMClient()

    def fake_post_error(url, headers=None, json=None, timeout=None):
        return MockResponse({"error": "bad"}, status_code=500, raise_on_status=True)

    monkeypatch.setattr(requests, "post", fake_post_error)

    with pytest.raises(requests.HTTPError):
        client.send_request("prompt", topic_vector_bundle={})