import requests
from typing import Dict, Any, Optional
from openenv_core.client import EnvClient
from models import EmailObservation, EmailAction, EmailState

class EmailEnvClient(EnvClient):
    """Client for the Email Triage OpenEnv environment."""

    def _step_payload(self, action: EmailAction) -> dict:
        """Map the action object to dictionary for JSON serialization."""
        return action.model_dump()

    def _parse_result(self, result: dict) -> EmailObservation:
        """Parse environment observation from API response."""
        return EmailObservation(**result)

    def _parse_state(self, result: dict) -> EmailState:
        """Parse environment state from API response."""
        return EmailState(**result)
