"""Thin wrapper around the Jira REST API v3."""

from typing import Any, cast

import requests


def fetch_projects(session: requests.Session, base_url: str) -> list[dict[str, Any]]:
    """Return all projects the authenticated user can access.

    Raises:
        requests.HTTPError: On a non-2xx response.
    """
    resp = session.get(
        f"{base_url}/rest/api/3/project/search",
        params={"maxResults": 50, "orderBy": "name"},
        timeout=30,
    )
    resp.raise_for_status()
    return cast(list[dict[str, Any]], resp.json().get("values", []))


def parse_project(project: dict[str, Any]) -> dict[str, str]:
    """Convert a raw Jira project dict to a flat display dict.

    Keys: ``key``, ``name``, ``type``.
    """
    return {
        "key": project.get("key", ""),
        "name": project.get("name", "(unnamed)"),
        "type": project.get("projectTypeKey", ""),
    }


def fetch_issues(
    session: requests.Session, base_url: str, project_keys: list[str]
) -> list[dict[str, Any]]:
    """Return open issues across the given projects using a single JQL query.

    Fetches issues where ``statusCategory != Done``, ordered by last updated.
    Returns up to 200 issues.

    Raises:
        requests.HTTPError: On a non-2xx response.
    """
    if not project_keys:
        return []

    keys_joined = ", ".join(project_keys)
    jql = f"project in ({keys_joined}) AND statusCategory != Done ORDER BY updated DESC"
    resp = session.get(
        f"{base_url}/rest/api/3/search",
        params={
            "jql": jql,
            "maxResults": 200,
            "fields": "summary,status,issuetype,priority,assignee,updated,project",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return cast(list[dict[str, Any]], resp.json().get("issues", []))


def parse_issue(issue: dict[str, Any]) -> dict[str, str]:
    """Convert a raw Jira issue dict to a flat display dict.

    Keys: ``key``, ``summary``, ``status``, ``type``, ``priority``,
    ``assignee``, ``updated``, ``project_key``.
    """
    fields = issue.get("fields", {})
    assignee_obj = fields.get("assignee")
    priority_obj = fields.get("priority") or {}

    return {
        "key": issue.get("key", ""),
        "summary": fields.get("summary") or "(no summary)",
        "status": fields.get("status", {}).get("name", ""),
        "type": fields.get("issuetype", {}).get("name", ""),
        "priority": priority_obj.get("name", ""),
        "assignee": (
            assignee_obj.get("displayName", "") if assignee_obj else "Unassigned"
        ),
        "updated": fields.get("updated", ""),
        "project_key": fields.get("project", {}).get("key", ""),
    }
