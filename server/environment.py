import os
import json
import logging
from typing import Optional
from openenv_core import Environment

from models import EmailAction, EmailObservation, EmailState
from graders.grader import grade_action

class EmailEnvironment(Environment):
    """OpenEnv Email Triage Environment."""

    def __init__(self):
        super().__init__()
        self._tasks = []
        self._task_index = 0
        self._current_state: Optional[EmailState] = None
        self._last_response = None
        self._load_tasks()

    def _load_tasks(self):
        task_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks")
        for filename in ["task_easy.json", "task_medium.json", "task_hard.json"]:
            path = os.path.join(task_dir, filename)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self._tasks.append(json.load(f))
        
        if not self._tasks:
            logging.warning("No tasks loaded for EmailEnvironment.")

    def reset(self) -> EmailObservation:
        """Loads next task, initializes state, returns the observation."""
        if not self._tasks:
            raise RuntimeError("Cannot reset without tasks loaded.")
            
        task = self._tasks[self._task_index]
        self._task_index = (self._task_index + 1) % len(self._tasks)
        
        # Initialize internal state
        # The base State normally takes an id, here we just use what was defined in our models.py
        self._current_state = EmailState(
            correct_category=task["correct_category"],
            correct_priority=task["correct_priority"],
            expected_keywords=task["expected_keywords"]
        )
        self._last_response = None
        
        return EmailObservation(
            email_text=task["email_text"],
            sender=task["sender"],
            subject=task["subject"],
            history=[]
        )

    def step(self, action: EmailAction) -> dict:
        """Call grader, compute reward, update state, and return one-step output."""
        if self._current_state is None:
            raise RuntimeError("Environment not reset")
            
        reward = grade_action(action, self._current_state, self._last_response)
        self._last_response = action.response

        # Escalate logics
        if action.escalate and self._current_state.correct_category.lower() == "important":
            reward += 0.1
        elif action.escalate:
            reward -= 0.1

        # Reward boundary [0.0, 1.0]
        reward = float(max(0.0, min(1.0, reward)))
        
        idx = (self._task_index - 1) % len(self._tasks)
        task = self._tasks[idx]

        history_item = f"Action - Category: {action.category}, Priority: {action.priority}, Response: {action.response}, Escalate: {action.escalate}"

        obs = EmailObservation(
            email_text=task["email_text"],
            sender=task["sender"],
            subject=task["subject"],
            history=[history_item]
        )
        # Fast API often needs python dict mappings for typical openenv returns depending on the wrapper interface
        result = obs.model_dump()
        result["reward"] = reward
        result["done"] = True
        return result

    @property
    def state(self) -> EmailState:
        return self._current_state
