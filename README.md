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

## Groq setup

Add your Groq API key to `.env`:

```env
GROQ_API_KEY=your_key_here
```

## Run the AI client

The AI client starts the MCP server itself over stdio:

```bash
python ai_client.py
```

## Run the HTTP AI client

Start the HTTP server in one terminal:

```bash
python http/server.py
```

Then, in another terminal, run:

```bash
python http/client.py
```

It connects to `http://127.0.0.1:8000/mcp`.

## Tools

| Tool           | Arguments                  |
| -------------- | -------------------------- |
| `list_users`   | None                       |
| `get_user`     | `user_id`                  |
| `create_user`  | `name`, `email`            |
| `update_user`  | `user_id`, `name`, `email` |
| `delete_user`  | `user_id`                  |
| `search_users` | `name`                     |

`users.db` is created automatically with two sample users.
