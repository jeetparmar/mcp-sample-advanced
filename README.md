# MCP User Directory

A small [Model Context Protocol](https://modelcontextprotocol.io/) server that exposes a SQLite-backed user directory. It is accompanied by a local client that demonstrates every tool.

## Requirements

- Python 3.10 or later

## Setup

Create and activate a virtual environment, then install the pinned dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the demo client

```bash
python client.py
```

The client starts `server.py` as an MCP subprocess, discovers the available tools, and calls each one. The server uses the stdio transport, so it is normally started by an MCP host rather than opened directly in a terminal.

## Tools

| Tool | Arguments | Description |
| --- | --- | --- |
| `list_users` | None | Returns every user in the directory. |
| `get_user` | `user_id: int` | Returns one user, or `{"error": "user not found"}` when the ID is absent. |
| `search_users` | `name: str` | Performs a literal substring search on user names. `%` and `_` are treated as normal characters, not SQL wildcards. |

## Data and logging

On its first start, the server creates `users.db` beside `server.py` and seeds two sample users: Jeet and Riya. The database is local runtime data and is ignored by Git. Delete it to start again with the sample data.

Both the client and server write operational logs to standard error. Standard output remains reserved for MCP messages, which prevents logging from corrupting the stdio protocol.

## Project layout

```text
server.py         MCP server and SQLite access layer
client.py         Demonstration MCP client
requirements.txt  Pinned Python dependency
```

## Verify

```bash
python -m py_compile server.py client.py
python client.py
```
