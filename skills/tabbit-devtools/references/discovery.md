# Tabbit Endpoint Discovery

Tabbit is a Chromium-based browser. This note focuses on endpoint discovery so that `agent-browser` can be pointed at Tabbit afterward.

The lightweight helper script tries the following sources in order:

1. `TABBIT_DEVTOOLS_ACTIVE_PORT_FILE`
2. macOS default path `~/Library/Application Support/Tabbit/DevToolsActivePort`
3. macOS mainland build path `~/Library/Application Support/Tabbit Browser/DevToolsActivePort`
4. Windows user path `%LOCALAPPDATA%\Tabbit Browser\User Data\DevToolsActivePort`
5. Windows roaming path `%APPDATA%\Tabbit\User Data\DevToolsActivePort`

For real Tabbit instances, `DevToolsActivePort` is the most reliable path. The helper script reads it directly and does not rely on `/json/version`.

## Supported environment variables

- `TABBIT_DEVTOOLS_ACTIVE_PORT_FILE`
  Absolute path to a `DevToolsActivePort` file.
- `TABBIT_DISCOVERY_WAIT_SECONDS`
  Override how long the discovery helper waits for `DevToolsActivePort` to appear.
- `TABBIT_DISCOVERY_POLL_INTERVAL_SECONDS`
  Override the polling interval used by the discovery helper.

## Discovery notes

- On macOS, the default search order is `~/Library/Application Support/Tabbit/DevToolsActivePort` first, then `~/Library/Application Support/Tabbit Browser/DevToolsActivePort`.
- On Windows, the default search order is `%LOCALAPPDATA%\Tabbit Browser\User Data\DevToolsActivePort` first, then `%APPDATA%\Tabbit\User Data\DevToolsActivePort`.
- Read both lines from `DevToolsActivePort`: the port and the `/devtools/browser/<id>` path.
- The helper script is intentionally simple and optimized for the lowest-install-cost path.
- Prefer the full `wsEndpoint` over the raw port because Tabbit may not expose the standard HTTP discovery routes.
- The bundled `run_agent_browser_on_tabbit.py` wrapper uses that `wsEndpoint` to launch `agent-browser --cdp ...`.
- This skill should not create its own CDP proxy or bridge daemon just to automate Tabbit.
