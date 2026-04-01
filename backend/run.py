#!/usr/bin/env python
"""
ResumeIQ Application Entry Point
Starts the FastAPI server and initializes all components.
"""

import logging
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from resumeiq.config.settings import settings
from resumeiq.observability.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main entry point for the application."""
    logger.info("Starting ResumeIQ application...")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")

    # Start FastAPI server
    uvicorn.run(
        "resumeiq.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)
