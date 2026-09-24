# 0001. Packaging with uv
**Date:** 2026-09-23 · **Step:** 0 · **Status:** accepted

## Context
A Python project needs a way to create a virtual environment (a private folder of libraries for one project), install libraries, and record exact versions in a lockfile so it installs the same way on any machine. None of these tools (uv, poetry) were installed on the Mac. See [Package manager](../concepts.md#package-manager).

## Options considered
- **uv.** One tool that creates the environment, installs libraries, and writes a lockfile automatically. Much faster. Uses `pyproject.toml`, the modern standard. Needs one extra install through Homebrew (uv 0.12.17 was available).
- **pip + venv.** Ship with Python, so nothing to install. But they are two separate tools and don't lock exact versions.

## Decision
Use uv, with `pyproject.toml` and `uv.lock`. It is one tool, it is fast, and it writes a lockfile automatically. `pyproject.toml` is the modern standard employers expect.

## Tradeoffs
One extra install via Homebrew.

## Revisit when
Never likely.
