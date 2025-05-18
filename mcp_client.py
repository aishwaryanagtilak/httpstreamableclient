# import asyncio
# from fastmcp import Client
# from fastmcp.client.transports import PythonStdioTransport

# async def main():
#     # 'server.py' आपके सर्वर स्क्रिप्ट का पथ है
#     transport = PythonStdioTransport("mcp_server.py")
#     client = Client(transport=transport)

#     async with client:
#         tools = await client.list_tools()
#         print("Avaialable Tools:", tools)

#         result = await client.call_tool("fetch_stock_info", {"symbol": "AAPL"})
#         print("AAPL Stock Information:", result)

# if __name__ == "__main__":
#     asyncio.run(main())

# ----------------------------------------------------------

# # weather_client.py
# import asyncio
# from fastmcp import Client
# from fastmcp.client.transports import PythonStdioTransport

# async def main():
#     transport = PythonStdioTransport("mcp_server.py")
#     client = Client(transport=transport)

#     async with client:
#         result = await client.call_tool("get_weather", {"city": "New York"})
#         print("Weather in New York:", result)

# if __name__ == "__main__":
#     asyncio.run(main())

# ----------------------------------------------------------

from fastmcp import Client
import asyncio

server_url = "http://127.0.0.1:8000/mcp"

client = Client(server_url)

async def main():
    async with client:
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]
        print("Available tools:")
        for i, name in enumerate(tool_names):
            print(f"{i + 1}. {name}")

        choice = int(input("Select a tool to call (enter number): ")) - 1
        selected_tool = tool_names[choice]
        print(f"Selected tool: {selected_tool}")

        if selected_tool == "greet":
            name = input("Enter name: ")
            result = await client.call_tool("greet", {"name": name})
        elif selected_tool == "math_eval":
            expr = input("Enter a math expression: ")
            result = await client.call_tool("math_eval", {"expression": expr})
        else:
            print("Tool not recognized or not supported in this demo.")
            return

        print("Response:", result[0].text)

# Run the client
if __name__ == "__main__":
    asyncio.run(main())
