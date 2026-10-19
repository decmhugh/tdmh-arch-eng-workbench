#!/usr/bin/env python3
"""Status-checked HTTP for the Jira and greenhopper scripts.

curl is used rather than urllib because Python's SSL on macOS rejects the
corporate CA chain.

``curl -s`` exits **0 on 4xx and 5xx**, so the HTTP status has to be asked for
explicitly with ``-w``. Without it a rejected write is indistinguishable from a
successful one, which is how ``sync_epic_gates.py`` could report an epic moved
when Jira had refused the transition, and how ``manage_swimlanes.py`` could
delete every lane and then silently fail to recreate them.

Auth from env: ``JIRA_BASE_URL``, ``JIRA_USER_EMAIL``, ``JIRA_API_TOKEN``.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess

DEFAULT_BASE = "https://sunlife.atlassian.net"


class JiraHTTPError(RuntimeError):
    """A Jira call that did not return a 2xx, or returned an unparseable body."""

    def __init__(self, method: str, path: str, status: int | None, detail: str) -> None:
        self.status = status
        code = status if status is not None else "no response"
        super().__init__(f"{method} {path} -> {code}: {detail}")


def _auth_header() -> str:
    raw = f"{os.environ['JIRA_USER_EMAIL']}:{os.environ['JIRA_API_TOKEN']}".encode()
    return "Basic " + base64.b64encode(raw).decode()


def base_url() -> str:
    return os.environ.get("JIRA_BASE_URL", DEFAULT_BASE)


def _detail(body: str) -> str:
    """Jira packs failures into errorMessages/errors; fall back to the raw body."""
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return " ".join(body.split())[:400] or "(empty body)"
    if isinstance(parsed, dict):
        messages = list(parsed.get("errorMessages") or [])
        messages += [f"{k}: {v}" for k, v in (parsed.get("errors") or {}).items()]
        if messages:
            return "; ".join(messages)[:400]
    return json.dumps(parsed)[:400]


def request(method: str, path: str, payload: dict | None = None, *, timeout: int = 60) -> dict:
    """Call ``path`` on the Jira base URL and return the parsed body.

    Raises ``JiraHTTPError`` on a non-2xx status, a curl failure, or a 2xx body
    that is not JSON — an HTML SSO redirect reaching a caller as a string is a
    failure worth seeing at the call site, not three frames later.
    """
    cmd = [
        "curl", "-sS", "--max-time", str(timeout),
        "-X", method,
        "-H", f"Authorization: {_auth_header()}",
        "-H", "Content-Type: application/json",
        "-H", "Accept: application/json",
        "-H", "X-Atlassian-Token: no-check",
        "-w", "\n%{http_code}",
        f"{base_url()}{path}",
    ]
    if payload is not None:
        cmd += ["-d", json.dumps(payload)]

    result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603
    if result.returncode != 0:
        raise JiraHTTPError(method, path, None, result.stderr.strip() or "curl failed")

    body, _, status = result.stdout.rpartition("\n")
    if not status.strip().isdigit():
        raise JiraHTTPError(method, path, None, f"no status code in response: {result.stdout[:300]}")

    code = int(status)
    if code >= 400:
        raise JiraHTTPError(method, path, code, _detail(body))

    body = body.strip()
    if not body:
        return {}  # 204, as transitions and swimlane deletes return
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise JiraHTTPError(method, path, code, f"expected JSON, got {body[:300]}") from None
