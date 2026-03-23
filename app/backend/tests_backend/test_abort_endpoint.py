import os
import sys
from uuid import uuid4
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from main_api import app


client = TestClient(app)


def test_abort_upload_success():
    analysis_id = str(uuid4())

    with patch("main_api.os.path.exists", return_value=True), patch("main_api.os.remove") as mock_remove:
        response = client.delete(f"/projects/{analysis_id}/upload/abort")

    assert response.status_code == 200
    assert response.json() == {"message": "Upload aborted and cache cleared."}
    assert mock_remove.called


def test_abort_upload_not_found():
    analysis_id = str(uuid4())

    with patch("main_api.os.path.exists", return_value=False), patch("main_api.os.remove") as mock_remove:
        response = client.delete(f"/projects/{analysis_id}/upload/abort")

    assert response.status_code == 404
    assert response.json() == {"message": "No pending upload found to abort."}
    mock_remove.assert_not_called()


def test_abort_upload_invalid_uuid():
    response = client.delete("/projects/not-a-valid-uuid/upload/abort")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid UUID format"


def test_abort_upload_delete_failure():
    analysis_id = str(uuid4())

    with patch("main_api.os.path.exists", return_value=True), patch(
        "main_api.os.remove", side_effect=Exception("Mocked permission error")
    ):
        response = client.delete(f"/projects/{analysis_id}/upload/abort")

    assert response.status_code == 500
    assert "Failed to delete cache file" in response.json()["detail"]