import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_fields_from_text(text, model="gpt-4o"):
    system_msg = "You are a helpful assistant that extracts structured resume information."

    prompt = f"""
Score this candidate's resume on the following criteria:
1. Technical Capabilities (0–15)
2. Aligned to Arcadis Values (0–15)
3. Prior Experience (0–10)
4. Resume Quality/Flow (0–10)
5. Degree Alignment (0–20)
Given the text below, extract the following details:
- Full Name
- Email Address
- Phone Number
- Latest University
- Degree (e.g., BS, MS)
- Major
- Graduation Date
- Previous University (if any)
- Met on Campus (true/false)
- Campus Score (1, 2, 3, or "Not Captured")
- Cities/States of interest mentioned

Respond ONLY in valid JSON — no markdown code block, no extra comments.

TEXT:
{text}
"""

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
    )

    try:
        content = response['choices'][0]['message']['content']
        if content.strip().startswith("```"):
            content = content.strip().strip("`").strip("json").strip()
        return json.loads(content)
    except Exception as e:
        return {"error": str(e), "raw_output": content}
