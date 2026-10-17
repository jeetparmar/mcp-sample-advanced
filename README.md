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

## Run the AI client

Add your Groq API key to `.env`:

```env
GROQ_API_KEY=your_key_here
```

Run it from the project virtual environment so the `groq` and `mcp` packages are available:

```bash
source .venv/bin/activate
python ai_client.py
```

The AI client sends the available MCP tools to Groq, then calls a tool when the model requests one. With MCP SDK v2, use `tool.input_schema`, `result.is_error`, and `model_dump()` in `ai_client.py`.

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
