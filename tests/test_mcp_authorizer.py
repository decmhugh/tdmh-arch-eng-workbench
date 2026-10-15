import json
import logging
from unittest.mock import Mock, patch

import pytest

from src.mcp_authorizer import handler

SECRET_ARN = "arn:aws:secretsmanager:eu-west-1:123456789012:secret:mcp-token"
TOKEN = "s3cr3t-token-value"


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    monkeypatch.setenv("TOKEN_SECRET_ARN", SECRET_ARN)
    handler._cache.update({"value": None, "expires": 0.0})


def _client(value=TOKEN):
    client = Mock()
    client.get_secret_value.return_value = {"SecretString": value}
    return client


def _event(auth):
    headers = {} if auth is None else {"authorization": auth}
    return {"headers": headers}


def test_correct_token_is_authorized():
    with patch.object(handler.boto3, "client", return_value=_client()):
        assert handler.lambda_handler(_event(f"Bearer {TOKEN}"), None) == {"isAuthorized": True}


@pytest.mark.parametrize(
    "auth",
    [None, "", "Bearer", "Bearer ", f"Basic {TOKEN}", TOKEN, "Bearer wrong"],
)
def test_missing_malformed_or_wrong_token_is_denied(auth):
    with patch.object(handler.boto3, "client", return_value=_client()):
        assert handler.lambda_handler(_event(auth), None) == {"isAuthorized": False}


def test_header_name_is_case_insensitive():
    event = {"headers": {"Authorization": f"Bearer {TOKEN}"}}
    with patch.object(handler.boto3, "client", return_value=_client()):
        assert handler.lambda_handler(event, None) == {"isAuthorized": True}


def test_uses_constant_time_comparison():
    with patch.object(handler.boto3, "client", return_value=_client()):
        with patch.object(handler.hmac, "compare_digest", return_value=True) as compare:
            handler.lambda_handler(_event(f"Bearer {TOKEN}"), None)
    compare.assert_called_once()


def test_secret_is_cached_within_ttl():
    client = _client()
    with patch.object(handler.boto3, "client", return_value=client):
        handler.lambda_handler(_event(f"Bearer {TOKEN}"), None)
        handler.lambda_handler(_event(f"Bearer {TOKEN}"), None)
    client.get_secret_value.assert_called_once_with(SecretId=SECRET_ARN)


def test_secret_is_refreshed_after_ttl():
    client = _client()
    with patch.object(handler.boto3, "client", return_value=client):
        with patch.object(handler.time, "monotonic", side_effect=[0.0, 301.0]):
            handler.lambda_handler(_event(f"Bearer {TOKEN}"), None)
            handler.lambda_handler(_event(f"Bearer {TOKEN}"), None)
    assert client.get_secret_value.call_count == 2


def test_secret_lookup_failure_fails_closed():
    client = Mock()
    client.get_secret_value.side_effect = handler.ClientError(
        {"Error": {"Code": "ResourceNotFoundException", "Message": "x"}}, "GetSecretValue"
    )
    with patch.object(handler.boto3, "client", return_value=client):
        assert handler.lambda_handler(_event(f"Bearer {TOKEN}"), None) == {"isAuthorized": False}


def test_empty_secret_fails_closed():
    with patch.object(handler.boto3, "client", return_value=_client("")):
        assert handler.lambda_handler(_event("Bearer "), None) == {"isAuthorized": False}


def test_logs_never_contain_token_or_header(caplog):
    with caplog.at_level(logging.DEBUG):
        with patch.object(handler.boto3, "client", return_value=_client()):
            handler.lambda_handler(_event(f"Bearer {TOKEN}"), None)
            handler.lambda_handler(_event("Bearer attacker-guess"), None)
    output = caplog.text + json.dumps([r.__dict__.get("msg") for r in caplog.records], default=str)
    assert TOKEN not in output
    assert "attacker-guess" not in output
