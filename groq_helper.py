from groq import Groq
from dotenv import load_dotenv
import os
import pandas as pd

# =========================================================
# VEILGuard - Groq AI Engine
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(
    api_key=GROQ_API_KEY
)

# =========================================================
# AI Alert Explanation
# =========================================================

def generate_alert_explanation(alert_data):

    try:
        # Safe extraction if alert_data is a dictionary / row object
        user_id = str(alert_data.get("user_id", "UNKNOWN"))
        severity = str(alert_data.get("severity", "Unknown"))
        risk_score = str(alert_data.get("risk_score", "0"))
        action = str(alert_data.get("action", "Unknown"))
        location = str(alert_data.get("location", "Unknown"))
        device = str(alert_data.get("device", "Unknown"))
        file_path = str(alert_data.get("file_path", "N/A"))

        # Generate proper Alert ID
        try:
            score_value = float(alert_data.get("risk_score", 0))
        except:
            score_value = 0

        alert_id = f"VG-{user_id[:3].upper()}-{int(score_value * 10)}"

        # Safe timestamp handling
        try:
            timestamp = pd.to_datetime(alert_data.get("timestamp"))
            alert_date = str(timestamp.date())
            alert_time = str(timestamp.strftime("%H:%M:%S"))
        except:
            alert_date = "N/A"
            alert_time = "N/A"

        prompt = f"""
You are a Senior SOC Analyst working in an enterprise cybersecurity team.

Generate a professional SOC Investigation Report.

STRICT RULES:
- Do NOT use placeholders like [Insert Alert ID]
- Do NOT use placeholders like [Insert Date]
- Do NOT use placeholders like [Insert Time]
- Do NOT invent analyst names
- Use exact values provided below
- Use professional cybersecurity language
- Keep it concise, executive-level, and enterprise-grade

Use these exact values:

Alert ID: {alert_id}
Date: {alert_date}
Time: {alert_time}
Analyst Name: VEILGuard AI SOC Analyst

User: {user_id}
Severity: {severity}
Risk Score: {risk_score}
Suspicious Action: {action}
Location: {location}
Device: {device}
File Accessed: {file_path}

Explain:

1. Why this behavior is suspicious
2. What potential insider threat it may indicate
3. Recommended immediate actions

Write like a real enterprise SOC analyst report.
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert cybersecurity SOC analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=700
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Groq Error: {str(e)}"


# =========================================================
# What-If Insider Attack Simulation
# =========================================================

def generate_attack_simulation(user_id, scenario):

    prompt = f"""
You are a cybersecurity threat modeling expert.

Generate a realistic malicious insider attack chain for:

User: {user_id}
Scenario: {scenario}

Requirements:
- 5 to 7 realistic attack steps
- step-by-step progression
- insider threat focused
- professional security language
- include mitigation recommendations
- enterprise-grade quality

Make it realistic and suitable for SOC review.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert insider threat simulation analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=700
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Groq Error: {str(e)}"
