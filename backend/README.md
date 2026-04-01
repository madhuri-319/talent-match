# ResumeIQ - AI-Powered Recruitment Agent System

## Overview

ResumeIQ is an intelligent recruitment matching system powered by AI agents. It uses LLMs and semantic search to match candidates with job opportunities, automate resume parsing, and streamline the hiring process.

## Architecture

### Core Components

**Agents**
- **Orchestrator**: Root agent that routes requests to specialized sub-agents
- **User Agents**: Handle candidate-side operations (resume parsing, job matching, applications)
- **HR Agents**: Handle HR-side operations (requisition management, candidate review)

**Workflows**
- Resume Flow: Upload → Parse → Validate → Store
- HR Flow: Requisition → Candidate Review → Interview → Offer

**Tools**
- LLM Client: Interface to language models
- Database Tool: Persistent data storage
- Embedding Tool: Semantic search and similarity matching

**Infrastructure**
- FastAPI: REST API server
- Pydantic: Data validation and schemas
- LangChain/LangGraph: Agent orchestration

## Project Structure

```
resumeiq/
├── agents/                 # AI agents
│   ├── orchestrator/      # Main routing agent
│   ├── user_agents/       # Candidate-side agents
│   └── hr_agents/         # HR-side agents
├── tools/                 # Shared utilities
├── workflows/             # Flow definitions
├── schemas/               # Data models
├── config/                # Configuration
├── observability/         # Logging & tracing
├── api/                   # FastAPI routes
└── tests/                 # Test suite
```

## Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL (or SQLite for development)
- OpenAI API key (or compatible LLM)

### Installation

1. Clone the repository
```bash
cd backend
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run the application
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

### Key Endpoints

**Resume Operations**
- `POST /api/v1/resume/parse` - Parse resume
- `GET /api/v1/candidates/{id}/resume` - Retrieve resume

**Job Matching**
- `POST /api/v1/jobs/match` - Find matching jobs
- `GET /api/v1/jobs/{id}` - Get job details

**Applications**
- `POST /api/v1/applications` - Submit application
- `GET /api/v1/applications/{id}/status` - Check status

**HR Operations**
- `POST /api/v1/requisitions` - Create requisition
- `GET /api/v1/requisitions/{id}/candidates` - View candidates

## Configuration

Settings are managed through environment variables. See `.env.example` for all available options.

## Development

### Running Tests
```bash
pytest
```

### Code Style
```bash
black .
flake8 .
mypy .
```

## Future Enhancements

- [ ] Multi-language support
- [ ] Advanced skill extraction
- [ ] Interview scheduling automation
- [ ] Offer letter generation
- [ ] Analytics dashboard
- [ ] Real-time notifications

## License

Proprietary - ResumeIQ 2024

## Support

For issues and questions, please contact the development team.
