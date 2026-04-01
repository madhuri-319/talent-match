from google.adk.agents import Agent

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
    - Otherwise → ask for clarification
    """
)