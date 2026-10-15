import base64
import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

SERVICE = "bedrock-agentcore"
FORWARDED_REQUEST_HEADERS = ("content-type", "accept", "mcp-session-id", "mcp-protocol-version")
RETURNED_RESPONSE_HEADERS = ("content-type", "mcp-session-id", "mcp-protocol-version")
TIMEOUT_SECONDS = 25


def _response(status: int, body: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    return {"statusCode": status, "headers": headers or {}, "body": body}


def _bad_gateway() -> dict[str, Any]:
    return _response(
        502,
        json.dumps({"error": "Gateway unavailable"}),
        {"content-type": "application/json"},
    )


def _sign(request: urllib.request.Request) -> urllib.request.Request:
    credentials = boto3.Session().get_credentials().get_frozen_credentials()
    aws_request = AWSRequest(
        method=request.get_method(),
        url=request.full_url,
        data=request.data,
        headers=dict(request.header_items()),
    )
    SigV4Auth(credentials, SERVICE, os.environ["AWS_REGION"]).add_auth(aws_request)
    for key, value in aws_request.headers.items():
        request.add_header(key, value)
    return request


def _forward_headers(event: dict[str, Any]) -> dict[str, str]:
    incoming = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    return {name: incoming[name] for name in FORWARDED_REQUEST_HEADERS if name in incoming}


def _body(event: dict[str, Any]) -> bytes | None:
    body = event.get("body")
    if body is None:
        return None
    if event.get("isBase64Encoded"):
        return base64.b64decode(body)
    return body.encode("utf-8")


def _result(status: int, body: bytes, headers: Any) -> dict[str, Any]:
    lowered = {k.lower(): v for k, v in headers.items()}
    kept = {name: lowered[name] for name in RETURNED_RESPONSE_HEADERS if name in lowered}
    return _response(status, body.decode("utf-8", errors="replace"), kept)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    url = os.environ.get("GATEWAY_MCP_URL")
    if not url:
        logger.error("gateway url not configured")
        return _bad_gateway()

    method = event.get("requestContext", {}).get("http", {}).get("method", "POST")
    request = urllib.request.Request(
        url,
        data=_body(event),
        headers=_forward_headers(event),
        method=method,
    )
    try:
        with urllib.request.urlopen(_sign(request), timeout=TIMEOUT_SECONDS) as upstream:
            return _result(upstream.status, upstream.read(), upstream.headers)
    except urllib.error.HTTPError as err:
        return _result(err.code, err.read(), err.headers or {})
    except Exception:
        logger.error("gateway request failed")
        return _bad_gateway()
