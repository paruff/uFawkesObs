# Contributing to uFawkesObs

Thank you for your interest in contributing to uFawkesObs!

## Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/<your-username>/uFawkesObs.git`
3. **Create** a branch: `git checkout -b feat/my-feature`
4. **Make** your changes
5. **Test** your changes: `make test-acceptance`
6. **Commit** with a conventional commit message
7. **Push** and open a Pull Request

## Development Setup

```bash
# Start the full observability stack
make up

# Run acceptance tests
make test-acceptance

# Stop the stack
make down
```

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(compose): add new exporter
fix(config): correct scrape interval
docs: update README
chore: bump prometheus version
```

Prefixes: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`, `perf`, `ci`

## Pull Request Requirements

- All acceptance tests must pass
- Docker Compose config must validate: `docker compose config --quiet`
- PR description must follow the AI-Assisted Review Block format (see AGENTS.md)
- One component per PR — no bundled changes
- All image versions must be pinned (no `latest`)

## Reporting Issues

- Use GitHub Issues for bugs and feature requests
- Include stack traces, logs, and reproduction steps for bugs
- Tag issues with appropriate labels

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you agree to uphold its standards.

## License

By contributing, you agree that your contributions will be licensed under the
[Apache License 2.0](LICENSE).
