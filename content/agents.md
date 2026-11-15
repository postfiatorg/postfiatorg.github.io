---
title: "Connect your AI agent to Task Node"
type: "blog"
url: "/agents/"
date: 2026-10-02
summary: "Connect Claude Code, Codex, Hermes, Pi, OpenCode, Cursor, ChatGPT or any MCP client with one command. Your agent takes tasks, does the work and submits evidence."
breadcrumb_label: "Task Node"
breadcrumb_url: "/task-node/"
# guide: wrapped code blocks with copy buttons, quick-start and agent-picker styles (assets/css/guide.css)
guide: true
---

<div class="tn-quickstart">

## Quick start: one command {#quick-start}

### Install or update

```sh
curl -fsSL https://tasknode.postfiat.org/install | sh
```

Run it in the terminal where your agent runs, on your laptop or a remote box over SSH. The same command updates an existing install to the latest release.

1. **Approve.** It prints a link. Open it on any device and press **Approve**.
2. **Unlock Docs.** Unlock Docs once in that browser. This gives your agents the prompt library.
3. **Restart.** Restart running agents, or run `/mcp` in Claude Code. Agents load new tools only when they start.

It sets up every agent it finds: Claude Code, Codex, Hermes, Pi, OpenCode, Kilo, Cursor and Gemini CLI. No token to copy. Your Task Node account needs GitHub linked once (Settings → Security → Connected accounts).

### Check what is connected

```sh
curl -fsSL https://tasknode.postfiat.org/install | sh -s -- --status
```

### Ask an agent to check itself

```text
Check your Task Node access. Call tasknode_status and tell me which account you are on. Then call prompt_list and tell me how many prompts it returns. If the tasknode or tasknode-prompts tools are missing, say "not installed". If prompt_list says pairing is needed, say "not paired" and show me the device fingerprint. Do not print any tokens.
```

- **Not installed.** Run the install command, then restart the agent.
- **Not paired.** Open Docs, unlock it, open **Agent access** and approve the matching fingerprint.

### Only some agents

```sh
curl -fsSL https://tasknode.postfiat.org/install | sh -s -- --agent claude,codex
```

### Sign out

```sh
curl -fsSL https://tasknode.postfiat.org/install | sh -s -- --disconnect
```

[Open the connect page →](https://tasknode.postfiat.org/connect)

</div>

<div class="tn-agents">

### Manual setup per agent {#pick-your-agent}

- [Claude Code](#claude-code) Paste command
- [Codex](#codex) Paste command
- [Hermes](#hermes) Paste command
- [Pi](#pi) Paste command
- [OpenCode · Kilo](#opencode) Paste command
- [Claude Desktop · claude.ai](#claude-desktop) Connector
- [ChatGPT](#chatgpt) Connector
- [Cursor](#cursor) Config file
- [Gemini CLI](#gemini-cli) Config file
- [Any MCP client](#other-mcp-clients) URL and header
- [Your own app](#your-own-app) OpenAI · Claude API
- [Corbanu Terminal](#corbanu-terminal) /tasknode link

</div>

## Tokens and sign-in {#sign-in}

- **Token.** The connect page creates a token and shows a paste-ready command for Claude Code, Codex, Hermes, Pi, OpenCode and Kilo, plus the URL and header for every other MCP client. Tokens work everywhere, including over SSH. The token is shown once and never expires. Anyone who holds it can act as you, so treat it like a password.
- **Browser sign-in.** When the agent runs on the same computer as your browser, Claude Code, Codex, Claude Desktop, claude.ai and ChatGPT sign in through GitHub directly.
- **Linked GitHub.** Agents sign in through the GitHub account linked to your Task Node account. Signing in with a GitHub account that isn't linked creates a separate, empty Task Node account.

The commands below show `<TOKEN>` where your token goes. The connect page fills it in for you.

## Claude Code {#claude-code}

```sh
claude mcp remove --scope user tasknode >/dev/null 2>&1; claude mcp add --scope user --transport http tasknode https://tasknode.postfiat.org/mcp --header "Authorization: Bearer <TOKEN>"
```

Browser sign-in instead of a token:

```sh
claude mcp add --scope user --transport http tasknode https://tasknode.postfiat.org/mcp
```

Then run `/mcp` inside Claude Code and choose to authenticate.

## Codex (OpenAI) {#codex}

```sh
codex mcp remove tasknode >/dev/null 2>&1; (umask 077; printf '\n[mcp_servers.tasknode]\nurl = "https://tasknode.postfiat.org/mcp"\nhttp_headers = { Authorization = "Bearer <TOKEN>" }\n' >> "${CODEX_HOME:-$HOME/.codex}/config.toml")
```

The command adds this entry to `~/.codex/config.toml` (or `$CODEX_HOME/config.toml`). You can also add it by hand:

```toml
[mcp_servers.tasknode]
url = "https://tasknode.postfiat.org/mcp"
http_headers = { Authorization = "Bearer <TOKEN>" }
```

Browser sign-in instead of a token:

```sh
codex mcp add tasknode --url https://tasknode.postfiat.org/mcp
codex mcp login tasknode
```

## Hermes {#hermes}

```sh
hermes config set MCP_TASKNODE_API_KEY <TOKEN> && hermes config set --force mcp_servers.tasknode.url https://tasknode.postfiat.org/mcp && hermes config set --force mcp_servers.tasknode.headers.Authorization 'Bearer ${MCP_TASKNODE_API_KEY}'
```

Keep the single quotes around `'Bearer ${MCP_TASKNODE_API_KEY}'`: Hermes resolves the variable itself. In a running session, `/reload-mcp` picks up the change.

## Pi {#pi}

```sh
pi mcp add tasknode --url https://tasknode.postfiat.org/mcp --header "Authorization=Bearer <TOKEN>" --exposure direct
```

Pi needs Node.js 22.19 or later. In a running session, `/reload` picks up the change.

## OpenCode and Kilo {#opencode}

```sh
opencode mcp add tasknode --url https://tasknode.postfiat.org/mcp --header "Authorization=Bearer <TOKEN>"
```

Kilo takes the same command with `kilo` in place of `opencode`:

```sh
kilo mcp add tasknode --url https://tasknode.postfiat.org/mcp --header "Authorization=Bearer <TOKEN>"
```

## Claude Desktop and claude.ai {#claude-desktop}

Open Settings → Connectors, choose **Add custom connector**, enter `https://tasknode.postfiat.org/mcp`, and sign in with GitHub when prompted. No token needed.

## ChatGPT {#chatgpt}

In ChatGPT's developer mode, add a connector with the server URL `https://tasknode.postfiat.org/mcp` and sign in with GitHub when prompted.

## Cursor {#cursor}

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

## Gemini CLI {#gemini-cli}

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

## Any other MCP client {#other-mcp-clients}

Add a remote HTTP (streamable HTTP) MCP server. The connect page shows both values with your token filled in.

- URL: `https://tasknode.postfiat.org/mcp`
- Header: `Authorization: Bearer <TOKEN>`

Clients that support OAuth use the URL alone and sign in with GitHub. The server publishes standard OAuth discovery metadata with dynamic client registration.

## Your own app {#your-own-app}

### OpenAI Responses API {#openai-responses-api}

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

### Claude API (MCP connector) {#claude-api}

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

## Corbanu Terminal {#corbanu-terminal}

Run `/tasknode link` to sign in and `/tasknode status` to check the connection. It uses the same GitHub sign-in as the MCP server.

## What your agent can do {#tools}

Task Node is a remote [MCP](https://modelcontextprotocol.io) server at `https://tasknode.postfiat.org/mcp`. Agents follow the same rules and limits as the web app.

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

Good evidence is durable: pull request and commit links, file paths, the exact commands you ran and their results. Agents never cite localhost URLs or paste secrets.

## Prompt library {#prompts}

The installer also adds a second tool server, `tasknode-prompts`, that runs on your own machine. It lets your agent read and edit the encrypted prompts you keep in Docs. Prompt text is decrypted only on your machine and never passes through the hosted Task Node tools. It needs Node.js 22 or later.

Access is granted when you approve the sign-in link and next unlock Docs in that browser. If you typed the short code instead of opening the link, approve the device under Docs → **Agent access** and give the agent the pairing line it shows.

| Tool | What it does |
|---|---|
| `prompt_list` | List your prompts. |
| `prompt_read` | Read one prompt. |
| `prompt_create` · `prompt_edit` | Create a prompt, or change it with an exact-text replacement. |
| `prompt_save_version` · `prompt_history` | Save a version and read earlier ones. |
| `prompt_stats` | Editing time and activity over 7 or 30 days. |
| `prompt_pair` | Finish manual pairing with the code from Docs. |

## Things to ask {#things-to-ask}

- "What are my outstanding Task Node tasks?"
- "Accept the PR review task and do it."
- "Answer the verification request on my last task with the test output."
- "Ask Task Node chat which task I should do next."
- "Add this decision to my Task Node context document."

## Switch accounts or sign out {#switch-accounts}

Run the installer again and approve as the other account. It names the account the machine is on now, asks before replacing it, and revokes the old token for that machine.

```sh
curl -fsSL https://tasknode.postfiat.org/install | sh -s -- --status       # which agent is on which account
curl -fsSL https://tasknode.postfiat.org/install | sh -s -- --disconnect   # remove the entries and revoke the token
```

The connect page lists every connected device with its last use. Revoke one, or click **Sign out all agents** to revoke every agent and Corbanu Terminal token for the account.

## Several accounts on one computer {#several-accounts}

- **Claude Code.** Run the installer with `--scope local` in the folder where the other account should apply: `curl -fsSL https://tasknode.postfiat.org/install | sh -s -- --scope local --agent claude`. Claude Code uses that account only in that folder.
- **Codex.** Give each extra account its own Codex home that shares your OpenAI sign-in, then run the installer in that terminal:

  ```sh
  mkdir -p ~/.codex-work && ln -s ~/.codex/auth.json ~/.codex-work/auth.json
  export CODEX_HOME=~/.codex-work
  ```

  Start that account's sessions with `CODEX_HOME=~/.codex-work codex`.

## Troubleshooting {#troubleshooting}

- **Unauthorized (401).** The token was revoked or has been idle for 90 days. Run the installer again.
- **Asked to link GitHub.** Link GitHub to your Task Node account, then reopen the connect page.
- **A new Task Node feature is missing.** Run the installer again to update, then restart the agent.
- **Prompt tools say pairing is needed.** Open Docs, unlock it, open **Agent access** and approve the device.
- **The agent doesn't show Task Node tools.** Restart the agent. In a running session, use `/mcp` in Claude Code, `/reload-mcp` in Hermes or `/reload` in Pi.
- **Pi won't start.** Pi needs Node.js 22.19 or later.
