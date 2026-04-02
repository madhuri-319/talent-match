TOOL_REGISTRY = {}

def handle_request(tool_name: str, payload: dict):
    if tool_name not in TOOL_REGISTRY:
        return {"status": "error", "message": f"Tool '{tool_name}' not found"}
    try:
        result = TOOL_REGISTRY[tool_name](payload)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
