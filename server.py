import logging
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("user-directory")
DB = Path(__file__).with_name("users.db")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
logger.addHandler(handler)


@contextmanager
def get_db():
    """Open, commit, and close one SQLite connection."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO users VALUES
            (1, 'Jeet', 'jeet@example.com'),
            (2, 'Riya', 'riya@example.com')
            """
        )


@mcp.tool()
def list_users() -> list:
    """Return all users."""
    logger.info("list_users")
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    return [dict(row) for row in rows]


@mcp.tool()
def get_user(user_id: int) -> dict:
    """Return one user by ID."""
    logger.info("get_user id=%d", user_id)
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else {"error": "user not found"}


@mcp.tool()
def create_user(name: str, email: str) -> dict:
    """Create a user."""
    logger.info("create_user")
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)", (name, email)
        )
    return {"id": cursor.lastrowid, "name": name, "email": email}


@mcp.tool()
def update_user(user_id: int, name: str, email: str) -> dict:
    """Replace a user's name and email."""
    logger.info("update_user id=%d", user_id)
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, user_id),
        )
    if cursor.rowcount == 0:
        return {"error": "user not found"}
    return {"id": user_id, "name": name, "email": email}


@mcp.tool()
def delete_user(user_id: int) -> dict:
    """Delete one user by ID."""
    logger.info("delete_user id=%d", user_id)
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    if cursor.rowcount == 0:
        return {"error": "user not found"}
    return {"id": user_id, "deleted": True}


@mcp.tool()
def search_users(name: str) -> list:
    """Find users whose names contain the given text."""
    logger.info("search_users")
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM users WHERE name LIKE ? ORDER BY id", (f"%{name}%",)
        ).fetchall()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    logger.info("Starting MCP server")
    mcp.run(transport="stdio")
