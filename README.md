# Tabbit Agent-Browser Skill

[![English](https://img.shields.io/badge/Language-English-blue)](./README.md)
[![简体中文](https://img.shields.io/badge/语言-简体中文-lightgrey)](./README.zh-CN.md)

A Tabbit browser skill for agents that support Skills.

- `Tabbit` is a Chromium-based browser.
- This skill helps an agent discover Tabbit's DevTools / CDP endpoint and hand browser control to `agent-browser`.
- It does not promise that `chrome-devtools` MCP will be automatically retargeted to Tabbit.
- Once connected, page opening, navigation, clicking, script execution, and extraction should follow the normal `agent-browser` workflow.
- It searches for `DevToolsActivePort` in `Tabbit` first and `Tabbit Browser` second.
- It outputs the live DevTools WebSocket details and drives the current Tabbit instance through `agent-browser --cdp <wsEndpoint>`.

## Prerequisites

- `python3` is installed locally
- `node` / `npx` is installed locally, or `agent-browser` is already runnable
- `Tabbit` is installed and open
- Remote debugging is enabled in `tabbit://inspect/#remote-debugging`

## Install with `npx skills add`

Recommended:

```bash
npx skills add Tabbit-Browser/Tabbit-Devtools-Skill
```

Install only this skill:

```bash
npx skills add Tabbit-Browser/Tabbit-Devtools-Skill --skill tabbit-devtools
```

Restarting the agent after installation is the safest option.

## Recommended: install `agent-browser` too

If your agent host supports skills, install the official `agent-browser` skill as well:

```bash
npx skills add vercel-labs/agent-browser
```

Even without the extra skill, the wrapper in this repo can launch it as long as `agent-browser` or `npx agent-browser` is available locally.

If your environment uses a different command name, set:

```bash
export AGENT_BROWSER_BIN="your agent-browser launch command"
```

For example:

```bash
export AGENT_BROWSER_BIN="npx --yes agent-browser"
```

## What is `agent-browser`

`agent-browser` is a browser automation CLI for agents.

Its role in this repository is simple:

- this skill discovers the currently available Tabbit `wsEndpoint`
- the wrapper injects `--cdp <wsEndpoint>` into `agent-browser`
- actual page operations are executed by `agent-browser`

For the full command surface, refer to the official README:

- GitHub: [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)
- Common agent workflow: [Usage with AI Agents](https://github.com/vercel-labs/agent-browser#usage-with-ai-agents)

## Install in Codex

In a Codex conversation:

```text
$skill-installer install https://github.com/Tabbit-Browser/Tabbit-Devtools-Skill/tree/main/skills/tabbit-devtools
```

Or:

```text
$skill-installer install-skill-from-github --repo Tabbit-Browser/Tabbit-Devtools-Skill --path skills/tabbit-devtools
```

If you want to install from a terminal:

```bash
mkdir -p ~/.agents/skills
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/Tabbit-Browser/Tabbit-Devtools-Skill/tree/main/skills/tabbit-devtools \
  --dest ~/.agents/skills
```

## Manual install

```bash
mkdir -p ~/.agents/skills
ln -sfn /path/to/Tabbit-Devtools-Skill/skills/tabbit-devtools ~/.agents/skills/tabbit-devtools
```

Restart the agent after installation.

## How it works

This skill is best understood as a "connect Tabbit through a Chromium-compatible DevTools endpoint and hand control to agent-browser" layer.

It tells the agent:

- where to look for `DevToolsActivePort`
- how to derive Tabbit's `port` and `wsEndpoint`
- how to hand the rest of the work to `agent-browser`

It does not implement its own bridge or browser automation layer. Actual page operations belong to `agent-browser`.

The default search order is:

- `~/Library/Application Support/Tabbit/DevToolsActivePort` (macOS)
- `~/Library/Application Support/Tabbit Browser/DevToolsActivePort` (macOS)
- `%LOCALAPPDATA%\Tabbit Browser\User Data\DevToolsActivePort` (Windows)
- `%APPDATA%\Tabbit\User Data\DevToolsActivePort` (Windows)

Only when none of these locations exist should the environment be treated as missing a usable Tabbit browser.

## License

This repository is released under the [MIT License](./LICENSE).
