# MCP User Directory

A minimal MCP server backed by SQLite.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the demo

```bash
python client.py
```

The client starts the server using MCP's stdio transport. Server logs go to stderr; stdout is reserved for MCP messages.

## Tools

| Tool | Arguments |
| --- | --- |
| `list_users` | None |
| `get_user` | `user_id` |
| `create_user` | `name`, `email` |
| `update_user` | `user_id`, `name`, `email` |
| `delete_user` | `user_id` |
| `search_users` | `name` |

`users.db` is created automatically with two sample users.
