#!/usr/bin/env python3

import argparse
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
from typing import List, Sequence, Tuple

from discover_tabbit_cdp import (
    DEFAULT_POLL_INTERVAL_SECONDS,
    DEFAULT_WAIT_SECONDS,
    read_active_port_file,
    resolve_active_port_file_candidates,
    wait_for_active_port_file_candidates,
)


def parse_args(argv: Sequence[str]) -> Tuple[argparse.Namespace, List[str]]:
    parser = argparse.ArgumentParser(
        description="Run agent-browser against the current Tabbit instance by injecting Tabbit's live CDP wsEndpoint."
    )
    parser.add_argument(
        "--active-port-file",
        default=os.environ.get("TABBIT_DEVTOOLS_ACTIVE_PORT_FILE", ""),
        help="Path to Tabbit DevToolsActivePort. If omitted, search Tabbit first, then Tabbit Browser.",
    )
    parser.add_argument(
        "--wait-seconds",
        default=float(os.environ.get("TABBIT_DISCOVERY_WAIT_SECONDS", str(DEFAULT_WAIT_SECONDS))),
        type=float,
        help="Wait up to this many seconds for DevToolsActivePort to appear",
    )
    parser.add_argument(
        "--poll-interval-seconds",
        default=float(os.environ.get("TABBIT_DISCOVERY_POLL_INTERVAL_SECONDS", str(DEFAULT_POLL_INTERVAL_SECONDS))),
        type=float,
        help="Polling interval used while waiting for DevToolsActivePort",
    )
    parser.add_argument(
        "--agent-browser-bin",
        default=os.environ.get("AGENT_BROWSER_BIN", ""),
        help="Command used to launch agent-browser, for example 'agent-browser' or 'npx --yes agent-browser'",
    )
    parser.add_argument(
        "--print-command",
        action="store_true",
        help="Print the resolved agent-browser command instead of executing it",
    )
    args, remaining = parser.parse_known_args(argv)
    if remaining[:1] == ["--"]:
        remaining = remaining[1:]
    return args, remaining


def resolve_agent_browser_command(configured_command: str) -> List[str]:
    if configured_command.strip():
        return shlex.split(configured_command)

    if shutil.which("agent-browser"):
        return ["agent-browser"]

    if shutil.which("npx"):
        return ["npx", "--yes", "agent-browser"]

    raise RuntimeError(
        "agent-browser is not available. Install it, or set AGENT_BROWSER_BIN to a runnable command."
    )


def build_command(base_command: Sequence[str], ws_endpoint: str, agent_browser_args: Sequence[str]) -> List[str]:
    if not agent_browser_args:
        raise RuntimeError(
            "Missing agent-browser arguments. Example: snapshot -i, open https://example.com, or click @e3."
        )

    return [*base_command, "--cdp", ws_endpoint, *agent_browser_args]


def main(argv: Sequence[str]) -> int:
    args, agent_browser_args = parse_args(argv)
    active_port_file = wait_for_active_port_file_candidates(
        resolve_active_port_file_candidates(args.active_port_file),
        args.wait_seconds,
        args.poll_interval_seconds,
    )
    discovery = read_active_port_file(active_port_file)
    command = build_command(
        resolve_agent_browser_command(args.agent_browser_bin),
        discovery["wsEndpoint"],
        agent_browser_args,
    )

    if args.print_command:
        sys.stdout.write(shlex.join(command) + "\n")
        return 0

    completed = subprocess.run(command)
    return completed.returncode


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as error:
        sys.stderr.write(f"[tabbit-devtools] {error}\n")
        raise SystemExit(1)
