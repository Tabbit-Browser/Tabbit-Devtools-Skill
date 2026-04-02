# Tabbit Devtools Setup

This skill does not require any Tabbit code changes and does not require a dedicated custom MCP server for the default path.
The core trick is to read Tabbit's live `DevToolsActivePort` file and use the browser WebSocket endpoint written there.
Tabbit should be treated as a Chromium-based browser, but the recommended client is `agent-browser`, not `chrome-devtools` MCP.

`agent-browser` is the browser-operation layer in this setup. This skill only discovers the live Tabbit endpoint and forwards it into `agent-browser --cdp ...`.
On macOS, discovery first checks `~/Library/Application Support/Tabbit/DevToolsActivePort`, then `~/Library/Application Support/Tabbit Browser/DevToolsActivePort`.

## Lowest-Cost Path

This is the default path for the skill and has the lowest installation cost:

1. Install or symlink the skill folder.
2. In Tabbit, open `tabbit://inspect/#remote-debugging` and enable remote debugging.
3. Ensure `agent-browser` is runnable, either from PATH or through `npx`.
4. Use the bundled wrapper script:

```bash
python3 /path/to/Tabbit-Connector-Skill/skills/tabbit-devtools/scripts/run_agent_browser_on_tabbit.py snapshot -i
```

This path does not require:

- a dedicated `tabbit-devtools` MCP server
- modifying `chrome-devtools-mcp`
- a custom bridge or local CDP daemon

The wrapper discovers Tabbit's live `wsEndpoint` and then launches `agent-browser --cdp <wsEndpoint> ...`.
This keeps the Tabbit-specific logic at the connection layer while delegating browser actions to `agent-browser`.

## What The Helper Is For

Prefer the helper script for:

- surfacing Tabbit's DevTools connection details as JSON
- confirming the current `port`, `browserPath`, and `wsEndpoint`
- giving `agent-browser` the exact `wsEndpoint` it needs to connect to Tabbit

Once those details are known, page interaction should follow the normal `agent-browser` workflow.

Prefer this explicit flow for real work:

```bash
python3 /path/to/Tabbit-Connector-Skill/skills/tabbit-devtools/scripts/run_agent_browser_on_tabbit.py open https://www.baidu.com
python3 /path/to/Tabbit-Connector-Skill/skills/tabbit-devtools/scripts/run_agent_browser_on_tabbit.py snapshot -i
```

Common `agent-browser` actions in this setup:

- `open <url>`
- `snapshot -i`
- `click @e3`
- `fill @e5 <text>`
- `press Enter`

If the helper cannot find `DevToolsActivePort` in either the `Tabbit` or `Tabbit Browser` support directory, ask the user to confirm Tabbit is open and that `tabbit://inspect/#remote-debugging` is enabled.

If you only need the raw endpoint details, use `discover_tabbit_cdp.py` directly.
If you need to actually operate the browser, prefer `run_agent_browser_on_tabbit.py` so the `--cdp` wiring stays consistent.

## Important Behavior

- Tabbit may expose the browser WebSocket while `http://127.0.0.1:<port>/json/version` and `http://127.0.0.1:<port>/json/list` still return `404`.
- The helper script reads `DevToolsActivePort` directly and reports the browser WebSocket endpoint.
- The wrapper script injects that browser WebSocket endpoint into `agent-browser --cdp ...`.
- Do not assume `browserUrl` discovery will work unless you have confirmed that Tabbit exposes the standard HTTP DevTools discovery endpoints.
- Because Tabbit may return `404` on HTTP discovery, prefer the full browser WebSocket endpoint over passing only a port when possible.
- For the full `agent-browser` command set, refer to the upstream docs: https://github.com/vercel-labs/agent-browser
