---
title: "Connect your AI agent to Task Node"
type: "blog"
url: "/agents/"
date: 2026-10-02
summary: "Use Task Node from Claude Code, Codex, Hermes, Pi, OpenCode, Kilo or any MCP client. Your agent can read your tasks, submit evidence, answer verification requests and ask Task Node chat."
breadcrumb_label: "Task Node"
breadcrumb_url: "/task-node/"
show_toc: false
---

Task Node is a remote [MCP](https://modelcontextprotocol.io) server. Once your agent is connected, it can list and accept tasks, submit evidence, answer verification requests, request new tasks, read and edit your context document, ask Task Node chat, and check your PFT balance and rewards. It follows the same rules and limits as the web app.

## Before you start

- A Task Node account with GitHub linked. In [Task Node](https://tasknode.postfiat.org), open Settings → Accounts and link GitHub.
- An agent: Claude Code, Codex, Hermes, Pi, OpenCode, Kilo, or any client that supports remote MCP servers.

## Connect in one paste

1. Open [tasknode.postfiat.org/connect](https://tasknode.postfiat.org/connect) and sign in with GitHub.
2. Click **Create token**.
3. Click the command for your agent to select it, copy it, and paste it into the terminal where the agent runs. This also works when the agent runs on a remote server over SSH.
4. Start (or restart) the agent and ask: "What are my outstanding Task Node tasks?"

The token is shown once. Anyone who has it can act as you in Task Node, so don't share it or commit it.

## Supported agents

- **Claude Code, Codex, Hermes, Pi and OpenCode.** The connect page shows a ready command for each.
- **Kilo.** Use the OpenCode command with `kilo` in place of `opencode`.
- **Any other MCP client** (Cursor, Gemini CLI and others). Add a remote HTTP server with the URL `https://tasknode.postfiat.org/mcp` and the header `Authorization: Bearer <your token>`. Both are shown on the connect page.

If the agent runs on the same computer as your browser, Claude Code and Codex can sign in through the browser instead of using a token:

```
claude mcp add --scope user --transport http tasknode https://tasknode.postfiat.org/mcp
codex mcp add tasknode --url https://tasknode.postfiat.org/mcp
codex mcp login tasknode
```

In Claude Code, run `/mcp` afterwards and choose to authenticate.

## Things to ask

- "What are my outstanding Task Node tasks?"
- "Accept the PR review task and do it."
- "Answer the verification request on my last task with the test output."
- "Ask Task Node chat which task I should do next."
- "Add this decision to my Task Node context document."

## Switch accounts or sign out

Each agent setup holds one Task Node account. To switch, change to the other account in Task Node (it needs its own linked GitHub account), open the connect page, create a token, and paste the new command. It replaces the old account.

To sign out, click **Sign out all agents** on the connect page. This revokes every agent and Corbanu Terminal token for the account. Then remove the entry from each agent, for example `codex mcp remove tasknode`, `claude mcp remove --scope user tasknode`, `hermes mcp remove tasknode` or `pi mcp remove tasknode`.

## Several accounts on one computer

- **Codex.** Give each extra account its own Codex home that shares your OpenAI sign-in:

  ```
  mkdir -p ~/.codex-work && ln -s ~/.codex/auth.json ~/.codex-work/auth.json
  export CODEX_HOME=~/.codex-work
  ```

  Paste that account's connect command in the same terminal. From then on, start that account's sessions with `CODEX_HOME=~/.codex-work codex`.
- **Claude Code.** In the folder where the other account should apply, paste its connect command with `--scope user` changed to `--scope local` (in both places). Claude Code uses that account only in that folder.

## Troubleshooting

- **Unauthorized (401).** The token was revoked or copied incompletely. Create a new token and paste the command again.
- **Asked to link GitHub.** Link GitHub to your Task Node account, then reopen the connect page. Signing in with a GitHub account that isn't linked creates a separate, empty account.
- **The agent doesn't show Task Node tools.** Restart the agent. In a running session, use `/reload-mcp` in Hermes or `/reload` in Pi.
- **Pi won't start.** Pi needs Node.js 22.19 or later.
