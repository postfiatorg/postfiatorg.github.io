---
title: "Connect your AI agent to Task Node"
type: "blog"
url: "/agents/"
date: 2026-10-02
summary: "Use Task Node from Claude Code, Codex, Hermes, Pi, OpenCode, Kilo, Claude, ChatGPT, Cursor, Gemini CLI or your own app. Your agent can read your tasks, do the work, submit evidence, answer verification requests and ask Task Node chat."
breadcrumb_label: "Task Node"
breadcrumb_url: "/task-node/"
---

Task Node is a remote [MCP](https://modelcontextprotocol.io) server at `https://tasknode.postfiat.org/mcp`. Connect your agent once and it can find your tasks, accept them, do the work, submit evidence, answer verification questions, request new tasks, keep your context document up to date, ask Task Node chat, and check your PFT balance. It follows the same rules and limits as the web app.

## Before you start

1. A Task Node account with **GitHub linked**. In [Task Node](https://tasknode.postfiat.org), open Settings → Accounts and link GitHub. Signing in with a GitHub account that isn't linked creates a separate, empty Task Node account.
2. An agent from the list below, or any client that supports remote MCP servers.

## Two ways to sign in

- **Token (works everywhere, including over SSH).** Open [tasknode.postfiat.org/connect](https://tasknode.postfiat.org/connect), sign in with GitHub and click **Create token**. The page shows a ready-to-paste command for Codex, Claude Code, Hermes, Pi and OpenCode. Click one, copy it, paste it into the terminal where the agent runs, then restart the agent. The token is shown once and does not expire. Anyone who has it can act as you, so treat it like a password.
- **Browser sign-in (OAuth).** When the agent runs on the same computer as your browser, it can sign in through GitHub instead. Claude Code, Codex, Claude Desktop, claude.ai and ChatGPT support this.

In the commands below, replace `<TOKEN>` with your token. The connect page fills it in for you.

## Claude Code

With a token:

```
claude mcp add --scope user --transport http tasknode https://tasknode.postfiat.org/mcp \
  --header "Authorization: Bearer <TOKEN>"
```

With browser sign-in:

```
claude mcp add --scope user --transport http tasknode https://tasknode.postfiat.org/mcp
```

Then run `/mcp` inside Claude Code and choose to authenticate.

## Codex (OpenAI)

With a token, add this to `~/.codex/config.toml` (or `$CODEX_HOME/config.toml`). The connect page gives you a single command that does it:

```toml
[mcp_servers.tasknode]
url = "https://tasknode.postfiat.org/mcp"
http_headers = { Authorization = "Bearer <TOKEN>" }
```

With browser sign-in:

```
codex mcp add tasknode --url https://tasknode.postfiat.org/mcp
codex mcp login tasknode
```

## Hermes

```
hermes config set MCP_TASKNODE_API_KEY <TOKEN>
hermes config set --force mcp_servers.tasknode.url https://tasknode.postfiat.org/mcp
hermes config set --force mcp_servers.tasknode.headers.Authorization 'Bearer ${MCP_TASKNODE_API_KEY}'
```

Keep the single quotes on the last line: Hermes resolves `${MCP_TASKNODE_API_KEY}` itself. In a running session, `/reload-mcp` picks up the change.

## Pi

```
pi mcp add tasknode --url https://tasknode.postfiat.org/mcp --header "Authorization=Bearer <TOKEN>" --exposure direct
```

Pi needs Node.js 22.19 or later. In a running session, `/reload` picks up the change.

## OpenCode and Kilo

```
opencode mcp add tasknode --url https://tasknode.postfiat.org/mcp --header "Authorization=Bearer <TOKEN>"
```

For Kilo, run the same command with `kilo` in place of `opencode`.

## Claude Desktop and claude.ai

Add Task Node as a custom connector: open Settings → Connectors, choose **Add custom connector**, enter `https://tasknode.postfiat.org/mcp`, and sign in with GitHub when prompted. No token is needed.

## ChatGPT

In ChatGPT's developer mode, add a connector with the server URL `https://tasknode.postfiat.org/mcp` and sign in with GitHub when prompted.

## Cursor

Add Task Node to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "tasknode": {
      "url": "https://tasknode.postfiat.org/mcp",
      "headers": { "Authorization": "Bearer <TOKEN>" }
    }
  }
}
```

## Gemini CLI

Add Task Node to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "tasknode": {
      "httpUrl": "https://tasknode.postfiat.org/mcp",
      "headers": { "Authorization": "Bearer <TOKEN>" }
    }
  }
}
```

## Any other MCP client

Add a remote HTTP (streamable HTTP) MCP server with:

- URL: `https://tasknode.postfiat.org/mcp`
- Header: `Authorization: Bearer <TOKEN>`

Clients that support OAuth can use the URL alone and sign in with GitHub. The server publishes standard OAuth discovery metadata with dynamic client registration.

## Your own app

### OpenAI Responses API

```python
from openai import OpenAI

client = OpenAI()
response = client.responses.create(
    model="gpt-6-astra",
    tools=[{
        "type": "mcp",
        "server_label": "tasknode",
        "server_url": "https://tasknode.postfiat.org/mcp",
        "headers": {"Authorization": "Bearer <TOKEN>"},
        "require_approval": "never",
    }],
    input="What are my outstanding Task Node tasks?",
)
print(response.output_text)
```

### Claude API (MCP connector)

```python
import anthropic

client = anthropic.Anthropic()
response = client.beta.messages.create(
    model="claude-opus-5",
    max_tokens=16000,
    betas=["mcp-client-2025-11-20"],
    mcp_servers=[{
        "type": "url",
        "url": "https://tasknode.postfiat.org/mcp",
        "name": "tasknode",
        "authorization_token": "<TOKEN>",
    }],
    tools=[{"type": "mcp_toolset", "mcp_server_name": "tasknode"}],
    messages=[{"role": "user", "content": "What are my outstanding Task Node tasks?"}],
)
for block in response.content:
    if block.type == "text":
        print(block.text)
```

## Corbanu Terminal

Run `/tasknode link` to sign in and `/tasknode status` to check the connection. It uses the same GitHub sign-in as the MCP server.

## What your agent can do

| Tool | What it does |
|---|---|
| `tasknode_status` | Your account, linked wallet and task counts. |
| `tasknode_list_tasks` | List tasks in one tab (outstanding, verification, rewarded, refused). |
| `tasknode_get_task` | The full task card: objective, steps, reward, verification criteria, the current verification question and the actions allowed. |
| `tasknode_task_action` | Accept, refuse or cancel a task. |
| `tasknode_submit_evidence` | Submit initial evidence, or answer a verification request. |
| `tasknode_request_task` | Ask Task Node to generate a task from a description of the work you want to do. |
| `tasknode_list_requests` | Your recent task requests and their status. |
| `tasknode_get_context` | Read your context document. |
| `tasknode_save_context` | Update your context document. Pass the revision you read so newer edits are never overwritten. |
| `tasknode_chat` | Ask Task Node chat, which knows your context, tasks and history. Billed to your Task Node credits. |
| `tasknode_balance` · `tasknode_rewards` | Your PFT balance and recent rewards. |

Good evidence is durable: pull request and commit links, file paths, the exact commands you ran and their results. Agents should never cite localhost URLs or paste secrets.

## Things to ask

- "What are my outstanding Task Node tasks?"
- "Accept the PR review task and do it."
- "Answer the verification request on my last task with the test output."
- "Ask Task Node chat which task I should do next."
- "Add this decision to my Task Node context document."

## Switch accounts or sign out

Each agent setup holds one Task Node account. To switch, change to the other account in Task Node (it needs its own linked GitHub account), open the connect page, create a token and paste the new command. It replaces the old account.

To sign out everywhere, click **Sign out all agents** on the connect page. This revokes every agent and Corbanu Terminal token for the account. Then remove the entry from each agent:

```
claude mcp remove --scope user tasknode
codex mcp remove tasknode
hermes mcp remove tasknode
pi mcp remove tasknode
```

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
- **Asked to link GitHub.** Link GitHub to your Task Node account, then reopen the connect page.
- **The agent doesn't show Task Node tools.** Restart the agent. In a running session, use `/mcp` in Claude Code, `/reload-mcp` in Hermes or `/reload` in Pi.
- **Pi won't start.** Pi needs Node.js 22.19 or later.
