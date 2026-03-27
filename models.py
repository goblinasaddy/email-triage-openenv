from openenv_core.env_server import Action, Observation, State

class EmailAction(Action):
    category: str
    priority: str
    response: str
    escalate: bool = False

class EmailObservation(Observation):
    email_text: str
    sender: str
    subject: str
    history: list[str]
    done: bool = False
    reward: float | None = None

class EmailState(State):
    correct_category: str
    correct_priority: str
    expected_keywords: list[str]
