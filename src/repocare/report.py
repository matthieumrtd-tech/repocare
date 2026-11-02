"""Turn GitHub repository data into transparent, actionable signals."""

from __future__ import annotations

from datetime import datetime, timezone


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def age_days(value: str | None, now: datetime) -> int | None:
    date = parse_datetime(value)
    if date is None:
        return None
    return max(0, (now - date.astimezone(timezone.utc)).days)


def _title(item: dict) -> str:
    return " ".join(str(item.get("title", "Untitled")).split())


def _link(item: dict) -> str:
    return str(item.get("html_url", ""))


def analyze(
    repository: dict,
    issues: list[dict],
    pulls: list[dict],
    contents: list[dict],
    release: dict | None,
    has_issue_templates: bool,
) -> dict:
    now = datetime.now(timezone.utc)
    stale_issues = [item for item in issues if (age_days(item.get("updated_at"), now) or 0) >= 30]
    unanswered_issues = [
        item for item in issues
        if (age_days(item.get("created_at"), now) or 0) >= 7
        and int(item.get("comments", 0)) == 0
    ]
    stale_pulls = [item for item in pulls if (age_days(item.get("updated_at"), now) or 0) >= 14]

    file_names = {str(item.get("name", "")).lower() for item in contents}
    has_readme = any(name.startswith("readme") for name in file_names)
    has_contributing = any(name.startswith("contributing") for name in file_names)
    return {
        "name": repository.get("full_name", "unknown/unknown"),
        "url": repository.get("html_url", ""),
        "description": repository.get("description") or "No repository description",
        "stars": int(repository.get("stargazers_count", 0)),
        "forks": int(repository.get("forks_count", 0)),
        "open_items_total": int(repository.get("open_issues_count", 0)),
        "language": repository.get("language") or "Not reported",
        "default_branch": repository.get("default_branch") or "Not reported",
        "license": (repository.get("license") or {}).get("spdx_id") or "No detected license",
        "pushed_days_ago": age_days(repository.get("pushed_at"), now),
        "issue_sample_size": len(issues),
        "stale_issues": sorted(stale_issues, key=lambda item: item.get("updated_at", "")),
        "unanswered_issues": sorted(unanswered_issues, key=lambda item: item.get("created_at", "")),
        "pull_sample_size": len(pulls),
        "stale_pulls": sorted(stale_pulls, key=lambda item: item.get("updated_at", "")),
        "release": release,
        "release_days_ago": age_days((release or {}).get("published_at"), now),
        "has_readme": has_readme,
        "has_contributing": has_contributing,
        "has_issue_templates": has_issue_templates,
    }


def _short_list(items: list[dict], limit: int = 5) -> list[str]:
    rows = []
    for item in items[:limit]:
        days = age_days(item.get("updated_at"), datetime.now(timezone.utc))
        label = f"{_title(item)} ({days} days since update)"
        url = _link(item)
        rows.append(f"- [{label}]({url})" if url else f"- {label}")
    if len(items) > limit:
        rows.append(f"- …and {len(items) - limit} more in the reviewed sample")
    return rows


def markdown(report: dict) -> str:
    lines = [
        f"# RepoCare report: {report['name']}",
        "",
        f"{report['description']}",
        "",
        f"Repository: {report['url']}",
        "",
        "## Snapshot",
        "",
        f"- Stars: {report['stars']:,} · forks: {report['forks']:,}",
        f"- GitHub open-item count: {report['open_items_total']:,} (GitHub's repository summary)",
        f"- Primary language: {report['language']}",
        f"- Default branch: `{report['default_branch']}`",
        f"- License detected: `{report['license']}`",
        f"- Last push: {_days_label(report['pushed_days_ago'])}",
        f"- Latest published release: {_release_label(report)}",
        "",
        "## Maintenance signals",
        "",
    ]

    if report["unanswered_issues"]:
        lines.append("### Open issues at least 7 days old with no comments")
        lines.append("")
        lines.extend(_short_list(report["unanswered_issues"]))
        lines.append("")
    else:
        lines.extend(["- No unanswered issue signal found in the reviewed sample.", ""])

    if report["stale_issues"]:
        lines.append("### Open issues not updated for at least 30 days")
        lines.append("")
        lines.extend(_short_list(report["stale_issues"]))
        lines.append("")
    else:
        lines.extend(["- No 30-day stale issue signal found in the reviewed sample.", ""])

    if report["stale_pulls"]:
        lines.append("### Open pull requests not updated for at least 14 days")
        lines.append("")
        lines.extend(_short_list(report["stale_pulls"]))
        lines.append("")
    else:
        lines.extend(["- No 14-day stale pull request signal found in the reviewed sample.", ""])

    recommendations = []
    if not report["has_readme"]:
        recommendations.append("Add a README that explains the project's purpose and how to get started.")
    if not report["has_contributing"]:
        recommendations.append("Add a CONTRIBUTING guide with setup, review, and pull request expectations.")
    if not report["has_issue_templates"]:
        recommendations.append("Consider issue templates so bug reports and feature requests arrive with useful context.")
    if report["release_days_ago"] is None:
        recommendations.append("Publish a first tagged release if the project is ready for users.")
    elif report["release_days_ago"] >= 180:
        recommendations.append("Review whether a release or a short maintenance-status note would help users.")
    if report["stale_pulls"]:
        recommendations.append("Review the oldest open pull requests and either give feedback, merge, or close with an explanation.")
    if report["unanswered_issues"]:
        recommendations.append("Acknowledge older unanswered issues, even when the answer is that they are not planned.")

    lines.extend(["## Suggested next steps", ""])
    if recommendations:
        lines.extend(f"- {item}" for item in recommendations)
    else:
        lines.append("- No setup gap was detected in the repository root. Review the open-item signals above and ask maintainers whether anything is missing.")

    lines.extend([
        "",
        "## Scope and limits",
        "",
        f"RepoCare reviewed up to {report['issue_sample_size']} recently created open issues and {report['pull_sample_size']} recently created open pull requests. Signals are simple age and metadata checks, not a quality score or a judgment about maintainers. An issue can be old for a good reason. Review the linked items before acting.",
        "",
        "Generated from GitHub's public REST API. RepoCare does not write to repositories or send code to an AI service.",
    ])
    return "\n".join(lines)


def _days_label(days: int | None) -> str:
    if days is None:
        return "unknown"
    return "today" if days == 0 else f"{days} days ago"


def _release_label(report: dict) -> str:
    release = report["release"]
    days = report["release_days_ago"]
    if release is None:
        return "none found"
    tag = release.get("tag_name") or "untagged"
    return f"`{tag}` ({_days_label(days)})"
