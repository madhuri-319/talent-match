import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp_client")

from resumeiq.mcp_layer.server import handle_request


def call_tool(tool_name: str, payload: dict):
    """
    Client interface used by agents
    """
    logger.info(f"[MCP-CLIENT] call_tool() - tool={tool_name}, payload={payload}")

    response = handle_request(tool_name, payload)

    if response.get("status") == "error":
        logger.error(f"[MCP-CLIENT] call_tool() ERROR - tool={tool_name}, error={response.get('message')}")
        raise Exception(response["message"])
    
    logger.info(f"[MCP-CLIENT] call_tool() SUCCESS - tool={tool_name}")
    return response["data"]