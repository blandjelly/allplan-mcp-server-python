"""Explorer-launched setup actions; no owner code editing or test commands."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "utils"))
from register_python_host import default_allplan_local, register, restore, verify_package

MCP_URL = "http://127.0.0.1:8888/mcp"


def connect_codex(config: Path) -> dict:
    """Add only our server table, retaining every existing Codex setting."""
    original = config.read_text(encoding="utf-8") if config.exists() else ""
    parsed = tomllib.loads(original)
    existing = parsed.get("mcp_servers", {}).get("allplan_m0")
    if existing is not None:
        if existing.get("url") != MCP_URL or existing.get("enabled") is False:
            raise ValueError("Codex already has an allplan_m0 server at another URL. Report this configuration conflict; it has not been overwritten.")
        return {"status": "already_configured", "config": str(config)}
    backup = None
    config.parent.mkdir(parents=True, exist_ok=True)
    if config.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = config.with_name(f"config.toml.allplan-backup-{stamp}")
        shutil.copy2(config, backup)
    updated = original + '\n[mcp_servers.allplan_m0]\nurl = "' + MCP_URL + '"\n'
    tomllib.loads(updated)  # Validate before replacing the owner's settings.
    staged = config.with_name("config.toml.allplan-stage")
    staged.write_text(updated, encoding="utf-8")
    staged.replace(config)
    return {"status": "configured", "config": str(config), "backup": str(backup) if backup else None}


CLAUDE_SERVER = "allplan"


def connect_claude(run=subprocess.run, which=shutil.which) -> dict:
    """Register the loopback endpoint for Claude Code through its own CLI.

    Claude Code owns its configuration format, so this never edits its files.
    An existing server with this name at another URL is reported, not replaced.
    """
    executable = which("claude")
    manual = f"claude mcp add --transport http --scope user {CLAUDE_SERVER} {MCP_URL}"
    if executable is None:
        raise ValueError(f"Claude Code CLI (claude) was not found on PATH. Install Claude Code or run manually: {manual}")
    def call(*args):
        return run([executable, "mcp", *args], capture_output=True, text=True, timeout=60)
    existing = call("get", CLAUDE_SERVER)
    if existing.returncode == 0:
        if MCP_URL in (existing.stdout or ""):
            return {"status": "already_configured", "server": CLAUDE_SERVER, "url": MCP_URL}
        raise ValueError(f"Claude Code already has an MCP server named {CLAUDE_SERVER} with another configuration. Report this conflict; it has not been overwritten.")
    added = call("add", "--transport", "http", "--scope", "user", CLAUDE_SERVER, MCP_URL)
    if added.returncode != 0:
        raise ValueError(f"claude mcp add failed ({added.returncode}): {(added.stderr or added.stdout or '').strip()[:500]}")
    return {"status": "configured", "server": CLAUDE_SERVER, "url": MCP_URL, "scope": "user"}


def choose_local() -> Path:
    from tkinter import Tk, filedialog
    window = Tk()
    window.withdraw()
    default = default_allplan_local("2026")
    chosen = filedialog.askdirectory(title="Select the actual Allplan user Local folder (see Allmenu)",
                                    initialdir=str(default if default.exists() else Path.home()), mustexist=True)
    window.destroy()
    if not chosen:
        raise ValueError("No Allplan folder selected; installation was not changed.")
    return Path(chosen)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["verify", "install", "restore", "connect", "connect-claude"])
    args = parser.parse_args()
    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    try:
        if args.action == "verify":
            result = verify_package(ROOT)
        elif args.action == "install":
            verify_package(ROOT)
            input("Close Allplan, then press Enter to choose its user Local folder: ")
            result = register(ROOT, choose_local())
            (logs / "installation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        elif args.action == "restore":
            input("Close Allplan, then press Enter to restore the previous bridge: ")
            installation = json.loads((logs / "installation.json").read_text(encoding="utf-8"))
            result = restore(Path(installation["allplan_local"]), installation["backup_id"])
        elif args.action == "connect-claude":
            verify_package(ROOT)
            result = connect_claude()
            print("Open this folder in Claude Code and check /mcp. Launch Allplan MCP.cmd must stay open.")
        else:
            verify_package(ROOT)
            result = connect_codex(Path.home() / ".codex/config.toml")
            print("Restart Codex on this Windows machine. Launch Allplan MCP.cmd must stay open.")
        (logs / f"{args.action}-result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"{args.action.capitalize()} failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
