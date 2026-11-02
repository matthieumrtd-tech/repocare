
# RepoCare

**A practical, read-only maintenance report for public GitHub repositories.**

RepoCare helps maintainers spot a few items that may deserve a human review: older unanswered issues, pull requests with no recent activity, missing contributor guidance, and gaps in release history. Every signal links back to GitHub so maintainers can judge it in context.

The first version is deliberately small. It uses GitHub's public REST API, runs locally, and never changes a repository or sends source code to an AI service.

## Quick start

Requires Python 3.10 or newer.

```bash
git clone https://github.com/matthieumrtd-tech/repocare.git
cd repocare
python -m pip install .
repocare pallets/flask
```

Scan several repositories or request JSON output:

```bash
repocare pallets/flask psf/requests python/cpython
repocare --format json pallets/flask
```

Unauthenticated GitHub API requests have a low rate limit. To use a personal token for a higher limit, set `GITHUB_TOKEN` in your shell. RepoCare never prints or stores it. Use a fine-grained token with read-only public repository access, and never commit a token to a repository.

## What it checks

- Repository description, stars, forks, primary language, license, and last push.
- Up to 100 recently created open issues, with signals for issues at least seven days old with no comments and issues unchanged for at least 30 days.
- Up to 100 recently created open pull requests, with a signal for items unchanged for at least 14 days.
- Root-level README and CONTRIBUTING guidance, plus GitHub issue templates under `.github/ISSUE_TEMPLATE`.
- The latest published GitHub release and its age.

These are prompts for human review, not a quality score or a judgment about maintainers. Older work may be intentional or blocked by outside factors.

## Privacy and safety

- RepoCare sends read-only `GET` requests and never writes to issues, pull requests, repositories, or accounts.
- The first version reads public repository data only.
- Reports are printed in your terminal and are not sent elsewhere.
- An optional `GITHUB_TOKEN` is sent only to `api.github.com` in an authorization header.
- RepoCare makes no AI calls and does not send source code to Claude or another model.

## Current status

RepoCare is an early project. Its usefulness and adoption have not yet been measured. Feedback is welcome, especially examples where a signal is misleading or a useful maintenance action is missing.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and suggestions are welcome.

## License

MIT. See [LICENSE](LICENSE).
