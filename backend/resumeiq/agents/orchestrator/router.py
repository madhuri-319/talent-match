"""
Router - Handles request routing logic for orchestrator.
"""

import logging
from enum import Enum
from typing import Any, Dict

logger = logging.getLogger(__name__)


class RequestType(Enum):
    """Enumeration of supported request types."""

    PARSE_RESUME = "parse_resume"
    MATCH_JOBS = "match_jobs"
    SUBMIT_APPLICATION = "submit_application"
    CREATE_REQUISITION = "create_requisition"


class Router:
    """Route requests to appropriate agents."""

    def __init__(self):
        """Initialize the router."""
        self.routes = {
            RequestType.PARSE_RESUME: "resume_parser",
            RequestType.MATCH_JOBS: "job_matching",
            RequestType.SUBMIT_APPLICATION: "application",
            RequestType.CREATE_REQUISITION: "requisition",
        }

    def get_destination_agent(self, request_type: str) -> str:
        """
        Determine which agent should handle the request.

        Args:
            request_type: Type of request

        Returns:
            Name of the destination agent
        """
        try:
            req_type = RequestType(request_type)
            return self.routes.get(req_type)
        except ValueError:
            logger.error(f"Unknown request type: {request_type}")
            return None
