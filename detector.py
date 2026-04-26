import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from math import radians, sin, cos, sqrt, atan2
from parser import parse_uploaded_logs
import os

# =========================================================
# VEILGuard - Detection Engine
# Rule-Based Detection + Isolation Forest + Risk Scoring
# =========================================================

DATA_PATH = "data/synthetic_logs.csv"
OUTPUT_PATH = "data/detected_alerts.csv"


# ---------------------------------------------------------
# Haversine Formula
# ---------------------------------------------------------

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two geo locations in KM
    """

    R = 6371  # Earth radius in KM

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------

def load_data():
    print("Loading uploaded enterprise logs...")

    os.makedirs("data", exist_ok=True)

    file_path = "data/synthetic_logs.csv"

    if not os.path.exists(file_path):
        print("Input file not found:", file_path)
        return pd.DataFrame()

    df = parse_uploaded_logs(file_path)

    if df.empty:
        print("No valid logs found after parsing.")
        return pd.DataFrame()

    # Force timestamp conversion safely
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        df = df.dropna(subset=["timestamp"])

    print(f"Loaded {len(df)} records successfully.")

    return df

# =========================================================
# VEILGuard — Flexible Log Parser Layer
# Add this near helper functions in veilguard.py or detector.py
# =========================================================

def normalize_uploaded_logs(df):
    """
    Makes uploaded enterprise logs flexible by auto-mapping
    common enterprise column names into VEILGuard schema.
    This prevents recruiter/company uploads from breaking.
    """

    # -----------------------------------------------------
    # Common real-world aliases → VEILGuard standard schema
    # -----------------------------------------------------

    column_map = {
        # user
        "username": "user_id",
        "user": "user_id",
        "employee_id": "user_id",

        # time
        "time": "timestamp",
        "event_time": "timestamp",
        "login_time": "timestamp",

        # action
        "event": "action",
        "activity": "action",
        "operation": "action",

        # place
        "city": "location",
        "geo_location": "location",
        "ip_location": "location",

        # machine
        "host": "device",
        "machine": "device",
        "system": "device",

        # file
        "file": "file_path",
        "filename": "file_path",
        "resource": "file_path",

        # security
        "sensitivity": "file_sensitivity",
        "access_level": "privilege_level",
        "role": "privilege_level",

        # geo
        "lat": "latitude",
        "lon": "longitude",
        "lng": "longitude",

        # ml feature
        "download_size": "download_size_mb",
        "file_size_mb": "download_size_mb",
    }

    # lowercase cleanup
    df.columns = [str(col).strip().lower() for col in df.columns]

    # rename matching aliases
    for old_col, new_col in column_map.items():
        if old_col in df.columns and new_col not in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)

    # -----------------------------------------------------
    # Required fallback defaults
    # -----------------------------------------------------

    required_defaults = {
        "user_id": "UNKNOWN_USER",
        "timestamp": pd.Timestamp.now(),
        "action": "login",
        "location": "Unknown",
        "device": "Unknown Device",
        "file_path": "general_access.log",
        "file_sensitivity": "Medium",
        "privilege_level": "User",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "download_size_mb": 0,
        "login_hour": 12,
        "failed_login_attempts": 0,
        "usb_usage": 0,
        "vpn_used": 0,
        "after_hours_access": 0,
        "sensitive_file_access_count": 0,
        "risk_score": 0,
        "severity": "Low"
    }

    for col, default_value in required_defaults.items():
        if col not in df.columns:
            df[col] = default_value

    # derive login hour if timestamp exists
    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["login_hour"] = df["timestamp"].dt.hour.fillna(12)
        df["after_hours_access"] = (
            (df["login_hour"] < 6) |
            (df["login_hour"] > 22)
        ).astype(int)
    except Exception:
        pass

    return df


# =========================================================
# HOW TO USE
# =========================================================
# Replace this:
# df = pd.read_csv(DATA_PATH)
#
# With this:
# df = pd.read_csv(DATA_PATH)
# df = normalize_uploaded_logs(df)
# =========================================================

# ---------------------------------------------------------
# Rule-Based Detection Engine
# ---------------------------------------------------------

def detect_rule_based_anomalies(df):
    print("Running rule-based detection engine...")

    df["off_hours_flag"] = 0
    df["sensitive_access_flag"] = 0
    df["privilege_misuse_flag"] = 0
    df["device_anomaly_flag"] = 0
    df["impossible_travel_flag"] = 0

    # -------------------------
    # 1. Off-Hours Access
    # -------------------------
    df.loc[
        (df["timestamp"].dt.hour < 6) |
        (df["timestamp"].dt.hour > 22),
        "off_hours_flag"
    ] = 1

    # -------------------------
    # 2. Sensitive File Access
    # -------------------------
    df.loc[
        df["file_sensitivity"].isin(["High", "Critical"]),
        "sensitive_access_flag"
    ] = 1

    # -------------------------
    # 3. Privilege Misuse
    # -------------------------
    df.loc[
        (df["action"] == "privilege_request") &
        (df["privilege_level"] == "Admin"),
        "privilege_misuse_flag"
    ] = 1

    # -------------------------
    # 4. Device Anomaly
    # Example: Linux Workstation access
    # -------------------------
    df.loc[
        df["device"] == "Linux Workstation",
        "device_anomaly_flag"
    ] = 1

    # -------------------------
    # 5. Impossible Travel
    # Compare consecutive logins per user
    # -------------------------
    df = df.sort_values(["user_id", "timestamp"])

    previous_locations = {}

    for index, row in df.iterrows():
        user = row["user_id"]

        current_location = (
            row["latitude"],
            row["longitude"],
            row["timestamp"]
        )

        if user in previous_locations:
            prev_lat, prev_lon, prev_time = previous_locations[user]

            distance = haversine_distance(
                prev_lat,
                prev_lon,
                row["latitude"],
                row["longitude"]
            )

            time_diff_hours = abs(
                (row["timestamp"] - prev_time).total_seconds()
            ) / 3600

            if time_diff_hours > 0:
                speed = distance / time_diff_hours

                # unrealistic travel threshold
                if speed > 1000:
                    df.at[index, "impossible_travel_flag"] = 1

        previous_locations[user] = current_location

    return df


# ---------------------------------------------------------
# Isolation Forest ML Detection
# ---------------------------------------------------------

def run_isolation_forest(df):
    print("Running Isolation Forest anomaly detection...")

    feature_columns = [
        "download_size_mb",
        "off_hours_flag",
        "sensitive_access_flag",
        "privilege_misuse_flag",
        "device_anomaly_flag",
        "impossible_travel_flag"
    ]

    X = df[feature_columns].fillna(0)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    model.fit(X)

    df["ml_anomaly"] = model.predict(X)

    # Convert:
    # -1 = anomaly
    #  1 = normal

    df["ml_anomaly_flag"] = df["ml_anomaly"].apply(
        lambda x: 1 if x == -1 else 0
    )

    return df


# ---------------------------------------------------------
# Risk Score Engine
# ---------------------------------------------------------

def calculate_risk_score(df):
    print("Calculating risk scores...")

    # =====================================================
    # STEP 1: RAW SCORE CALCULATION
    # (before normalization)
    # =====================================================

    df["raw_score"] = 0

    # ---------------------------------
    # Base behavioral anomaly scoring
    # ---------------------------------

    df["raw_score"] += df["off_hours_flag"] * 20
    df["raw_score"] += df["sensitive_access_flag"] * 30
    df["raw_score"] += df["privilege_misuse_flag"] * 35
    df["raw_score"] += df["device_anomaly_flag"] * 15
    df["raw_score"] += df["impossible_travel_flag"] * 40
    df["raw_score"] += df["ml_anomaly_flag"] * 25

    # ---------------------------------
    # Dynamic scoring for large downloads
    # More realistic than fixed scoring
    # ---------------------------------

    if "download_size_mb" in df.columns:
        df["raw_score"] += (
            df["download_size_mb"]
            .fillna(0)
            .astype(float) / 100
        ).clip(upper=35)

    # ---------------------------------
    # Critical action boost
    # High-risk administrative actions
    # ---------------------------------

    critical_actions = [
        "admin_access",
        "delete_logs",
        "bulk_export",
        "database_export",
        "usb_copy",
        "repository_clone",
        "privilege_escalation",
        "terminated_user_access",
        "credential_dump",
        "sensitive_export"
    ]

    if "action" in df.columns:
        df.loc[
            df["action"].astype(str).str.lower().isin(critical_actions),
            "raw_score"
        ] += 30

    # ---------------------------------
    # Sensitive file keyword boost
    # Detect critical enterprise assets
    # ---------------------------------

    if "file_path" in df.columns:

        sensitive_keywords = [
            "payroll",
            "salary",
            "credential",
            "admin",
            "backup",
            "source_code",
            "database",
            "customer",
            "pii",
            "finance",
            "confidential",
            "encryption",
            "master_keys",
            "domain_admin",
            "siem",
            "audit"
        ]

        for keyword in sensitive_keywords:
            df.loc[
                df["file_path"]
                .astype(str)
                .str.lower()
                .str.contains(
                    keyword,
                    na=False
                ),
                "raw_score"
            ] += 5

    # =====================================================
    # STEP 2: NORMALIZATION TO 0–100 SCALE
    # Enterprise-grade standardized scoring
    # =====================================================

    MAX_POSSIBLE_SCORE = 120

    df["risk_score"] = (
        (df["raw_score"] / MAX_POSSIBLE_SCORE) * 100
    )

    # ---------------------------------
    # Soft Cap instead of Hard Clip
    # Makes scores realistic
    # ---------------------------------

    df["risk_score"] = df["risk_score"].apply(
        lambda x: (
            round(
                85 + ((x - 85) * 0.35),
                1
            )
            if x > 85 else round(x, 1)
        )
    )

    # Final absolute safety cap
    df["risk_score"] = df["risk_score"].clip(
        upper=99.8
    )
    # =====================================================
    # STEP 3: SEVERITY MAPPING
    # =====================================================

    def severity(score):
        if score >= 80:
            return "Critical"
        elif score >= 60:
            return "High"
        elif score >= 35:
            return "Medium"
        else:
            return "Low"

    df["severity"] = df["risk_score"].apply(severity)

    # =====================================================
    # STEP 4: ALERT FLAG
    # Used for dashboard + reports
    # =====================================================

    df["is_alert"] = df["risk_score"].apply(
        lambda x: 1 if x >= 35 else 0
    )

    return df

# ---------------------------------------------------------
# Save Alerts
# ---------------------------------------------------------

def save_alerts(df):
    print("Saving detected alerts...")

    alerts = df[df["risk_score"] >= 25].copy()

    alerts.to_csv(OUTPUT_PATH, index=False)

    return len(alerts)

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    print("\n======================================")
    print("VEILGuard Detection Engine Started")
    print("======================================")

    df = load_data()

    if df.empty:
        print("No valid logs found.")
        return

    df = detect_rule_based_anomalies(df)

    df = run_isolation_forest(df)

    df = calculate_risk_score(df)

    total_alerts = save_alerts(df)

    print("\n======================================")
    print("VEILGuard Detection Engine Completed")
    print("======================================")
    print(f"Total Records Processed: {len(df)}")
    print(f"Alerts Generated: {total_alerts}")
    print(f"Saved To: {OUTPUT_PATH}")
    print("======================================")


if __name__ == "__main__":
    main()