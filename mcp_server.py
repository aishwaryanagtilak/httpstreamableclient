# import yfinance as yf
# from fastmcp import FastMCP
# from pandas import DataFrame

# mcp = FastMCP("stocks")

# @mcp.tool()
# def fetch_stock_info(symbol: str) -> dict:
#     """Get Company's general information."""
#     stock = yf.Ticker(symbol)
#     return stock.info

# @mcp.tool()
# def fetch_quarterly_financials(symbol: str) -> DataFrame :
#     """Get stock quarterly financials."""
#     stock = yf.Ticker(symbol)
#     return stock.quarterly_financials.T

# @mcp.tool()
# def fetch_annual_financials(symbol: str) -> DataFrame:
#     """Get stock annual financials."""
#     stock = yf.Ticker(symbol)
#     return stock.financials.T

# if __name__ == "__main__":
#     mcp.run(transport="stdio")

# ----------------------------------------------------------


# weather_server.py
# import requests
# from fastmcp import FastMCP

# API_KEY = "219ca700aac40573a4f52f7344be72c9"
# mcp = FastMCP("weather_tools")

# @mcp.tool()
# def get_weather(city: str) -> dict:
#     """Fetch current weather for a given city."""
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
#     response = requests.get(url)
#     return response.json()

# if __name__ == "__main__":
#     mcp.run(transport="stdio")

# ----------------------------------------------------------

from fastmcp import Client
import asyncio

# Define the server URL
server_url = "http://127.0.0.1:8000/mcp"

# Initialize the client
client = Client(server_url)

async def main():
    async with client:
        # Get the list of tools once
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]

        print("\nWelcome to FastMCP Client!")
        print("Available tools:")
        for i, name in enumerate(tool_names):
            print(f"{i + 1}. {name}")
        print("Type 'exit' to quit.\n")

        while True:
            choice = input("Select a tool to call (enter number or 'exit'): ").strip()

            if choice.lower() == "exit":
                print("Exiting client.")
                break

            if not choice.isdigit() or not (1 <= int(choice) <= len(tool_names)):
                print("Invalid choice. Please try again.")
                continue

            selected_tool = tool_names[int(choice) - 1]

            if selected_tool == "greet":
                name = input("Enter name: ")
                result = await client.call_tool("greet", {"name": name})

            elif selected_tool == "math_eval":
                expr = input("Enter a math expression: ")
                result = await client.call_tool("math_eval", {"expression": expr})

            else:
                print("Tool not supported in this demo.")
                continue

            print("Response:", result[0].text)
            print()

# Run the client
if __name__ == "__main__":
    asyncio.run(main())
