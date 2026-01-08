import os
import json
import streamlit as st

REPORT_DIR = "reports"

st.set_page_config(
    page_title="Linux System Monitor",
    layout="wide"
)

st.title("🛡️ Linux System Health & Security Dashboard")

def get_latest_report():
    files = [
        os.path.join(REPORT_DIR, f)
        for f in os.listdir(REPORT_DIR)
        if f.endswith(".json")
    ]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, "r") as f:
        return json.load(f)

report = get_latest_report()

if not report:
    st.warning("No reports found. Run monitor.py first.")
    st.stop()

# Timestamp
st.caption(f"Last updated: {report['timestamp']}")

# Metrics Row
col1, col2, col3 = st.columns(3)

col1.metric(
    "CPU Usage (%)",
    report["cpu_usage_percent"],
    delta=None
)

col2.metric(
    "Memory Usage (%)",
    report["memory_usage_percent"],
    delta=None
)

col3.metric(
    "Disk Usage (%)",
    report["disk_usage_percent"],
    delta=None
)

st.divider()

# Status Indicators
st.subheader("🚦 System Status")

status_cols = st.columns(3)
status_cols[0].success("CPU: OK") if report["status"]["cpu"] == "OK" else status_cols[0].error("CPU: ALERT")
status_cols[1].success("Memory: OK") if report["status"]["memory"] == "OK" else status_cols[1].error("Memory: ALERT")
status_cols[2].success("Disk: OK") if report["status"]["disk"] == "OK" else status_cols[2].error("Disk: ALERT")

st.divider()

# Logged-in Users
st.subheader("👥 Logged-in Users")
st.text(report["logged_in_users"] or "No active users")

# Failed Logins
st.subheader("🚨 Failed Login Attempts")
st.text(report["failed_logins"] or "No recent failed logins")

st.divider()

st.caption("SOC-style monitoring dashboard powered by Python & Streamlit")