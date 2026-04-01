"""
Configuration for the orchestrator agent.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class OrchestratorConfig:
    """Configuration settings for orchestrator."""

    max_retries: int = 3
    timeout_seconds: int = 300
    enable_feedback_loop: bool = True
    agent_configs: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values if not provided."""
        if self.agent_configs is None:
            self.agent_configs = {}
