import asyncio
import logging
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent / "server.py")],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            logger.info("Available tools: %s", [tool.name for tool in tools.tools])

            for name, arguments in [
                ("get_user", {"user_id": 1}),
                ("list_users", {}),
                ("search_users", {"name": "jeet"}),
                ("create_user", {"name": "samarth", "email": "samarth@example.com"}),
                (
                    "update_user",
                    {
                        "user_id": 1,
                        "name": "jeet singh",
                        "email": "jeetsingh@example.com",
                    },
                ),
                ("delete_user", {"user_id": 1}),
                ("list_users", {}),
            ]:
                result = await session.call_tool(name, arguments=arguments)
                for content in result.content:
                    if content.type == "text":
                        logger.info("%s: %s", name, content.text)


if __name__ == "__main__":
    asyncio.run(main())
