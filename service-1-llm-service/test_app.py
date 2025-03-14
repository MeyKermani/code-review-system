import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, mock_open
import json
from app import app  # Import your FastAPI application

client = TestClient(app)  # Create a test client for FastAPI

# Test when LLM_PROVIDER is "openai"


@pytest.fixture
def mock_env_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")


# Test when LLM_PROVIDER is "deepseek"
@pytest.fixture
def mock_env_deepseek(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")


# Test when LLM_PROVIDER is not set
@pytest.fixture
def mock_env_default(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)


# Mock OpenAI client
@pytest.fixture
def mock_openai_client():
    with patch("app.OpenAI") as mock_client:
        yield mock_client


# Mock file read for API key
@pytest.fixture
def mock_file_read():
    mock_file = mock_open(read_data="dummy_api_key")
    with patch("builtins.open", mock_file):
        yield mock_file


# Test case: Analyze endpoint with valid request and "openai" provider
def test_analyze_openai(mock_env_openai, mock_openai_client, mock_file_read):
    mock_openai_client.return_value.chat.with_raw_response.completions.create.return_value.content = json.dumps({
        "choices": [
            {
                "message": {
                    "content": "This is a suggestion for the function."
                }
            }
        ]
    })

    response = client.post(
        "/analyze",
        json={"function_code": "def test_function(): pass"}
    )

    assert response.status_code == 200


# Test case: Analyze endpoint with valid request and "deepseek" provider
def test_analyze_deepseek(mock_env_deepseek, mock_openai_client, mock_file_read):
    mock_openai_client.return_value.chat.with_raw_response.completions.create.return_value.content = json.dumps({
        "choices": [
            {
                "message": {
                    "content": "This is a suggestion for deepseek."
                }
            }
        ]
    })

    response = client.post(
        "/analyze",
        json={"function_code": "def test_function(): pass"}
    )

    assert response.status_code == 200


# Test case: Analyze endpoint with valid request and default provider
def test_analyze_default(mock_env_default, mock_openai_client, mock_file_read):
    mock_openai_client.return_value.chat.with_raw_response.completions.create.return_value.content = json.dumps({
        "choices": [
            {
                "message": {
                    "content": "This is a suggestion for the default provider."
                }
            }
        ]
    })

    response = client.post(
        "/analyze",
        json={"function_code": "def test_function(): pass"}
    )

    assert response.status_code == 200


# Test case: Analyze endpoint when OpenAI client raises an exception
def test_analyze_exception(mock_env_openai, mock_openai_client, mock_file_read):
    mock_openai_client.return_value.chat.with_raw_response.completions.create.side_effect = Exception("API error")

    response = client.post(
        "/analyze",
        json={"function_code": "def test_function(): pass"}
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "API error"
    }
