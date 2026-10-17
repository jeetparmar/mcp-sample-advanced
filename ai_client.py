import asyncio
import json
import os
from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

llm = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])
model = "openai/gpt-oss-120b"


async def main():
    server = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server) as (read, write):
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
            available_tools = {tool.name for tool in response.tools}
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant. "
                        "Use available tools when needed. "
                        "Answer using tool results."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Find the user with ID 1, "
                        "then list all users."
                        "then create another user with some name and email"
                        "fetch again the user list"
                    ),
                },
            ]
            for _ in range(5):
                response = await llm.chat.completions.create(
                    model=model, messages=messages, tools=tools, tool_choice="auto"
                )
                message = response.choices[0].message
                if not message.tool_calls:
                    print(message.content)
                    break

                messages.append(message.model_dump(exclude_none=True))

                for call in message.tool_calls:
                    name = call.function.name
                    args = json.loads(call.function.arguments or "{}")

                    if name not in available_tools:
                        result = {"error": "unknown mcp tool"}
                    else:
                        try:
                            result = await session.call_tool(name, arguments=args)
                            result = {
                                "isError": result.is_error,
                                "content": [
                                    item.model_dump(mode="json")
                                    for item in result.content
                                ],
                            }
                        except Exception as exc:
                            result = {"error": str(exc)}
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(result),
                        }
                    )
            else:
                print("stopped")


if __name__ == "__main__":
    asyncio.run(main())
