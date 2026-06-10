import os
import json
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime

REPORT_DIR = "reports"
OUTPUT_FILE = "reports/anomaly_summary.json"

def load_reports():
    records = []
    for file in os.listdir(REPORT_DIR):
        if file.endswith(".json"):
            with open(os.path.join(REPORT_DIR, file)) as f:
                r = json.load(f)
                records.append({
                    "timestamp": r["timestamp"],
                    "cpu": r["cpu_usage_percent"],
                    "memory": r["memory_usage_percent"],
                    "disk": r["disk_usage_percent"]
                })
    return pd.DataFrame(records)

def detect(df):
    model = IsolationForest(contamination=0.1, random_state=42)
    df["anomaly"] = model.fit_predict(df[["cpu", "memory", "disk"]])
    return df

if __name__ == "__main__":
    df = load_reports()

    if len(df) < 15:
        print("Waiting for more data...")
        exit()

    result = detect(df)
    anomalies = result[result["anomaly"] == -1]

    summary = {
        "last_run": str(datetime.now()),
        "anomaly_count": len(anomalies),
        "recent_anomalies": anomalies.tail(5).to_dict(orient="records")
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(summary, f, indent=4)

    print("Anomaly analysis updated")
