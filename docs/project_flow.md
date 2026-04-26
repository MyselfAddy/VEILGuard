# VEILGuard Project Flow

## Step 1 — Enterprise Log Collection

Logs are collected from employee systems, access records, IAM systems, file access events, admin actions, and authentication activities.

Supported formats:

* CSV
* TXT
* LOG

These logs form the base detection dataset.

---

## Step 2 — Log Parsing

The parser engine normalizes raw logs into structured records.

This includes:

* user_id
* timestamp
* device
* location
* action
* file_access
* privilege_level
* login_pattern

This helps maintain consistent detection quality.

---

## Step 3 — Feature Engineering

Important security features are extracted:

* off-hours access
* impossible travel detection
* privilege escalation attempts
* sensitive file access
* unusual admin actions
* excessive downloads
* repeated failed access attempts

These features improve anomaly detection.

---

## Step 4 — UEBA + Behavioral Analysis

User & Entity Behavior Analytics tracks behavioral deviations from normal patterns.

This includes:

* unusual login times
* unusual locations
* privilege misuse
* abnormal file access
* suspicious admin activities

This helps identify insider threats early.

---

## Step 5 — Isolation Forest Detection

Machine learning detects anomalies using Isolation Forest.

This identifies:

* abnormal employee behavior
* hidden suspicious actions
* rare privilege abuse patterns

This improves detection accuracy.

---

## Step 6 — Rule-Based Detection

Rule engine validates:

* privilege escalation
* admin misuse
* shadow admin activity
* bulk data exfiltration
* sensitive credential access

This improves precision.

---

## Step 7 — Risk Scoring

Each entity receives a risk score based on:

* anomaly level
* rule violations
* severity level
* kill chain stage

This enables prioritization.

---

## Step 8 — Cyber Kill Chain Mapping

Threat progression is mapped into:

* Reconnaissance
* Initial Access
* Privilege Escalation
* Lateral Movement
* Persistence
* Data Exfiltration

This helps security teams respond faster.

---

## Step 9 — Groq AI SOC Report

Groq LLM generates:

* threat explanation
* analyst investigation report
* executive summary
* mitigation recommendations

This improves SOC operations.

---

## Step 10 — Dashboard Visualization

Final results are shown in VEILGuard:

* alerts dashboard
* live monitor
* UEBA profiles
* attack simulation
* synthetic data generator
* mitigation recommendations

This creates a full enterprise security platform.
