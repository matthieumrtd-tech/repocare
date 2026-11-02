"""Command-line interface for RepoCare."""

from __future__ import annotations

import argparse
import json
import sys

from .github_api import (
    GitHubApiError,
    issue_templates,
    latest_release,
    open_issues,
    open_pull_requests,
    repository,
    root_contents,
)
from .report import analyze, markdown


def _parse_repo(value: str) -> tuple[str, str]:
    parts = value.strip("/").split("/")
    if len(parts) != 2 or not all(parts):
        raise argparse.ArgumentTypeError("use the OWNER/REPOSITORY format, for example python/cpython")
    return parts[0], parts[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repocare",
        description="Create a read-only maintenance report for public GitHub repositories.",
        epilog="Set GITHUB_TOKEN to raise GitHub's API rate limit. The token is only read from the environment.",
    )
    parser.add_argument("repositories", nargs="+", metavar="OWNER/REPOSITORY")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def scan(value: str) -> dict:
    owner, name = _parse_repo(value)
    metadata = repository(owner, name)
    issues = open_issues(owner, name)
    pulls = open_pull_requests(owner, name)
    contents = root_contents(owner, name)
    templates = issue_templates(owner, name)
    release = latest_release(owner, name)
    return analyze(metadata, issues, pulls, contents, release, templates)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    reports = []
    for value in args.repositories:
        try:
            reports.append(scan(value))
        except argparse.ArgumentTypeError as error:
            parser.error(str(error))
        except GitHubApiError as error:
            print(f"repocare: {value}: {error}", file=sys.stderr)
            return 1

    if args.format == "json":
        print(json.dumps(reports, indent=2, ensure_ascii=False))
    else:
        print("\n\n---\n\n".join(markdown(report) for report in reports))
    return 0
