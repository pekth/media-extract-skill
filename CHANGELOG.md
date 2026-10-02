# Changelog

## Unreleased

- Extend CUDA fallback to transcription and lazy segment generation. Restart
  once on CPU INT8 and discard partial GPU results before emitting JSON.
- Add entry-point regressions for CPU and GPU success, CUDA failures at each
  inference stage, and CPU failure without partial JSON.
- Document fallback behavior and the limits of automated inference tests.
- Add a documentation gate to CI. It refreshes the document index and checks
  local inline Markdown file links without fetching external URLs.
