import os
import requests
import pytest

from llm_api import LLMAPIClient
from stats_cache import collect_stats

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
    client = LLMAPIClient()
    assert client.api_key == "env-test-key"


def test_constructor_uses_api_key_argument(monkeypatch):
    """Explicit api_key argument should override the environment variable."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
    client = LLMAPIClient(api_key="param-key")
    assert client.api_key == "param-key"
    assert client.api_key != "env-key"


def test_raises_error_when_no_api_key(monkeypatch):
    """Constructor raises ValueError if no API key is available."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ValueError):
        LLMAPIClient()


def test_send_request_builds_and_posts_payload(monkeypatch):
    """send_request should construct the correct URL, headers, timeout and JSON body."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    client = LLMAPIClient()
    captured = {}

    #capture post
    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return MockResponse({"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(requests, "post", fake_post)

    bundle = collect_stats( #prepare mock bundle
        metadata_stats={"a.py": {"size": 10}},
        text_analysis={"keywords": ["x"]},
        project_analysis={"repositories": [{"total_commits": 1}]}
    )
    resp = client.send_request(prompt="Hello", data_bundle=bundle)

    #check headers and payload
    assert captured["url"].endswith("/chat/completions")
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["timeout"] == 30
    assert isinstance(captured["json"], dict)
    assert captured["json"]["model"] == client.model
    assert "messages" in captured["json"]
    assert resp["choices"][0]["message"]["content"] == "ok"


def test_data_bundle_is_appended_to_message(monkeypatch):
    """The data_bundle should be present in the message content sent to the API."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    client = LLMAPIClient()

    def fake_post(url, headers=None, json=None, timeout=None):
        content = json["messages"][0]["content"]
        assert "metadata_stats" in content
        return MockResponse({"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(requests, "post", fake_post)

    #preparebundle
    bundle = collect_stats(
        metadata_stats={"b.py": {"size": 20}},
        text_analysis={"keywords": ["y"]},
        project_analysis={"repositories": [{"total_commits": 2}]}
    )
    client.send_request(prompt="Summarize", data_bundle=bundle)


def test_online_short_summary_returns_response(monkeypatch):
    """online_generate_short_summary should use send_request and return the LLM text."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    client = LLMAPIClient()

    def fake_send(self, prompt, data_bundle):
        return {"choices": [{"message": {"content": "• Short bullet 1\n• Short bullet 2"}}]}

    monkeypatch.setattr(LLMAPIClient, "send_request", fake_send)

    bundle = collect_stats(
        metadata_stats={"c.py": {"size": 30}},
        text_analysis={"keywords": ["z"]},
        project_analysis={"repositories": [{"total_commits": 3}]}
    )
    out = client.online_generate_short_summary(bundle)
    assert "Short bullet 1" in out
    assert out.count("•") >= 1


def test_send_request_throws_on_http_error(monkeypatch):
    """send_request should raise requests.HTTPError when response.raise_for_status() signals an error."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    client = LLMAPIClient()

    def fake_post_error(url, headers=None, json=None, timeout=None):
        return MockResponse({"error": "bad"}, status_code=500, raise_on_status=True)

    monkeypatch.setattr(requests, "post", fake_post_error)

    with pytest.raises(requests.HTTPError):
        client.send_request("prompt", data_bundle="{}")