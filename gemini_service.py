import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-3.6-flash")
with open("prompt.txt", "r", encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()

def get_decision(short_description: str, description: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(
        short_description=short_description,
        description=description
    )

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()

    decision_data = json.loads(raw_text)
    return decision_data

if __name__ == "__main__":
    result = get_decision(
        short_description="Request: annual leave approval",
        description="I would like to take next week off."
    )
    print(result)