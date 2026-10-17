import asyncio
import json
import os

from dotenv import load_dotenv
from groq import AsyncGroq
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

MODEL = "openai/gpt-oss-120b"
SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Set GROQ_API_KEY in .env")

    async with AsyncGroq(api_key=api_key) as llm:
        async with streamable_http_client(SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.list_tools()
                tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description or "",
                            "parameters": tool.input_schema,
                        },
                    }
                    for tool in response.tools
                ]
                messages = [{"role": "user", "content": "Find user ID 1."}]

                for _ in range(5):
                    response = await llm.chat.completions.create(
                        model=MODEL, messages=messages, tools=tools, tool_choice="auto"
                    )
                    message = response.choices[0].message
                    messages.append(message.model_dump(exclude_none=True))

                    if not message.tool_calls:
                        print(message.content or "")
                        return

                    for call in message.tool_calls:
                        try:
                            result = await session.call_tool(
                                call.function.name,
                                arguments=json.loads(call.function.arguments or "{}"),
                            )
                            content = "\n".join(
                                item.text
                                for item in result.content
                                if item.type == "text"
                            )
                        except Exception as exc:
                            content = f"Tool error: {exc}"

                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "name": call.function.name,
                                "content": content,
                            }
                        )

    print("Stopped after five tool rounds.")


if __name__ == "__main__":
    asyncio.run(main())
