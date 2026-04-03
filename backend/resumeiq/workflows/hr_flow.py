from agents.hr_agents.requisition.agent import RequisitionAgent
from tools.db_tool import save_job_to_mongo # Assuming this is in your db_tool

def run_hr_requisition_flow(hr_input: str):
    agent = RequisitionAgent()
    
    # 1. Extract contextually
    job_data = agent.extract_job_details(hr_input)
    
    # 2. Convert Pydantic to Dict/JSON
    job_json = job_data.model_dump()
    
    # 3. Optional: Save to DB
    # save_job_to_mongo(job_json)
    
    return job_json