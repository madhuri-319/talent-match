import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp_server")

from resumeiq.mcp_layer.tools.pg_mcp_tools import (
    init_db,
    query_db,
    insert_candidate,
    insert_job,
    insert_application,
    get_candidates,
    get_jobs,
    get_applications,
)

TOOL_REGISTRY = {
    "init_db": init_db,
    "query_db": query_db,
    "insert_candidate": insert_candidate,
    "insert_job": insert_job,
    "insert_application": insert_application,
    "get_candidates": get_candidates,
    "get_jobs": get_jobs,
    "get_applications": get_applications,
}


def get_tool_schemas():
    return [
        {
            "name": "query_db",
            "description": "Execute a raw SQL query on the PostgreSQL database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query to execute"},
                    "params": {"type": "array", "description": "Query parameters"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "insert_candidate",
            "description": "Insert a new candidate into the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "string",
                        "description": "JSON object with candidate fields",
                    }
                },
                "required": ["data"],
            },
        },
        {
            "name": "insert_job",
            "description": "Insert a new job description into the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "JSON object with job fields"}
                },
                "required": ["data"],
            },
        },
        {
            "name": "insert_application",
            "description": "Insert a new job application",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "JSON object with application fields"}
                },
                "required": ["data"],
            },
        },
        {
            "name": "get_candidates",
            "description": "Retrieve candidates from the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "string",
                        "description": "JSON object with filter criteria",
                        "default": "{}",
                    }
                },
            },
        },
        {
            "name": "get_jobs",
            "description": "Retrieve job descriptions from the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "string",
                        "description": "JSON object with filter criteria",
                        "default": "{}",
                    }
                },
            },
        },
        {
            "name": "get_applications",
            "description": "Retrieve job applications from the database",
            "parameters": {
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "string",
                        "description": "JSON object with filter criteria",
                        "default": "{}",
                    }
                },
            },
        },
        {
            "name": "init_db",
            "description": "Initialize database tables (run once on setup)",
            "parameters": {"type": "object", "properties": {}},
        },
    ]


def handle_request(tool_name: str, payload: dict):
    logger.info(f"[MCP-SERVER] handle_request() - tool={tool_name}, payload={payload}")
    
    if tool_name not in TOOL_REGISTRY:
        logger.error(f"[MCP-SERVER] Tool not found: {tool_name}")
        return {"status": "error", "message": f"Tool '{tool_name}' not found"}
    
    try:
        tool_func = TOOL_REGISTRY[tool_name]
        
        if tool_name in ("query_db", "get_candidates", "get_jobs", "get_applications"):
            result = tool_func(**payload)
        elif tool_name == "insert_candidate":
            result = tool_func(payload.get("data", "{}"))
        elif tool_name == "insert_job":
            result = tool_func(payload.get("data", "{}"))
        elif tool_name == "insert_application":
            result = tool_func(payload.get("data", "{}"))
        else:
            result = tool_func()
            
        logger.info(f"[MCP-SERVER] handle_request() SUCCESS - tool={tool_name}")
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"[MCP-SERVER] handle_request() ERROR - tool={tool_name}, error={str(e)}")
        return {"status": "error", "message": str(e)}