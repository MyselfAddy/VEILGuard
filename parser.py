import pandas as pd
import os


def parse_uploaded_logs(file_path="data/synthetic_logs.csv"):
    """
    Converts any uploaded enterprise CSV
    into VEILGuard standard schema
    """

    if not os.path.exists(file_path):
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    # =====================================
    # POSSIBLE COLUMN NAME VARIATIONS
    # =====================================

    column_mapping = {
        "employee_name": "user_id",
        "event_time": "timestamp",
        "event_type": "action",
        "login_city": "location",
        "geo_lat": "latitude",
        "geo_long": "longitude",
        "endpoint_name": "device",
        "file_name": "file_path",
        "file_classification": "file_sensitivity",
        "download_volume_mb": "download_size_mb",
        "role": "privilege_level",
        "remarks": "remarks"
    }

    # Rename only existing columns
    df = df.rename(
        columns={
            k: v for k, v in column_mapping.items()
            if k in df.columns
        }
    )

    # =====================================
    # REQUIRED FALLBACK COLUMNS
    # =====================================

    required_columns = {
        "user_id": "Unknown_User",
        "timestamp": pd.Timestamp.now(),
        "action": "login",
        "location": "Unknown",
        "latitude": 0.0,
        "longitude": 0.0,
        "device": "Unknown_Device",
        "file_path": "N/A",
        "file_sensitivity": "Low",
        "download_size_mb": 0,
        "privilege_level": "User",
        "severity": "Low"
    }

    for col, default_value in required_columns.items():
        if col not in df.columns:
            df[col] = default_value

    # =====================================
    # DATETIME FIX
    # =====================================

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["timestamp"] = df["timestamp"].fillna(
        pd.Timestamp.now()
    )

    # =====================================
    # PRIVILEGE STANDARDIZATION
    # =====================================

    df["privilege_level"] = df["privilege_level"].replace({
        "System Admin": "Admin",
        "Cloud Administrator": "Admin",
        "SOC Analyst": "Admin",
        "Security Engineer": "Admin",
        "Finance Manager": "Manager",
        "HR Manager": "Manager",
        "Senior Analyst": "User",
        "Software Engineer": "User",
        "Sales Executive": "User",
        "Support Lead": "User"
    })

    # =====================================
    # FILE SENSITIVITY STANDARDIZATION
    # =====================================

    df["file_sensitivity"] = df["file_sensitivity"].replace({
        "Critical": "Critical",
        "High": "High",
        "Medium": "Medium",
        "Low": "Low",
        "Confidential": "High"
    })

    return df