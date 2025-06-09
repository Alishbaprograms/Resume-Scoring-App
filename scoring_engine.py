# import pandas as pd
# import os
# import re

# def load_cam_weights(filepath="scoring/cam_weights.xlsx"):
#     df = pd.read_excel(filepath)
#     weights = {row["Criteria"]: row["Weight"] for _, row in df.iterrows()}
#     return weights

# def score_resume(text, weights):
#     score = 0

#     if "python" or "programming" in text.lower() or "revit" in text.lower():
#         score += weights.get("Technical Capabilities", 0)

#     if re.search(r"sustainab|integrity|collaborat", text.lower()):
#         score += weights.get("Aligned to Arcadis Values", 0)

#     if re.search(r"internship|co-op|research|project|engineer", text.lower()):
#         score += weights.get("Prior Experience", 0)

#     if len(text.split()) > 200:
#         score += weights.get("Resume Quality/Flow", 0)

#     if re.search(r"civil|environmental|structural|geotechnical", text.lower()):
#         score += weights.get("Degree Alignment", 0)

#     return score
import openai, os, json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def score_resume_ai(text):
    messages = [
        {"role": "system", "content": "You are an expert resume evaluator for Arcadis."},
        {"role": "user", "content": f"""
Score this candidate's resume on the following criteria:
1. Technical Capabilities (0–15)
2. Aligned to Arcadis Values (0–15)
3. Prior Experience (0–10)
4. Resume Quality/Flow (0–10)
5. Degree Alignment (0–20)

Resume:
{text}

Return JSON like:
{{
  "Technical Capabilities": ...,
  "Aligned to Arcadis Values": ...,
  "Prior Experience": ...,
  "Resume Quality/Flow": ...,
  "Degree Alignment": ...,
  "Total CAM Score": ...
}}
"""}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages
    )

    try:
        content = response['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        return {"error": str(e), "raw": response['choices'][0]['message']['content']}
