import httpx
import json
import logging
import uuid  # Import uuid to generate session ID

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Server:
    """Handles the connection and communication with the MCP server."""

    def __init__(self, base_url: str, tool_name: str, session_id: str = None) -> None:
        self.base_url = base_url
        self.tool_name = tool_name
        self.session_id = session_id  # Store session ID
        self.client: httpx.Client = None  # To hold the HTTP client

    def initialize(self) -> None:
        """Initialize the HTTP client."""
        self.client = httpx.Client()
        logging.info(f"Initialized server with base URL: {self.base_url}")

    def cleanup(self) -> None:
        """Clean up the HTTP client when done."""
        if self.client:
            self.client.close()
            logging.info("Cleaned up the HTTP client.")

    def call_tool(self, expression: str) -> dict:
        """Call the tool (e.g., math evaluator) on the server."""

        url = f"{self.base_url}/{self.tool_name}/"
        headers = {
            "accept": "text/event-stream",
            # "content-type": "application/json",
        }

        # Include session ID in the headers if available
        if self.session_id:
            headers["X-Session-ID"] = self.session_id
            logging.info(f"Adding session ID to headers: {self.session_id}")

        payload = {
            "tool": self.tool_name,
            "arguments": {"expression": expression}
        }

        try:
            response = self.client.post(url, headers=headers, json=payload, timeout=None)
            response.raise_for_status()

            logging.info(f"Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    response_json = response.json()
                    if "result" in response_json:
                        logging.info(f"Result: {response_json['result']}")
                        return response_json["result"]
                    else:
                        logging.error("No result found in the response.")
                        return None
                except json.JSONDecodeError:
                    logging.error("Error: Response is not in valid JSON format")
                    return None
            else:
                logging.error(f"Failed to get valid response: {response.status_code}")
                return None
        except httpx.RequestError as e:
            logging.error(f"Request error: {e}")
            return None

class MathEvaluatorServer(Server):
    """Handles specific server logic for a math evaluator tool."""

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url, "math-evaluator")


class Session:
    """Manages the entire communication session with the server, keeping it alive across interactions."""

    def __init__(self, server: Server) -> None:
        self.server = server
        self.server_initialized = False

    def initialize(self) -> None:
        """Initialize the session (connect to the server)."""
        if not self.server_initialized:
            # Generate a unique session ID here
            self.server.session_id = str(uuid.uuid4())  # Generate a new unique session ID
            self.server.initialize()
            self.server_initialized = True
            logging.info(f"Session initialized with session ID: {self.server.session_id}")

    def cleanup(self) -> None:
        """Clean up the session and close the server connection."""
        if self.server_initialized:
            self.server.cleanup()
            self.server_initialized = False
            logging.info("Session cleaned up.")

    def call_math_evaluator(self, expression: str) -> str:
        """Call the math evaluator tool through the session."""
        if not self.server_initialized:
            raise RuntimeError("Session not initialized")

        result = self.server.call_tool(expression)
        return result if result else "Failed to evaluate expression"


def main() -> None:
    """Main function to interact with the server."""
    # Initialize the math evaluator server
    server = MathEvaluatorServer(base_url="http://127.0.0.1:3000/mcp")
    session = Session(server)

    try:
        # Initialize the session (open server connection)
        session.initialize()

        while True:
            expression = input("Enter a mathematical expression (or 'quit' to exit): ").strip()
            if expression.lower() == 'quit':
                break

            result = server.call_tool(expression)
            print(f"Result: {result}")

    finally:
        # Clean up the session and close server connection
        session.cleanup()


if __name__ == "__main__":
    main()
