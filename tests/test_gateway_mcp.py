import base64
import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest

from src.gateway_mcp import handler

URL = "https://gw-abc.gateway.bedrock-agentcore.eu-west-1.amazonaws.com/mcp"


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("GATEWAY_MCP_URL", URL)
    monkeypatch.setenv("AWS_REGION", "eu-west-1")


def _event(body='{"jsonrpc":"2.0","id":1,"method":"tools/list"}', method="POST", **headers):
    base = {
        "content-type": "application/json",
        "accept": "application/json, text/event-stream",
        "authorization": "Bearer should-not-be-forwarded",
        "x-other": "dropped",
    }
    base.update(headers)
    return {
        "headers": base,
        "body": body,
        "isBase64Encoded": False,
        "requestContext": {"http": {"method": method}},
    }


def _upstream(status=200, body=b'{"result":{}}', headers=None):
    resp = MagicMock()
    resp.status = status
    resp.read.return_value = body
    resp.headers = headers or {"Content-Type": "application/json", "Mcp-Session-Id": "s1"}
    resp.__enter__.return_value = resp
    return resp


def _run(event, upstream=None, side_effect=None):
    captured = {}

    def fake_open(request, timeout=None):
        captured["request"] = request
        if side_effect:
            raise side_effect
        return upstream or _upstream()

    with patch.object(handler, "_sign", side_effect=lambda req: req) as sign:
        with patch.object(handler.urllib.request, "urlopen", side_effect=fake_open):
            result = handler.lambda_handler(event, None)
    return result, captured, sign


def test_forwards_body_and_returns_upstream_response():
    result, captured, sign = _run(_event())
    request = captured["request"]
    assert request.full_url == URL
    assert request.get_method() == "POST"
    assert request.data == b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
    sign.assert_called_once()
    assert result["statusCode"] == 200
    assert result["body"] == '{"result":{}}'
    assert result["headers"]["mcp-session-id"] == "s1"


def test_only_mcp_headers_are_forwarded_and_authorization_dropped():
    _, captured, _ = _run(_event(**{"mcp-session-id": "abc", "mcp-protocol-version": "2025-06-18"}))
    sent = {k.lower(): v for k, v in captured["request"].header_items()}
    assert sent["mcp-session-id"] == "abc"
    assert sent["mcp-protocol-version"] == "2025-06-18"
    assert sent["content-type"] == "application/json"
    assert "x-other" not in sent
    assert "should-not-be-forwarded" not in json.dumps(sent)


def test_base64_body_is_decoded():
    raw = b'{"jsonrpc":"2.0","id":2,"method":"ping"}'
    event = _event(body=base64.b64encode(raw).decode())
    event["isBase64Encoded"] = True
    _, captured, _ = _run(event)
    assert captured["request"].data == raw


def test_upstream_http_error_status_is_passed_through():
    err = urllib.error.HTTPError(URL, 400, "Bad", {"Content-Type": "application/json"}, None)
    err.read = lambda: b'{"error":"bad"}'
    result, _, _ = _run(_event(), side_effect=err)
    assert result["statusCode"] == 400
    assert result["body"] == '{"error":"bad"}'


def test_network_failure_returns_generic_502():
    result, _, _ = _run(_event(), side_effect=urllib.error.URLError("secret internal host"))
    assert result["statusCode"] == 502
    assert json.loads(result["body"]) == {"error": "Gateway unavailable"}
    assert "secret internal host" not in result["body"]


def test_missing_gateway_url_returns_generic_502(monkeypatch):
    monkeypatch.delenv("GATEWAY_MCP_URL")
    result = handler.lambda_handler(_event(), None)
    assert result["statusCode"] == 502
    assert json.loads(result["body"]) == {"error": "Gateway unavailable"}


def test_sign_uses_bedrock_agentcore_service():
    creds = MagicMock()
    creds.get_frozen_credentials.return_value = creds
    session = MagicMock()
    session.get_credentials.return_value = creds
    request = handler.urllib.request.Request(URL, data=b"{}", method="POST")
    with patch.object(handler.boto3, "Session", return_value=session):
        with patch.object(handler, "SigV4Auth") as auth_cls:
            handler._sign(request)
    assert auth_cls.call_args.args[1:] == ("bedrock-agentcore", "eu-west-1")
    auth_cls.return_value.add_auth.assert_called_once()
