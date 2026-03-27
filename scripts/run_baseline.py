import os
import json
import re
import logging
import requests
from google import genai

BASE_URL = "http://127.0.0.1:8000"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def extract_json(text):
    match = re.search(r"{.*}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return {"category": "normal", "priority": "medium", "response": "", "escalate": False}


def reset_env():
    response = requests.post(f"{BASE_URL}/reset")
    print("STATUS:", response.status_code)
    print("RAW:", response.text)   # 👈 IMPORTANT
    return response.json()


def step_env(action):
    return requests.post(f"{BASE_URL}/step", json=action).json()


def baseline_eval():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logging.error("GEMINI_API_KEY not set.")
        return

    # ✅ New Gemini SDK
    client = genai.Client(api_key=api_key)

    total_score = 0
    tasks_count = 3

    for i in range(tasks_count):
        print(f"\n--- Task {i + 1} ---")

        # ✅ Call API
        obs_data = reset_env()
        obs = obs_data["observation"]

        prompt = f"""You are an email triage agent.

Subject: {obs['subject']}
From: {obs['sender']}
Body: {obs['email_text']}

Return ONLY valid JSON:
{{
  "category": "spam | important | normal",
  "priority": "low | medium | high",
  "response": "email reply",
  "escalate": true or false
}}
"""

        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )

            text = response.text
            output = extract_json(text)

        except Exception as e:
            print(f"Gemini error: {e}")
            output = {"category": "normal", "priority": "medium", "response": "", "escalate": False}

        # ✅ Send to env
        result = step_env(output)

        score = result.get("reward", 0.0)
        print(f"Score: {score}")

        total_score += score

    print(f"\nAverage Score: {total_score / tasks_count:.2f}")


if __name__ == "__main__":
    baseline_eval()