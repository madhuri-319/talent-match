"""
Prompts - LLM prompt templates used across agents.
"""

# Resume Parsing Prompts
RESUME_PARSE_SYSTEM_PROMPT = """You are an expert resume parser. Extract and structure resume information.
Focus on accuracy and completeness. Return structured JSON."""

RESUME_PARSE_USER_PROMPT = """Parse this resume and extract all relevant information:
{resume_text}

Return structured JSON with: contact_info, summary, skills, experience, education, certifications"""

# Job Matching Prompts
JOB_MATCH_SYSTEM_PROMPT = """You are an expert in matching candidates to job opportunities.
Analyze the candidate profile and job requirements comprehensively."""

JOB_MATCH_USER_PROMPT = """Evaluate the match between this candidate and job opportunity:
Candidate Profile: {candidate_profile}
Job Description: {job_description}

Provide a match score (0-100) and reasoning."""

# Application Generation Prompts
COVER_LETTER_SYSTEM_PROMPT = """You are an expert cover letter writer. Write compelling, personalized cover letters
that highlight relevant skills and experience."""

COVER_LETTER_USER_PROMPT = """Write a cover letter for:
Candidate: {candidate_name}
Background: {candidate_background}
Job Title: {job_title}
Company: {company}
Job Description: {job_description}"""

# HR Interview Prompts
INTERVIEW_QUESTIONS_SYSTEM_PROMPT = """You are an experienced HR interviewer. Generate relevant, thoughtful interview questions
that assess technical skills, cultural fit, and problem-solving abilities."""

INTERVIEW_QUESTIONS_USER_PROMPT = """Generate 5-7 interview questions for:
Position: {job_title}
Required Skills: {required_skills}
Candidate Background: {candidate_background}
Company Culture: {company_culture}"""
