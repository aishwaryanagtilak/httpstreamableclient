import logging
import contextlib
from collections.abc import AsyncIterator
from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("basic-mcp")

app = Server("basic-mcp-app")

from starlette.requests import Request

@app.call_tool()
async def math_evaluator(request: Request, name: str, arguments: dict) -> list[TextContent]:
    ctx = request.state
    expression = arguments.get("expression", "").strip()
    allowed_chars = "0123456789+-*/(). "
    if not all(c in allowed_chars for c in expression):
        return [
            TextContent(
                type="text",
                text="Invalid expression. Only digits and + - * / ( ) allowed.",
            )
        ]

    try:
        result = eval(expression, {"__builtins__": {}})
        message = f"Result of '{expression}' is: {result}"
    except Exception as e:
        message = f"Error evaluating expression: {e}"

    if hasattr(ctx, 'session') and ctx.session:
        await ctx.session.send_log_message(
            level="info",
            data=message,
            logger="math-evaluator",
            related_request_id=ctx.request_id,
        )

    return [TextContent(type="text", text=message)]


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="math-evaluator",
            description="Evaluates a basic math expression like '2 + 3 * (4 - 1)'",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate (e.g., '2 + 3 * 4')",
                    },
                },
                "required": ["expression"],
            },
        ),
    ]


session_manager = StreamableHTTPSessionManager(
    app=app,
    json_response=True,
)

async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
    """
    Handles incoming requests and responds with either JSON or SSE based on the client 'Accept' header.
    """
    headers = dict(scope.get('headers', []))
    accept_header = headers.get(b'content-type', None)
    session_id = headers.get(b'x-session-id', None)

    print('======================================', headers)
    # Look for 'X-Session-ID' in headers (client may send it)
    if session_id:
        session_id = session_id.decode()
        logger.info(f"Received Session ID: {session_id}")
        if b'application/json' in accept_header:
            request = Request(scope, receive)    
            try:
                body = await request.json()

                if "tool" in body and "arguments" in body:
                    tool_name = body["tool"]
                    arguments = body["arguments"]

                    if tool_name == "math-evaluator":
                        result = await math_evaluator(request, "", arguments)
                        response_body = {
                            "result": result[0].text
                        }
                    else:
                        response_body = {"error": f"Tool '{tool_name}' not found."}
                else:
                    response_body = {"error": "'tool' and 'arguments' must be provided in the request."}
            
                response = JSONResponse(response_body)

                await send({
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")]
                })
                await send({
                    "type": "http.response.body",
                    "body": response.body,
                })
            except Exception as e:
                error_response = JSONResponse({"error": str(e)})
                error_body = error_response.body
                await send({
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [(b"content-type", b"application/json")]
                })
                await send({
                    "type": "http.response.body",
                    "body": error_body,
                })    
    
        else:
            no_accept_response = JSONResponse({"error": "No 'Accept' header found in request."})
            no_accept_body = no_accept_response.body
            await send({
                "type": "http.response.start",
                "status": 400,
                "headers": [(b"content-type", b"application/json")]
            })
            await send({
                "type": "http.response.body",
                "body": no_accept_body,
            })

    else:
        logger.warning("No Session ID found in the request.")
    
# Lifespan manager to start/stop session manager
@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    """Context manager for managing session manager lifecycle."""
    async with session_manager.run():
        logger.info("Application started with StreamableHTTP session manager!")
        try:
            yield
        finally:
            logger.info("Application shutting down...")


starlette_app = Starlette(
    debug=True,
    routes=[Mount("/mcp", app=handle_streamable_http)],
    lifespan=lifespan,
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(starlette_app, host="127.0.0.1", port=3000)


