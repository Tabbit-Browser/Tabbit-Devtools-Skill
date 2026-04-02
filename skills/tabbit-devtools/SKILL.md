---
name: tabbit-devtools
description: Use Tabbit with agent-browser by reading Tabbit's live DevToolsActivePort file, deriving the browser wsEndpoint, and routing browser actions through agent-browser --cdp.
---

# Tabbit Devtools

Prefer this skill whenever the request is explicitly about Tabbit or includes phrases like `用我的 tabbit 浏览器`, `在 Tabbit 里`, `Tabbit 当前页`, or `Tabbit 当前标签`.

Treat Tabbit as a Chromium-based browser.
This skill is about how to connect `agent-browser` to Tabbit.
After the connection is established, handle browser automation and inspection through the normal `agent-browser` workflow.
Do not implement a parallel browser automation layer, bridge daemon, or custom CDP client inside this skill.

## agent-browser Quick Reference

Treat `agent-browser` as the browser-operation layer after Tabbit endpoint discovery.

The most relevant commands for this skill are:

- `open <url>`
- `snapshot -i`
- `click @e3`
- `fill @e5 <text>`
- `press Enter`

Do not restate a full `agent-browser` manual here. Use these commands as the default vocabulary for Tabbit tasks, and prefer the official README for any broader command surface.

## Quick Path

1. Read `~/Library/Application Support/Tabbit/DevToolsActivePort` first.
2. If that file does not exist, read `~/Library/Application Support/Tabbit Browser/DevToolsActivePort`.
3. Use both lines in that file:
   - line 1: TCP port
   - line 2: browser path such as `/devtools/browser/<id>`
4. Build the full browser endpoint as `ws://127.0.0.1:<port><path>`.
5. Prefer that `wsEndpoint` over `http://127.0.0.1:<port>`. Tabbit may expose the browser WebSocket while `/json/version` and `/json/list` still return `404`.
6. Prefer [scripts/run_agent_browser_on_tabbit.py](scripts/run_agent_browser_on_tabbit.py) for actual browser actions. It injects the live `wsEndpoint` into `agent-browser --cdp ...`.
7. Use [scripts/discover_tabbit_cdp.py](scripts/discover_tabbit_cdp.py) when you only need structured connection facts.
8. Once connected, use the full normal `agent-browser` workflow for page operations.

## Workflow

1. For Tabbit requests, start by reading `DevToolsActivePort` directly or by running [scripts/discover_tabbit_cdp.py](scripts/discover_tabbit_cdp.py).
2. Return the connection facts the agent actually needs: `activePortFile`, `port`, `browserPath`, `browserUrl`, and `wsEndpoint`.
3. Unless the user explicitly asks only for endpoint details, prefer [scripts/run_agent_browser_on_tabbit.py](scripts/run_agent_browser_on_tabbit.py) immediately so the command becomes `agent-browser --cdp <wsEndpoint> ...`.
4. After that handoff, follow the normal `agent-browser` workflow for open, snapshot, click, fill, and other browser commands.
5. If `agent-browser` is unavailable, say so plainly and surface the connection facts instead of inventing a custom CDP bridge.

## Guidance

- This skill solves the connection problem, not the general browser-operation problem.
- Return structured connection data first, then any short explanatory note.
- Prefer the lightest possible discovery path: `DevToolsActivePort` and the derived browser WebSocket endpoint.
- Search the macOS `Tabbit` support directory first, then `Tabbit Browser`.
- Prefer the full `wsEndpoint` over a raw port because Tabbit may not expose HTTP discovery routes.
- Once a Tabbit task has started through `run_agent_browser_on_tabbit.py`, keep using that same wrapper path for the rest of the task unless the user explicitly asks otherwise.
- Once connected, use standard `agent-browser` patterns for everything else.

## Constraints

- Do not assume a dedicated `tabbit-devtools` MCP server exists.
- Do not assume the generic `chrome-devtools` session can be retargeted to Tabbit.
- Do not turn this skill into a replacement for `agent-browser`.
- Do not create a custom daemon, long-lived CDP proxy, or one-off WebSocket client for post-connection browser actions.
- Do not promise that `chrome-devtools` MCP will automatically take over Tabbit.
- If `agent-browser` cannot be launched in the current environment, stop at connection guidance and explain the limitation.
- After connection, the browser workflow belongs to `agent-browser`, not to this skill.

## Resources

- Setup and direct-connection notes: [references/setup.md](references/setup.md)
- Endpoint discovery rules and environment variables: [references/discovery.md](references/discovery.md)
- Endpoint discovery helper: [scripts/discover_tabbit_cdp.py](scripts/discover_tabbit_cdp.py)
- agent-browser wrapper: [scripts/run_agent_browser_on_tabbit.py](scripts/run_agent_browser_on_tabbit.py)
- agent-browser upstream docs: https://github.com/vercel-labs/agent-browser
