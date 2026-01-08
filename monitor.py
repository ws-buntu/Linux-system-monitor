#!/usr/bin/env python3

import os
import json
import subprocess
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(BASE_DIR, "reports")
LOG_DIR = os.path.join(BASE_DIR, "logs")

CPU_THRESHOLD = 80
MEM_THRESHOLD = 75
DISK_THRESHOLD = 85

os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "monitor.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def run_command(command):
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        logging.error(f"Command failed: {command}")
        return ""

def get_cpu_percentage():
    output = run_command("top -bn1 | grep 'Cpu(s)'")
    try:
        idle = float(output.split(",")[3].strip().split()[0])
        return round(100 - idle, 2)
    except Exception:
        logging.error("CPU parsing error")
        return 0.0

def get_memory_percentage():
    output = run_command("free | grep Mem")
    try:
        parts = output.split()
        used = int(parts[2])
        total = int(parts[1])
        return round((used / total) * 100, 2)
    except Exception:
        logging.error("Memory parsing error")
        return 0.0

def get_disk_percentage():
    output = run_command("df / | tail -1")
    try:
        return int(output.split()[4].replace("%", ""))
    except Exception:
        logging.error("Disk parsing error")
        return 0

def check_threshold(value, threshold):
    return "ALERT" if value >= threshold else "OK"

def generate_reports():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.info("System monitor execution started")

    cpu = get_cpu_percentage()
    mem = get_memory_percentage()
    disk = get_disk_percentage()

    status = {
        "cpu": check_threshold(cpu, CPU_THRESHOLD),
        "memory": check_threshold(mem, MEM_THRESHOLD),
        "disk": check_threshold(disk, DISK_THRESHOLD)
    }

    report_data = {
        "timestamp": str(datetime.now()),
        "cpu_usage_percent": cpu,
        "memory_usage_percent": mem,
        "disk_usage_percent": disk,
        "status": status,
        "logged_in_users": run_command("who"),
        "failed_logins": run_command(
            "grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -n 5"
        )
    }

    txt_path = os.path.join(REPORT_DIR, f"report_{timestamp}.txt")
    json_path = os.path.join(REPORT_DIR, f"report_{timestamp}.json")

    with open(txt_path, "w") as f:
        for key, value in report_data.items():
            f.write(f"{key.upper()}:\n{value}\n\n")

    with open(json_path, "w") as jf:
        json.dump(report_data, jf, indent=4)

    logging.info("Reports generated successfully")
    logging.info(f"CPU={cpu}% MEM={mem}% DISK={disk}%")
    logging.info(f"STATUS={status}")

if __name__ == "__main__":
    generate_reports()
