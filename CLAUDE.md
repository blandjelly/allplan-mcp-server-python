@AGENTS.md

# Claude Code notes

The instructions imported above apply unchanged to Claude Code. Wherever the
project documents say **Codex**, read **the coding agent in use** (Codex or
Claude Code); the responsibility split with the owner and GitHub Actions is the
same.

- Cloud sessions (claude.ai/code) have no Windows, Allplan or access to
  `127.0.0.1:8888`; they can analyse, implement, run focused tests and push.
  Native Allplan trials are run by the owner on Windows.
- Run focused tests with `uv run --frozen python -m unittest tests.<module> -v`
  (full CI runs the same `discover -s tests` modules through
  `utils/run_tests_parallel.py`); choose
  modules according to [the testing policy](docs/testing-policy.md).
- Without an explicit owner request, do not subscribe to PR activity to wait
  for CI, download artifacts, rerun CI or merge (see the testing policy).
- Connecting Claude Code to the MCP server on Windows is described in
  [Windows setup](docs/windows-setup.md#claude-code).
