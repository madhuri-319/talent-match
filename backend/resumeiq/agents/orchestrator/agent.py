from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from resumeiq.mcp_layer.server import handle_request


def make_pg_tool(tool_name: str):
    def tool_func(payload: dict = None):
        return handle_request(tool_name, payload or {})
    tool_func.__name__ = tool_name
    tool_func.__doc__ = f"PostgreSQL tool: {tool_name}"
    return FunctionTool(func=tool_func)


pg_tools = [
    make_pg_tool("init_db"),
    make_pg_tool("query_db"),
    make_pg_tool("insert_candidate"),
    make_pg_tool("insert_job"),
    make_pg_tool("insert_application"),
    make_pg_tool("get_candidates"),
    make_pg_tool("get_jobs"),
    make_pg_tool("get_applications"),
]

# Root Agent (entry point)
root_agent = Agent(
    name="resumeiq_orchestrator",
    model="gemini-1.5-flash",
    description="Main orchestrator agent for ResumeIQ system",
    instruction="""
    You are an orchestrator agent.

    Based on user input:
    - If it's resume related → say 'Routing to Resume Flow'
    - If it's HR prompt → say 'Routing to HR Flow'
    - For database operations → use the available PostgreSQL MCP tools
    - Otherwise → ask for clarification
    """,
    tools=pg_tools,
)