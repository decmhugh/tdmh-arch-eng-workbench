import hmac
import logging
import os
import time
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

CACHE_TTL_SECONDS = 300
_cache: dict[str, Any] = {"value": None, "expires": 0.0}


def _expected_token() -> str | None:
    now = time.monotonic()
    if _cache["value"] is not None and now < _cache["expires"]:
        return _cache["value"]
    try:
        client = boto3.client("secretsmanager")
        value = client.get_secret_value(SecretId=os.environ["TOKEN_SECRET_ARN"]).get("SecretString")
    except (BotoCoreError, ClientError, KeyError):
        logger.error("token secret lookup failed")
        return None
    if not value:
        return None
    _cache.update({"value": value, "expires": now + CACHE_TTL_SECONDS})
    return value


def _presented_token(event: dict[str, Any]) -> str | None:
    headers = event.get("headers") or {}
    header = next((v for k, v in headers.items() if k.lower() == "authorization"), None)
    if not isinstance(header, str):
        return None
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, bool]:
    presented = _presented_token(event)
    if presented is None:
        return {"isAuthorized": False}
    expected = _expected_token()
    if expected is None:
        return {"isAuthorized": False}
    allowed = hmac.compare_digest(presented.encode("utf-8"), expected.encode("utf-8"))
    logger.info('{"event": "mcp_auth", "authorized": %s}', str(allowed).lower())
    return {"isAuthorized": allowed}
