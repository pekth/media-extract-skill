# ADR-0001: Check local documentation before delivery

Status: Accepted

## Context

The global rules require `scripts/documentation.py`, but this repository had no
such gate. The owner requested a minimal implementation for the CUDA fallback PR.

## Decision

Use Python's standard library and Git to maintain a Markdown document index in
`docs/KB.md` and check local inline file links. Run `--write` after document path
changes and `--check` before delivery and in PR CI. Preserve authored knowledge
and reject malformed index markers before writing.

## Limits

The gate does not fetch external URLs, validate heading fragments, or parse
reference-style links. Add a Markdown parser only when the documents need it.
