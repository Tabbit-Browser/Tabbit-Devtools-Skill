#!/usr/bin/env python3

import argparse
import json
import os
import pathlib
import sys
import time
from typing import Any, Dict, List, Sequence

DEFAULT_WAIT_SECONDS = 0.0
DEFAULT_POLL_INTERVAL_SECONDS = 0.25


def default_active_port_files() -> List[pathlib.Path]:
    base = pathlib.Path.home() / "Library" / "Application Support"
    candidates = [
        base / "Tabbit" / "DevToolsActivePort",
        base / "Tabbit Browser" / "DevToolsActivePort",
    ]

    # Windows paths
    localappdata = os.environ.get("LOCALAPPDATA")
    appdata = os.environ.get("APPDATA")
    if localappdata:
        candidates.append(pathlib.Path(localappdata) / "Tabbit Browser" / "User Data" / "DevToolsActivePort")
    if appdata:
        candidates.append(pathlib.Path(appdata) / "Tabbit" / "User Data" / "DevToolsActivePort")

    return candidates


def default_active_port_file() -> pathlib.Path:
    return default_active_port_files()[0]


def resolve_active_port_file_candidates(active_port_file_arg: str) -> List[pathlib.Path]:
    if active_port_file_arg:
        return [pathlib.Path(active_port_file_arg)]
    return default_active_port_files()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover Tabbit's Chromium DevTools endpoint so agent-browser can connect to it."
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
    return parser.parse_args()


def wait_for_active_port_file_candidates(
    file_paths: Sequence[pathlib.Path], wait_seconds: float, poll_interval_seconds: float
) -> pathlib.Path:
    deadline = time.monotonic() + max(wait_seconds, 0.0)

    while True:
        for file_path in file_paths:
            if file_path.exists():
                return file_path
        if time.monotonic() >= deadline:
            searched = ", ".join(str(path) for path in file_paths)
            raise RuntimeError(
                f"DevToolsActivePort not found. Searched: {searched}. "
                "Treat this as Tabbit Browser not being available here, and ask the user to open Tabbit and enable remote debugging at tabbit://inspect/#remote-debugging."
            )
        time.sleep(max(poll_interval_seconds, 0.05))


def read_active_port_file(file_path: pathlib.Path) -> Dict[str, Any]:
    raw = file_path.read_text(encoding="utf-8")
    parts = [line.strip() for line in raw.splitlines() if line.strip()]
    if len(parts) < 2:
        raise RuntimeError(f"Invalid DevToolsActivePort file: {file_path}")

    port = int(parts[0])
    browser_path = parts[1]

    return {
        "activePortFile": str(file_path),
        "port": port,
        "browserPath": browser_path,
        "browserUrl": f"http://127.0.0.1:{port}",
        "wsEndpoint": f"ws://127.0.0.1:{port}{browser_path}",
    }


def build_notes() -> List[str]:
    return [
        "Tabbit is a Chromium-based browser.",
        "This helper only discovers connection details for Tabbit.",
        "Prefer agent-browser with the reported wsEndpoint instead of relying on HTTP-based CDP discovery.",
        "Use scripts/run_agent_browser_on_tabbit.py to inject the wsEndpoint into agent-browser automatically.",
        "Avoid building a custom bridge or a parallel daemon just to control Tabbit.",
        "Tabbit may expose the browser WebSocket even when /json/version or /json/list return 404.",
    ]


def main() -> int:
    args = parse_args()
    active_port_file = wait_for_active_port_file_candidates(
        resolve_active_port_file_candidates(args.active_port_file),
        args.wait_seconds,
        args.poll_interval_seconds,
    )

    result = read_active_port_file(active_port_file)
    result.update(
        {
            "browserName": "Tabbit",
            "browserFamily": "Chromium",
            "preferredClient": "agent-browser",
            "agentBrowserCdpArgs": ["--cdp", result["wsEndpoint"]],
            "notes": build_notes(),
        }
    )

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        sys.stderr.write(f"[tabbit-devtools] {error}\n")
        raise SystemExit(1)
