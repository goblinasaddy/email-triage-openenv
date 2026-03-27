import os
import json
import re
import logging
import sys
import google.generativeai as genai

# Add top level path to access models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client import EmailEnvClient
from models import EmailAction

# Setup minimal logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def extract_json(text):
    match = re.search(r"{.*}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {"category": "normal", "priority": "medium", "response": ""}

def baseline_eval():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("Required GEMINI_API_KEY environment variable not set.")
        return

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    host_url = os.environ.get("OPENENV_HOST", "http://localhost:8000")
    print(f"Starting baseline evaluation on {host_url}")

    client = None
    try:
        client = EmailEnvClient(host_url)
        # Attempt minimal server connection
        client.reset() 
    except Exception as e:
        print(f"Skipping remote env due to {e}. Falling back to inline env engine if available.")
        client = None

    if client:
        # Use remote api explicitly
        env = client
    else:
        # Direct local invocation fallback
        from server.environment import EmailEnvironment
        env = EmailEnvironment()

    total_score = 0
    tasks_count = 3

    for i in range(tasks_count):
        print(f"--- Task {i + 1} ---")
        try:
            obs = env.reset()
        except Exception as e:
            print(f"Error resetting environment: {e}")
            break

        # In case it's a raw dict from API fallback
        if isinstance(obs, dict):
            from models import EmailObservation
            obs = EmailObservation(**obs)

        prompt = f"""You are an email triage agent.
Subject: {obs.subject}
From: {obs.sender}
Body: {obs.email_text}

Analyze the email and output exactly four things in JSON format:
1. "category": ("spam", "important", or "normal")
2. "priority": ("low", "medium", "high")
3. "response": The drafted reply to this email.
4. "escalate": (boolean) Also include a boolean field 'escalate' if this email should be escalated to a manager.

ONLY output valid JSON. No other text."""

        try:
            response = model.generate_content(prompt)
            text = response.text
            
            output_dict = extract_json(text)
            
            action = EmailAction(
                category=output_dict.get("category", "normal"),
                priority=output_dict.get("priority", "medium"),
                response=output_dict.get("response", ""),
                escalate=output_dict.get("escalate", False)
            )
        except Exception as e:
            print(f"Error calling Gemini API or parsing: {e}")
            action = EmailAction(category="normal", priority="medium", response="")

        try:
            step_obs = env.step(action)
            # Fetching from dictionary or proper Observation payload wrapper
            score = step_obs.get('reward') if isinstance(step_obs, dict) else getattr(step_obs, 'reward', 0.0)
            if score is None:
                score = 0.0
        except Exception as e:
            print(f"Error stepping environment: {e}")
            score = 0.0

        print(f"Score for Task {i + 1}: {score}")
        total_score += score

    print(f"\nAverage Score: {total_score / tasks_count:.2f}")

if __name__ == "__main__":
    baseline_eval()
