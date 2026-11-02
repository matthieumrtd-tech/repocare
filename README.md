# RepoCare

**A practical, read-only maintenance report for public GitHub repositories.**

RepoCare helps maintainers and contributors spot a few useful next actions: older unanswered issues, open pull requests that may need attention, missing contributor guidance, and release-history gaps. Each signal links back to the item so people can review it in context.

The first version is intentionally small. It uses GitHub's public REST API, runs locally, and never changes repositories or sends source code to an AI service.

## Quick start

Requires Python 3.10 or newer.

```bash
python -m pip install .
repocare pallets/flask
```

Or run from a checkout:

```bash
python -m repocare pallets/flask
```

Analyze several repositories or emit JSON:

```bash
repocare pallets/flask psf/requests python/cpython
repocare --format json pallets/flask
```

Unauthenticated GitHub API requests have a low rate limit. Set `GITHUB_TOKEN` in your shell to use a personal token for a higher limit. RepoCare never prints or stores the token; use a fine-grained token with read-only public repository access.

## What it checks

- Repository basics: description, stars, forks, language, license, and last push.
- Open issues: up to 100 recently created, with signals for unanswered items at least 7 days old and items unchanged for at least 30 days.
- Open pull requests: up to 100 recently created, with a signal for items unchanged for at least 14 days.
- Setup: README, root-level CONTRIBUTING guide, and GitHub issue templates.
- Latest published GitHub release and its age.

These are prompts for human review, not a score or judgment about maintainers. Old work may be intentional or blocked by outside factors.

## Privacy and safety

- Read-only: RepoCare makes `GET` requests and never writes to issues, pull requests, repositories, or accounts.
- Public data only in this first version.
- Reports print in your terminal and are not transmitted elsewhere.
- The optional token is read from `GITHUB_TOKEN` and sent only to `api.github.com` in an authorization header.
- No AI calls; source code is not sent to Claude or another model.

## Current status

RepoCare is an early project. Its usefulness and adoption have not yet been measured. The initial goal is to make repository triage more concrete and less dependent on maintainers repeatedly rediscovering old work.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and suggestions are welcome, especially examples where a signal is misleading or a useful action is missing.

## License

MIT. See [LICENSE](LICENSE).
