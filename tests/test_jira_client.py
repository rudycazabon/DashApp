"""Tests for tools/jira/client.py — Jira REST API wrapper."""

from unittest.mock import MagicMock

import pytest

from tools.jira.client import (
    fetch_issues,
    fetch_projects,
    parse_issue,
    parse_project,
)

BASE_URL = "https://example.atlassian.net"


def _mock_session(json_data: dict) -> MagicMock:
    """Return a mock session whose get() call returns json_data."""
    session = MagicMock()
    session.get.return_value.json.return_value = json_data
    return session


# ---------------------------------------------------------------------------
# fetch_projects
# ---------------------------------------------------------------------------


def test_fetch_projects_returns_values() -> None:
    """fetch_projects returns the 'values' list from the response."""
    session = _mock_session({"values": [{"key": "PROJ", "name": "My Project"}]})

    result = fetch_projects(session, BASE_URL)

    assert result == [{"key": "PROJ", "name": "My Project"}]
    session.get.return_value.raise_for_status.assert_called_once()


def test_fetch_projects_empty_when_no_values_key() -> None:
    """fetch_projects returns [] when 'values' key is absent."""
    session = _mock_session({})

    result = fetch_projects(session, BASE_URL)

    assert result == []


def test_fetch_projects_raises_on_http_error() -> None:
    """fetch_projects propagates HTTPError from raise_for_status."""
    import requests as req_lib

    session = MagicMock()
    session.get.return_value.raise_for_status.side_effect = req_lib.HTTPError("403")

    with pytest.raises(req_lib.HTTPError):
        fetch_projects(session, BASE_URL)


# ---------------------------------------------------------------------------
# parse_project
# ---------------------------------------------------------------------------


def test_parse_project_normal_fields() -> None:
    """parse_project maps Jira project fields to the flat display dict."""
    project = {"key": "PROJ", "name": "My Project", "projectTypeKey": "software"}

    result = parse_project(project)

    assert result["key"] == "PROJ"
    assert result["name"] == "My Project"
    assert result["type"] == "software"


def test_parse_project_defaults_for_missing_fields() -> None:
    """parse_project uses safe defaults when fields are absent."""
    result = parse_project({})

    assert result["key"] == ""
    assert result["name"] == "(unnamed)"
    assert result["type"] == ""


# ---------------------------------------------------------------------------
# fetch_issues
# ---------------------------------------------------------------------------


def test_fetch_issues_returns_issues() -> None:
    """fetch_issues returns the 'issues' list from the response."""
    session = _mock_session({"issues": [{"key": "PROJ-1"}, {"key": "PROJ-2"}]})

    result = fetch_issues(session, BASE_URL, ["PROJ"])

    assert result == [{"key": "PROJ-1"}, {"key": "PROJ-2"}]


def test_fetch_issues_empty_when_no_project_keys() -> None:
    """fetch_issues returns [] immediately when project_keys is empty."""
    session = MagicMock()

    result = fetch_issues(session, BASE_URL, [])

    assert result == []
    session.get.assert_not_called()


def test_fetch_issues_raises_on_http_error() -> None:
    """fetch_issues propagates HTTPError from raise_for_status."""
    import requests as req_lib

    session = MagicMock()
    session.get.return_value.raise_for_status.side_effect = req_lib.HTTPError("401")

    with pytest.raises(req_lib.HTTPError):
        fetch_issues(session, BASE_URL, ["PROJ"])


# ---------------------------------------------------------------------------
# parse_issue
# ---------------------------------------------------------------------------


def test_parse_issue_normal_fields() -> None:
    """parse_issue maps Jira issue fields to the flat display dict."""
    issue = {
        "key": "PROJ-42",
        "fields": {
            "summary": "Fix the bug",
            "status": {"name": "In Progress"},
            "issuetype": {"name": "Bug"},
            "priority": {"name": "High"},
            "assignee": {"displayName": "Alice"},
            "updated": "2026-02-19T10:00:00.000+0000",
            "project": {"key": "PROJ"},
        },
    }

    result = parse_issue(issue)

    assert result["key"] == "PROJ-42"
    assert result["summary"] == "Fix the bug"
    assert result["status"] == "In Progress"
    assert result["type"] == "Bug"
    assert result["priority"] == "High"
    assert result["assignee"] == "Alice"
    assert result["updated"] == "2026-02-19T10:00:00.000+0000"
    assert result["project_key"] == "PROJ"


def test_parse_issue_unassigned_and_no_priority() -> None:
    """parse_issue handles absent assignee and priority gracefully."""
    issue = {
        "key": "PROJ-1",
        "fields": {
            "summary": "Task",
            "status": {"name": "To Do"},
            "issuetype": {"name": "Task"},
            "priority": None,
            "assignee": None,
            "updated": "",
            "project": {"key": "PROJ"},
        },
    }

    result = parse_issue(issue)

    assert result["assignee"] == "Unassigned"
    assert result["priority"] == ""


def test_parse_issue_defaults_for_missing_fields() -> None:
    """parse_issue uses safe defaults when all fields are absent."""
    result = parse_issue({})

    assert result["key"] == ""
    assert result["summary"] == "(no summary)"
    assert result["status"] == ""
    assert result["project_key"] == ""
