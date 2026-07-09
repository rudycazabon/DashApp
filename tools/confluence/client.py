"""Thin wrapper around the Confluence Cloud REST API v2.

The Confluence REST API lives under ``<base_url>/wiki``; ``base_url`` is the
Atlassian site root as stored in ``confluence_credentials.json``.
"""

from typing import Any, cast

import requests


def fetch_spaces(session: requests.Session, base_url: str) -> list[dict[str, Any]]:
    """Return spaces the authenticated user can access, ordered by name.

    Returns up to 50 spaces.

    Raises:
        requests.HTTPError: On a non-2xx response.
    """
    resp = session.get(
        f"{base_url}/wiki/api/v2/spaces",
        params={"limit": 50, "sort": "name"},
        timeout=30,
    )
    resp.raise_for_status()
    return cast(list[dict[str, Any]], resp.json().get("results", []))


def parse_space(space: dict[str, Any]) -> dict[str, str]:
    """Convert a raw Confluence space dict to a flat display dict.

    Keys: ``id``, ``key``, ``name``, ``type``.
    """
    return {
        "id": str(space.get("id", "")),
        "key": space.get("key", ""),
        "name": space.get("name", "(unnamed)"),
        "type": space.get("type", ""),
    }


def fetch_pages(session: requests.Session, base_url: str) -> list[dict[str, Any]]:
    """Return the most recently modified current pages across all spaces.

    Fetches pages ordered by last-modified date (newest first). Returns up to
    100 pages; group them by ``space_id`` for display.

    Raises:
        requests.HTTPError: On a non-2xx response.
    """
    resp = session.get(
        f"{base_url}/wiki/api/v2/pages",
        params={"limit": 100, "sort": "-modified-date", "status": "current"},
        timeout=30,
    )
    resp.raise_for_status()
    return cast(list[dict[str, Any]], resp.json().get("results", []))


def parse_page(page: dict[str, Any]) -> dict[str, str]:
    """Convert a raw Confluence page dict to a flat display dict.

    Keys: ``id``, ``title``, ``status``, ``space_id``, ``version``, ``updated``.
    ``updated`` is the latest version's timestamp, falling back to the page's
    creation date.
    """
    version = page.get("version") or {}
    version_number = version.get("number")

    return {
        "id": str(page.get("id", "")),
        "title": page.get("title") or "(untitled)",
        "status": page.get("status", ""),
        "space_id": str(page.get("spaceId", "")),
        "version": str(version_number) if version_number is not None else "",
        "updated": version.get("createdAt") or page.get("createdAt", ""),
    }
