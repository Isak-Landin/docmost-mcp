from __future__ import annotations

import os
from typing import Optional

import httpx

_token: Optional[str] = None


def _base_url() -> str:
    url = os.getenv("DOCMOST_APP_URL", "").rstrip("/")
    if not url:
        raise RuntimeError("DOCMOST_APP_URL is not set")
    return url


def login() -> str:
    """Authenticate against the Docmost REST API and return the access token.

    Reads DOCMOST_APP_URL, DOCMOST_USER_EMAIL, and DOCMOST_USER_PASSWORD from
    the environment. Raises RuntimeError if any variable is missing or if the
    login request fails.
    """
    email = os.getenv("DOCMOST_USER_EMAIL", "")
    password = os.getenv("DOCMOST_USER_PASSWORD", "")
    if not email or not password:
        raise RuntimeError("DOCMOST_USER_EMAIL and DOCMOST_USER_PASSWORD must be set")

    url = f"{_base_url()}/api/auth/login"
    response = httpx.post(url, json={"email": email, "password": password})
    response.raise_for_status()

    # Docmost returns the token as Set-Cookie: authToken=<jwt>; the JSON body
    # only contains {"success": true, "status": 200}.
    cookies = response.cookies
    token: Optional[str] = cookies.get("authToken")
    if not token:
        raise RuntimeError(
            "Docmost login did not set an authToken cookie. "
            f"Response status: {response.status_code}, body: {response.text[:200]}"
        )

    return token


def get_token() -> str:
    """Return the current in-memory access token, logging in first if needed."""
    global _token
    if _token is None:
        _token = login()
    return _token


def invalidate_token() -> None:
    """Clear the cached token, forcing a fresh login on the next get_token() call."""
    global _token
    _token = None


def auth_headers() -> dict[str, str]:
    """Return the Authorization header dict for use in Docmost REST API calls."""
    return {"Authorization": f"Bearer {get_token()}"}
