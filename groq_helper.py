from groq import Groq
import os

# =========================================================
# VEILGuard - Groq AI Engine
# =========================================================

from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =========================================================
# AI Alert Explanation
# =========================================================

def generate_alert_explanation(alert_data):

    prompt = f"""
You are a Senior SOC Analyst working in an enterprise cybersecurity team.

Analyze the following suspicious insider threat alert and explain:

1. Why this behavior is suspicious
2. What potential insider threat it may indicate
3. Recommended immediate actions

Alert Data:
{alert_data}

Write the response professionally like a real SOC analyst report.
Keep it concise but impactful.
"""

    try:
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
            max_tokens=500
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

Make it realistic and enterprise-grade.
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