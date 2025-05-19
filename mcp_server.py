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

from fastmcp import FastMCP

mcp = FastMCP(name="MyServer")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool()
def math_eval(expression: str) -> str:
    """
    Safely evaluates basic math expressions (e.g., "2 + 3 * 5").
    """
    try:
        allowed_names = {"__builtins__": None}
        result = eval(expression, allowed_names, {})
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
