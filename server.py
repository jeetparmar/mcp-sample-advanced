import logging
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("my third server")

DB = Path(__file__).with_name("users.db")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.propagate = False

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(
    logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
)
logger.addHandler(stderr_handler)


@contextmanager
def get_db_connection() -> Iterator[sqlite3.Connection]:
    """Provide a configured SQLite connection to each tool call."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except sqlite3.Error:
        logger.exception("SQLite operation failed")
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the local database and its sample users when necessary."""
    logger.info("Initializing user database")
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )         
            """)
        conn.execute("""
            INSERT OR IGNORE INTO users VALUES
            (1, 'Jeet', 'jeet@example.com'),
            (2, 'Riya', 'riya@example.com')         
            """)
    logger.info("User database initialized")


@mcp.tool()
def list_users() -> list:
    """Return every user in the local directory."""
    logger.info("Listing users")
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM users").fetchall()
        users = [dict(row) for row in rows]
    logger.info("Listed %d user(s)", len(users))
    return users


@mcp.tool()
def get_user(user_id: int) -> dict:
    """Return the user with the supplied numeric ID, if it exists."""
    logger.info("Getting user with id=%d", user_id)
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        logger.warning("User not found for id=%d", user_id)
        return {"error": "user not found"}

    logger.info("User found for id=%d", user_id)
    return dict(row)


def escape_like(value: str) -> str:
    """Escape SQL LIKE wildcards so a name search remains a literal substring search."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@mcp.tool()
def search_users(name: str) -> list:
    """Find users whose names contain the supplied text, case-insensitively for ASCII."""
    logger.info("Searching users")
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM users WHERE name LIKE ? ESCAPE '\\'",
            (f"%{escape_like(name)}%",),
        ).fetchall()
        users = [dict(row) for row in rows]
    logger.info("User search returned %d result(s)", len(users))
    return users


if __name__ == "__main__":
    init_db()
    logger.info("Starting MCP server with stdio transport")
    mcp.run(transport="stdio")
