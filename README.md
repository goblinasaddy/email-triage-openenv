# Email Triage OpenEnv Project

This project implements a complete OpenEnv environment for simulating a real-world email triage and response system. 

It is designed to evaluate an AI agent's ability to classify, prioritize, and generate appropriate responses to incoming emails.

## Project Structure

* **models.py**: Contains all the Pydantic data models for `EmailAction`, `EmailObservation`, and `EmailState`.
* **client.py**: Implements the `EmailEnvClient` pointing correctly to the backend server.
* **server/environment.py**: The OpenEnv Environment backend implementation.
* **server/app.py**: A FastAPI wrapper exposing the simulated environment endpoints.
* **server/Dockerfile**: Contains instructions for building the Docker image to deploy the FastAPI server.
* **tasks/**: Contains multiple JSON tasks (Easy, Medium, and Hard). 
* **graders/grader.py**: Module verifying responses based on string similarity and basic string checks, providing specific penalties and scores.
* **scripts/run_baseline.py**: Connects to the LLM (OpenAI) to parse tasks automatically and interact with the OpenEnv ecosystem.
* **openenv.yaml** & **pyproject.toml** & **requirements.txt**: Project metadata, dependencies, and settings.

## Setup Instructions

Ensure you have Python 3.11+ installed. I recommend using a virtual environment.

```bash
# Optional but recommended step
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Running Locally

To run the simulation server manually using your host machine instead of docker, use:

```bash
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
```
Then run the baseline evaluation loop:

```bash
# set your OpenAI API Key securely
export OPENAI_API_KEY="your-api-key-here"

# Execute
python scripts/run_baseline.py
```

### How to Test
A test loop can be achieved locally by observing standard standard environment behavior locally in python:

```python
from server.environment import EmailEnvironment
from models import EmailAction

env = EmailEnvironment()
obs = env.reset()
print(obs)
action = EmailAction(category="spam", priority="low", response="Delete")
next_obs = env.step(action)
print(f"Reward: {next_obs.reward}")
```

### How to Deploy (Docker)

To deploy using Docker:

```bash
docker build -t email-triage-env -f server/Dockerfile .

# Run the docker container
docker run -p 8000:8000 email-triage-env
```

### Deploying to Hugging Face Spaces

1. Create a new "Docker" Space on Hugging Face.
2. Clone your Space repository locally.
3. Copy all files from this project into the target Space folder.
4. Verify you pushed the whole hierarchy including `server/Dockerfile`. Adjust Hugging Face specific port requirements inside Space configs if necessary (by default Spaces exposes port 7860, not 8000, modify `EXPOSE 8000` to `7860` in `Dockerfile` for HuggingFace support, and swap out the `-port` arg appropriately).
5. Push to sync the git branch which triggers build automatically.

## Sample Evaluation Output
```
Starting baseline evaluation on http://localhost:8000...
--- Task 1 ---
Task 1 Score: 1.0
--- Task 2 ---
Task 2 Score: 0.95
--- Task 3 ---
Task 3 Score: 0.89

Average score: 0.94
```
