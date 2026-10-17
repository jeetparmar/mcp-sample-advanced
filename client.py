import asyncio
import logging
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent / "server.py")],
        env=None,
    )
    logger.info(
        "Starting MCP server: %s %s", server_params.command, server_params.args[0]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            logger.info("Initializing MCP session")
            await session.initialize()
            logger.info("MCP session initialized")
            logger.info("Connected to MCP server")

            tools_result = await session.list_tools()
            logger.info("Received %d tool(s) from the server", len(tools_result.tools))

            for tool in tools_result.tools:
                logger.info(
                    "Available tool: %s: %s",
                    tool.name,
                    tool.description or "No description",
                )

            logger.info("Calling get_user for user_id=1")
            get_result = await session.call_tool("get_user", arguments={"user_id": 1})
            for content in get_result.content:
                if content.type == "text":
                    logger.info("get_user: %s", content.text)

            logger.info("Calling list_users")
            list_result = await session.call_tool("list_users")
            for content in list_result.content:
                if content.type == "text":
                    logger.info("list_users: %s", content.text)

            logger.info("Calling search_users for name=jeet")
            search_result = await session.call_tool(
                "search_users", arguments={"name": "jeet"}
            )
            for content in search_result.content:
                if content.type == "text":
                    logger.info("search_users: %s", content.text)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        logger.exception("MCP client failed")
        raise
