# Tabbit Agent-Browser Skill

[![English](https://img.shields.io/badge/Language-English-lightgrey)](./README.md)
[![简体中文](https://img.shields.io/badge/语言-简体中文-blue)](./README.zh-CN.md)

一个给支持 Skills 的 agent 使用的 Tabbit 浏览器 skill。

- `Tabbit` 是一个基于 Chromium 的浏览器。
- 这个 skill 的核心职责是指导 agent 找到 Tabbit 的 DevTools / CDP 端点，并把浏览器操作切到 `agent-browser`。
- 它不再承诺 `chrome-devtools` MCP 会自动重定向到 Tabbit。
- 一旦连接建立，后续页面打开、导航、点击、执行脚本、抓取内容等操作，都应按 `agent-browser` 的常规方式进行。
- 在用户提到“用我的 tabbit 浏览器”“在 Tabbit 里”“Tabbit 当前页/当前标签”时触发。
- 它会按顺序读取 `Tabbit` 和 `Tabbit Browser` 目录下的 `DevToolsActivePort`。
- 它会输出 Tabbit 当前开启的 DevTools WebSocket 连接信息，并用 `agent-browser --cdp <wsEndpoint>` 驱动当前 Tabbit。

## 前置条件

- 本机已安装 `python3`
- 本机已安装 `node` / `npx`，或者已经能直接运行 `agent-browser`
- 已安装并打开 `Tabbit`
- 已在 Tabbit 中开启 `tabbit://inspect/#remote-debugging`

## 用 `npx skills add` 安装

推荐：

```bash
npx skills add Tabbit-Browser/Tabbit-Devtools-Skill
```

只安装这个 skill：

```bash
npx skills add Tabbit-Browser/Tabbit-Devtools-Skill --skill tabbit-devtools
```

安装完成后，重启 agent 最稳。

## 推荐一起安装 `agent-browser`

如果你的 agent host 支持 skills，建议一并安装官方 `agent-browser` skill：

```bash
npx skills add vercel-labs/agent-browser
```

即使没有额外安装 skill，只要本机能运行 `agent-browser` 或 `npx agent-browser`，这个仓库里的 wrapper 也可以直接调起它。

如果你的环境里 `agent-browser` 不是这个名字，可以设置：

```bash
export AGENT_BROWSER_BIN="你的 agent-browser 启动命令"
```

例如：

```bash
export AGENT_BROWSER_BIN="npx --yes agent-browser"
```

## `agent-browser` 是什么

`agent-browser` 是一个给 agent 使用的浏览器自动化 CLI。

在这个仓库里，它的职责很简单：

- 这个 skill 负责找到 Tabbit 当前可用的 `wsEndpoint`
- wrapper 负责把 `--cdp <wsEndpoint>` 注入给 `agent-browser`
- 真正的页面操作由 `agent-browser` 执行

如果你想看更完整的命令和能力范围，以官方 README 为准：

- GitHub: [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser)
- 常见 agent 工作流: [Usage with AI Agents](https://github.com/vercel-labs/agent-browser#usage-with-ai-agents)

## 在 Codex 里安装

在 Codex 对话里：

```text
$skill-installer install https://github.com/Tabbit-Browser/Tabbit-Devtools-Skill/tree/main/skills/tabbit-devtools
```

或者：

```text
$skill-installer install-skill-from-github --repo Tabbit-Browser/Tabbit-Devtools-Skill --path skills/tabbit-devtools
```

如果你想在终端里安装：

```bash
mkdir -p ~/.agents/skills
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/Tabbit-Browser/Tabbit-Devtools-Skill/tree/main/skills/tabbit-devtools \
  --dest ~/.agents/skills
```

## 手动安装

```bash
mkdir -p ~/.agents/skills
ln -sfn /path/to/Tabbit-Devtools-Skill/skills/tabbit-devtools ~/.agents/skills/tabbit-devtools
```

安装完成后，重启 agent。

## 使用方式

这个 skill 更像是 “connect Tabbit through a Chromium-compatible DevTools endpoint and hand control to agent-browser” 的说明层。

它负责告诉 agent：

- 按顺序去哪里找 `DevToolsActivePort`
- 怎么得到 Tabbit 的 `port` 和 `wsEndpoint`
- 怎么把后续工作切到 `agent-browser`

它不自己实现桥接层，也不自己实现浏览器自动化逻辑；真正的页面操作交给 `agent-browser`。

默认搜索顺序是：

- `~/Library/Application Support/Tabbit/DevToolsActivePort`（macOS）
- `~/Library/Application Support/Tabbit Browser/DevToolsActivePort`（macOS）
- `%LOCALAPPDATA%\Tabbit Browser\User Data\DevToolsActivePort`（Windows）
- `%APPDATA%\Tabbit\User Data\DevToolsActivePort`（Windows）

只有以上位置都不存在时，才会认为当前环境缺少可用的 Tabbit 浏览器。

## 开源协议

本仓库使用 [MIT License](./LICENSE)。
