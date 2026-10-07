# Allplan MCP Server

FastMCP server that exposes the local Allplan Python host as MCP tools.

The existing Allplan PythonPart starts a small local HTTP host at `127.0.0.1:5679`.
This package adds a FastMCP server in front of it, so agents can call MCP tools
over Streamable HTTP at `/mcp`.

## Windows / Codex evaluation

Version **0.1.2** prepares reproducible bridge installation and recovery, local Codex
configuration, read-only runtime diagnostics and a small acceptance batch. Allplan
baseline is **accepted on Allplan 2026-1-7** with local Windows Codex
(UAT-00/UAT-01 PASS). [M0 is closed](docs/test-results/m0-acceptance-0.1.2.md);
workflow toolkit capabilities begin with M1.

Current package **0.3.0** adds a bounded read-only `model_query`: explicit loaded
file/passive scope, type/layer/raw-attribute predicates, paginated session
selections and full-selection summaries with stale-read rejection. **24 relevant
portable checks pass; three bounded owner query cases PASS**.
[Contracts](docs/tool-reference.md), [portable evidence](docs/test-results/m1-query-portable-0.3.0.md)
and [small owner query batch](docs/m1-query-batch.md).
[0.3.0 runtime evidence and limits](docs/test-results/m1-query-runtime-0.3.0.md)
record scope, metadata, pages/full summary and observed-value predicates on two
native columns. Changed-source staleness and geometry remain separately pending.
The earlier **0.2.1 context correction batch remains PASS**; do not repeat it.
[Accepted context evidence](docs/test-results/m1-context-runtime-0.2.1.md).
Geometry/offset normalization, native component counting and demo profile binding
remain pending. The demonstration profile is unbound and inactive; M1 is not accepted.

- [Windows installation and restore](docs/windows-setup.md)
- [UAT-00 / UAT-01 prompts and result form](docs/m0-acceptance-batch.md)
- [Actual task status and evidence](docs/project-status.md)
- [Version history](docs/changelog.md)
- [Portable testing and package build](docs/testing.md)
- [Compatibility and limitations](docs/support-matrix.md)

End users use the versioned ZIP and its Explorer launchers. The following source
setup is for development.

## Setup

```bash
uv sync
```

Register the Allplan PythonPart bridge on the Windows machine where Allplan is
installed:

```cmd
utils\register_python_host.cmd
```

By default this copies the bridge to:

```text
%USERPROFILE%\Documents\Nemetschek\Allplan\2026\Usr\Local\Library\PythonHost
%USERPROFILE%\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonPartsScripts\PythonHost
```

For a different Allplan version:

```cmd
utils\register_python_host.cmd --allplan-version 2025
```

In Allplan, start the `StartPythonHost` PythonPart after registration. It must
keep running while the MCP server is being used.

## Run locally

```bash
uv run allplan-mcp
```

By default this starts the MCP server at:

```text
http://127.0.0.1:8888/mcp
```

Useful environment variables:

```bash
ALLPLAN_HOST_URL=http://127.0.0.1:5679
MCP_HOST=127.0.0.1
MCP_PORT=8888
MCP_PATH=/mcp
```

## Tools

- `allplan_health`: checks whether the Allplan host is reachable.
- `get_allplan_version`: returns the running Allplan version.
- `get_all_object_names`: returns display names for elements in the current document.
- `get_model_context`: bounded read-only context/identity probe; missing reads are explicit.
- `model_query`: typed read-only query/page/summary with explicit file scope; [contract and limits](docs/tool-reference.md).
- `create_cube`: creates a cube in the current document.
- `create_box`: creates a rectangular cuboid in the current document.
- `execute_python`: optional development tool, registered only when
  `ALLPLAN_MCP_ENABLE_PYTHON_EXEC=1`; the Allplan process must also opt in.

## Skill resources

Bundled skills are also exposed through MCP resources so clients can discover and read
them through the protocol.

Simple folder layout:

```text
src/allplan_mcp/allplan_skills/
  api-reference/
    SKILL.md
    assets/
    scripts/
  geometry/
    SKILL.md
    assets/
    scripts/
  rebar/
    SKILL.md
    assets/
    scripts/
  utilities/
    SKILL.md
    assets/
    scripts/
```

Resource URIs:

- `allplan://skills`
- `allplan://skills/api-reference`
- `allplan://skills/geometry`
- `allplan://skills/rebar`
- `allplan://skills/utilities`
- `allplan://skills/{skill_name}/assets/{asset_name}`
- `allplan://skills/{skill_name}/scripts/{script_name}`

The scripts are simple templates. They are meant to guide generated code and do not
depend on cross imports between skill folders.

## Notes

- [POST execution exploration](docs/post-execution-exploration.md)

## Development roadmap

The Allplan 2026 workflow toolkit is planned incrementally, starting with native
model queries, audits, and controlled cleanup through Codex. The following are
planning artifacts; they do not describe already implemented tools:

- [Implementation plan](docs/implementation-plan.md)
- [Next-model handoff](docs/next-model-handoff.md)
- [Demo profile and owner-built model](docs/demo-model-and-profile.md)
- [Manual acceptance tests](docs/manual-acceptance-tests.md)

## Development execution

Python execution is disabled by default on the host and omitted from the MCP tool
catalog. The evaluation launcher explicitly disables it. Developers may opt in
separately in the Allplan process and MCP process for local experiments.

Behavior:

- With the host opt-in, the raw Allplan bridge accepts `POST /execute-python`
- With the MCP opt-in, the external server exposes `execute_python(...)`
- The endpoint remains bound to `127.0.0.1`
- Imports are blocked by AST validation
- Private and dunder attribute access is blocked by AST validation
- Only a restricted builtin whitelist is available at runtime

AST filtering is not a process isolation boundary. It grants access to live
Allplan API objects. Do not expose this development path through a tunnel or a
shared agent setup. Production workflows use typed handlers. See the
[execution boundary](docs/post-execution-exploration.md).
