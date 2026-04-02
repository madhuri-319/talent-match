import json

from resumeiq.schemas.job_schema import JobPostingSchema

class RequisitionAgent:
    def __init__(self, api_key: str):
        # Initializing directly here for the test script
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=(
            "You are an HR data extractor. Extract details into JSON using these EXACT keys: "
            "job_title, department, location, job_type, experience_required, technical_skills. "
            "Return ONLY the JSON object."
        )
)

    def extract_job_details(self, raw_prompt: str):
        response = self.model.generate_content(
            raw_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        # Validates against your Pydantic schema
        return JobPostingSchema.model_validate_json(response.text)

# --- TEST BLOCK ---
if __name__ == "__main__":
    # 1. Mock the API Key (or pull from os.environ)
    import os
    TEST_KEY = "AIzaSyCcfUaftY2UDAgzzdTeDuD7QsPXxk-SgEY" 
    
    # 2. Initialize Agent
    test_agent = RequisitionAgent(api_key=TEST_KEY)
    
    # 3. Test Input
    test_prompt = "Hiring a QA Engineer in Pune, 3 years exp, Selenium and Java required."
    
    # 4. Execute and Print
    try:
        result = test_agent.extract_job_details(test_prompt)
        print("Successfully extracted JSON:")
        print(result.model_dump_json(indent=4))
    except Exception as e:
        print(f"Error during test: {e}")