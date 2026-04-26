import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# =========================================================
# VEILGuard - Synthetic Data Generator
# AI-Powered Insider Risk Detection & Proactive Threat Simulation
# =========================================================


# -------------------------------
# CONFIGURATION
# -------------------------------

NUM_USERS = 100
DAYS_OF_DATA = 30
MALICIOUS_PERCENTAGE = 15

OUTPUT_FILE = "data/synthetic_logs.csv"


# -------------------------------
# SAMPLE DATA
# -------------------------------

departments = [
    "Finance",
    "HR",
    "Engineering",
    "Security",
    "Admin",
    "Sales"
]

devices = [
    "MacBook",
    "Windows Laptop",
    "Linux Workstation",
    "iPhone",
    "Android Phone"
]

locations = {
    "Bangalore": (12.9716, 77.5946),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.7041, 77.1025),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Singapore": (1.3521, 103.8198)
}

sensitive_files = [
    "payroll.xlsx",
    "employee_salary.csv",
    "client_database.zip",
    "financial_report.pdf",
    "confidential_strategy.docx"
]

normal_files = [
    "project_notes.txt",
    "meeting_minutes.docx",
    "presentation.pptx",
    "training_material.pdf",
    "task_list.xlsx"
]

actions = [
    "login",
    "file_access",
    "download",
    "privilege_request",
    "logout"
]

privilege_levels = [
    "User",
    "Analyst",
    "Manager",
    "Admin"
]


# -------------------------------
# USER GENERATION
# -------------------------------

def generate_users(num_users):
    users = []

    for i in range(1, num_users + 1):
        user_id = f"USER_{i:03}"

        department = random.choice(departments)
        device = random.choice(devices)
        location = random.choice(list(locations.keys()))
        privilege = random.choice(["User", "Analyst", "Manager"])

        users.append({
            "user_id": user_id,
            "department": department,
            "usual_device": device,
            "usual_location": location,
            "usual_privilege": privilege
        })

    return users


# -------------------------------
# NORMAL ACTIVITY GENERATION
# -------------------------------

def generate_normal_activity(user, days):
    logs = []

    base_date = datetime.now() - timedelta(days=days)

    for day in range(days):
        daily_events = random.randint(3, 8)

        for _ in range(daily_events):
            timestamp = base_date + timedelta(
                days=day,
                hours=random.randint(9, 18),
                minutes=random.randint(0, 59)
            )

            action = random.choice(actions)

            file_path = random.choice(normal_files)
            file_sensitivity = "Low"

            location = user["usual_location"]
            latitude, longitude = locations[location]

            logs.append({
                "user_id": user["user_id"],
                "timestamp": timestamp,
                "action": action,
                "device": user["usual_device"],
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
                "file_path": file_path,
                "file_sensitivity": file_sensitivity,
                "privilege_level": user["usual_privilege"],
                "department": user["department"],
                "download_size_mb": random.randint(1, 20),
                "login_status": "Success",
                "malicious_flag": 0
            })

    return logs


# -------------------------------
# MALICIOUS ACTIVITY GENERATION
# -------------------------------

def generate_malicious_activity(user):
    logs = []

    attack_type = random.choice([
        "impossible_travel",
        "off_hours_access",
        "sensitive_download",
        "privilege_misuse",
        "device_anomaly"
    ])

    timestamp = datetime.now() - timedelta(
        days=random.randint(1, 5),
        hours=random.randint(0, 23)
    )

    if attack_type == "impossible_travel":
        unusual_location = random.choice([
            "New York",
            "London",
            "Singapore"
        ])

        latitude, longitude = locations[unusual_location]

        logs.append({
            "user_id": user["user_id"],
            "timestamp": timestamp,
            "action": "login",
            "device": user["usual_device"],
            "location": unusual_location,
            "latitude": latitude,
            "longitude": longitude,
            "file_path": "N/A",
            "file_sensitivity": "N/A",
            "privilege_level": user["usual_privilege"],
            "department": user["department"],
            "download_size_mb": 0,
            "login_status": "Success",
            "malicious_flag": 1
        })

    elif attack_type == "off_hours_access":
        timestamp = timestamp.replace(hour=2, minute=15)

        file_path = random.choice(sensitive_files)

        location = user["usual_location"]
        latitude, longitude = locations[location]

        logs.append({
            "user_id": user["user_id"],
            "timestamp": timestamp,
            "action": "file_access",
            "device": user["usual_device"],
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "file_path": file_path,
            "file_sensitivity": "High",
            "privilege_level": user["usual_privilege"],
            "department": user["department"],
            "download_size_mb": random.randint(50, 200),
            "login_status": "Success",
            "malicious_flag": 1
        })

    elif attack_type == "sensitive_download":
        file_path = random.choice(sensitive_files)

        location = user["usual_location"]
        latitude, longitude = locations[location]

        logs.append({
            "user_id": user["user_id"],
            "timestamp": timestamp,
            "action": "download",
            "device": user["usual_device"],
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "file_path": file_path,
            "file_sensitivity": "Critical",
            "privilege_level": user["usual_privilege"],
            "department": user["department"],
            "download_size_mb": random.randint(100, 500),
            "login_status": "Success",
            "malicious_flag": 1
        })

    elif attack_type == "privilege_misuse":
        location = user["usual_location"]
        latitude, longitude = locations[location]

        logs.append({
            "user_id": user["user_id"],
            "timestamp": timestamp,
            "action": "privilege_request",
            "device": user["usual_device"],
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "file_path": "N/A",
            "file_sensitivity": "N/A",
            "privilege_level": "Admin",
            "department": user["department"],
            "download_size_mb": 0,
            "login_status": "Success",
            "malicious_flag": 1
        })

    elif attack_type == "device_anomaly":
        unusual_device = "Linux Workstation"

        location = user["usual_location"]
        latitude, longitude = locations[location]

        logs.append({
            "user_id": user["user_id"],
            "timestamp": timestamp,
            "action": "login",
            "device": unusual_device,
            "location": location,
            "latitude": latitude,
            "longitude": longitude,
            "file_path": "N/A",
            "file_sensitivity": "N/A",
            "privilege_level": user["usual_privilege"],
            "department": user["department"],
            "download_size_mb": 0,
            "login_status": "Success",
            "malicious_flag": 1
        })

    return logs


# -------------------------------
# MAIN GENERATOR
# -------------------------------

def generate_dataset():
    print("Generating synthetic users...")
    users = generate_users(NUM_USERS)

    all_logs = []

    print("Generating normal behavior logs...")
    for user in users:
        all_logs.extend(generate_normal_activity(user, DAYS_OF_DATA))

    print("Injecting malicious insider scenarios...")
    malicious_users_count = int(NUM_USERS * MALICIOUS_PERCENTAGE / 100)
    malicious_users = random.sample(users, malicious_users_count)

    for user in malicious_users:
        all_logs.extend(generate_malicious_activity(user))

    df = pd.DataFrame(all_logs)

    df = df.sort_values("timestamp").reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print("\n===================================")
    print("VEILGuard Synthetic Dataset Created")
    print("===================================")
    print(f"Total Records: {len(df)}")
    print(f"Malicious Users Injected: {malicious_users_count}")
    print(f"Saved To: {OUTPUT_FILE}")
    print("===================================\n")


# -------------------------------
# RUN
# -------------------------------

if __name__ == "__main__":
    generate_dataset()