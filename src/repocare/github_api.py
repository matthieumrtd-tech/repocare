"""Small, read-only client for the public GitHub REST API."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

API_ROOT = "https://api.github.com"
USER_AGENT = "RepoCare/0.1.0 (open-source repository maintenance report)"


class GitHubApiError(Exception):
    """An API or network error that can be shown safely to the CLI user."""


def get_json(path: str):
    """Fetch one GitHub API endpoint. A token is optional and never displayed."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(f"{API_ROOT}{path}", headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 404:
            raise GitHubApiError("GitHub could not find that public repository or resource.") from None
        if error.code == 403 and error.headers.get("X-RateLimit-Remaining") == "0":
            raise GitHubApiError(
                "GitHub's unauthenticated API limit was reached. Set GITHUB_TOKEN and retry."
            ) from None
        if error.code == 401:
            raise GitHubApiError("GitHub rejected the token in GITHUB_TOKEN.") from None
        raise GitHubApiError(f"GitHub API returned HTTP {error.code}.") from None
    except URLError as error:
        reason = getattr(error, "reason", "network error")
        raise GitHubApiError(f"Could not reach GitHub: {reason}.") from None
    except TimeoutError:
        raise GitHubApiError("The GitHub API request timed out.") from None


def repository(owner: str, name: str) -> dict:
    owner_part = quote(owner, safe="")
    name_part = quote(name, safe="")
    return get_json(f"/repos/{owner_part}/{name_part}")


def open_issues(owner: str, name: str) -> list[dict]:
    owner_part = quote(owner, safe="")
    name_part = quote(name, safe="")
    result = get_json(
        f"/repos/{owner_part}/{name_part}/issues?state=open&sort=created&direction=desc&per_page=100"
    )
    return [item for item in result if "pull_request" not in item]


def open_pull_requests(owner: str, name: str) -> list[dict]:
    owner_part = quote(owner, safe="")
    name_part = quote(name, safe="")
    return get_json(
        f"/repos/{owner_part}/{name_part}/pulls?state=open&sort=created&direction=desc&per_page=100"
    )


def root_contents(owner: str, name: str) -> list[dict]:
    owner_part = quote(owner, safe="")
    name_part = quote(name, safe="")
    result = get_json(f"/repos/{owner_part}/{name_part}/contents")
    return result if isinstance(result, list) else []


def issue_templates(owner: str, name: str) -> bool:
    owner_part = quote(owner, safe="")
    name_part = quote(name, safe="")
    try:
        result = get_json(f"/repos/{owner_part}/{name_part}/contents/.github/ISSUE_TEMPLATE")
    except GitHubApiError as error:
        if str(error).startswith("GitHub could not find"):
            return False
        raise
    return isinstance(result, list) and bool(result)


def latest_release(owner: str, name: str) -> dict | None:
    owner_part = quote(owner, safe="")
    name_part = quote(name, safe="")
    try:
        return get_json(f"/repos/{owner_part}/{name_part}/releases/latest")
    except GitHubApiError as error:
        if str(error).startswith("GitHub could not find"):
            return None
        raise
