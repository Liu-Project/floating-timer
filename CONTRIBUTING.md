# Contributing

Thanks for your interest in **Floating Timer**! Contributions of all kinds are
welcome — bug reports, feature ideas, documentation, and code.

## Getting started

1. Fork the repository and clone it locally.
2. Create a feature branch: `git checkout -b feat/my-change`.
3. Make your changes.

## Development

The app has no third-party runtime dependencies. Run it directly:

```bash
python3 src/floating_timer.py
```

Run the test suite:

```bash
pip install pytest
pytest -v
```

Please keep the code simple, dependency-free, and compatible with Python 3.8+.

## Commit conventions

Use clear, imperative commit messages, e.g.:

- `feat: add preset duration menu`
- `fix: keep countdown running after window restore`
- `docs: add demo screenshot`

## Submitting changes

1. Commit your changes and push to your fork.
2. Open a pull request describing what you changed and why.
3. Make sure CI (tests) passes.

## Releasing

Maintainers: to cut a release, push a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The [Release workflow](.github/workflows/release.yml) builds the static binary
and publishes it automatically.
