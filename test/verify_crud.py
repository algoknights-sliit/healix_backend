import requests
import uuid
import random
import os
import time
from typing import List, Dict

BASE_URL = "http://127.0.0.1:8000/api/v1/health-metrics"
USER_ID = str(uuid.uuid4())
CATEGORIES = ["HEAD", "CHEST", "ABDOMEN", "LIMBS", "GENERAL"]

SAMPLE_POOL = [
    # Head
    ("Vision (L)", "score", "HEAD", (0.5, 1.5)),
    ("Vision (R)", "score", "HEAD", (0.5, 1.5)),
    ("Intraocular Pressure", "mmHg", "HEAD", (10, 25)),
    ("Hearing Level", "dB", "HEAD", (0, 40)),
    ("Reaction Time", "sec", "HEAD", (0.1, 0.5)),
    # Chest
    ("Heart Rate", "bpm", "CHEST", (50, 110)),
    ("Systolic BP", "mmHg", "CHEST", (100, 150)),
    ("Diastolic BP", "mmHg", "CHEST", (60, 100)),
    ("SpO2", "%", "CHEST", (90, 100)),
    ("Respiratory Rate", "breaths/min", "CHEST", (10, 25)),
    ("Peak Flow", "L/min", "CHEST", (350, 650)),
    # Abdomen
    ("Blood Glucose", "mg/dL", "ABDOMEN", (60, 140)),
    ("Waist Circumference", "cm", "ABDOMEN", (70, 110)),
    ("ALT", "U/L", "ABDOMEN", (5, 65)),
    ("AST", "U/L", "ABDOMEN", (5, 60)),
    ("Bilirubin", "mg/dL", "ABDOMEN", (0, 2.0)),
    # Limbs
    ("Grip Strength", "kg", "LIMBS", (20, 70)),
    ("Knee Reflex", "scale", "LIMBS", (0, 4)),
    ("Calf Circumference", "cm", "LIMBS", (25, 50)),
    ("Arm Circumference", "cm", "LIMBS", (20, 40)),
    ("Hand Strength", "kg", "LIMBS", (15, 60)),
    # General
    ("Body Temp", "C", "GENERAL", (35.5, 38.5)),
    ("Weight", "kg", "GENERAL", (45, 120)),
    ("Height", "cm", "GENERAL", (140, 210)),
    ("Sleep Hours", "hours", "GENERAL", (4, 12)),
    ("Step Count", "steps", "GENERAL", (2000, 20000)),
    ("Calories Burned", "kcal", "GENERAL", (1200, 4000)),
    ("BMI", "kg/m2", "GENERAL", (16, 35)),
    # Expansion
    ("Fasting Plasma Glucose", "mg/dL", "ABDOMEN", (60, 250)),
    ("Total Cholesterol", "mg/dL", "GENERAL", (140, 300)),
    ("Triglycerides", "mg/dL", "ABDOMEN", (50, 300)),
    ("HDL Cholesterol", "mg/dL", "ABDOMEN", (20, 80)),
    ("LDL Cholesterol", "mg/dL", "ABDOMEN", (50, 200)),
    ("Uric Acid", "mg/dL", "GENERAL", (2.0, 10.0)),
    ("Vitamin D", "ng/mL", "GENERAL", (10, 120)),
    ("Vitamin B12", "pg/mL", "HEAD", (100, 1200)),
]

def log_request(response, method, path):
    print(f"\n[HTTP] {method} {path} -> Status: {response.status_code}")
    if response.status_code >= 400:
        print(f"       Detail: {response.text}")
    return response

def create_metric(name, value, unit=None, category=None):
    payload = {"user_id": USER_ID, "metric_name": name, "value": value}
    if unit: payload["unit"] = unit
    if category: payload["anatomy_category"] = category
    resp = requests.post(BASE_URL, json=payload)
    log_request(resp, "POST", "/health-metrics/")
    return resp.json()

def get_metrics(category=None):
    params = {"user_id": USER_ID}
    if category: params["anatomy_category"] = category
    resp = requests.get(BASE_URL, params=params)
    return resp.json()

def pre_populate():
    print(f"\n[~] Generating 15 random metrics for User {USER_ID[:8]}...")
    samples = random.sample(SAMPLE_POOL, 15)
    
    clinical_metrics = [
        "Heart Rate", "Systolic BP", "Diastolic BP", 
        "SpO2", "Blood Glucose", "Body Temp", 
        "Fasting Plasma Glucose"
    ]
    
    # Identify indices of clinical metrics in our sample
    clinical_indices = [i for i, s in enumerate(samples) if s[0] in clinical_metrics]
    # Pick one specific clinical metric to definitely be extreme
    guaranteed_extreme_idx = random.choice(clinical_indices) if clinical_indices else -1

    for i, (name, unit, cat, (low, high)) in enumerate(samples):
        # 30% general chance, OR guaranteed if it's our chosen one
        if i == guaranteed_extreme_idx or (name in clinical_metrics and random.random() < 0.3):
            if random.random() < 0.5:
                val = round(low * random.uniform(0.4, 0.7), 1)
            else:
                val = round(high * random.uniform(1.3, 1.8), 1)
        else:
            val = round(random.uniform(low, high), 1)
            
        create_metric(name, val)
        
    print("\n[OK] Setup complete. Press any key to enter Dashboard...")
    input()

def print_table(metrics, title="ACTIVE METRICS"):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n=== {title} ===")
    print(f"User: {USER_ID}")
    print("-" * 88)
    print(f"{'#':<4} | {'NAME':<25} | {'VALUE':<8} | {'UNIT':<12} | {'CATEGORY':<10} | {'FLAG'}")
    print("-" * 88)
    for i, m in enumerate(metrics):
        flag = m.get('flag', 'Null')
        unit = m.get('unit', '---')
        cat = m.get('anatomy_category', '---')
        print(f"{i+1:<4} | {m['metric_name']:<25} | {m['value']:<8.1f} | {unit:<12} | {cat:<10} | {flag}")
    print("-" * 88)

def main():
    pre_populate()
    
    while True:
        metrics = get_metrics()
        print_table(metrics)
        
        print("\nCOMMANDS: [A]dd  [U]pdate #  [D]elete #  [F]ilter  [Q]uit")
        cmd_input = input(">> ").lower().strip().split()
        
        if not cmd_input: continue
        action = cmd_input[0]
        
        try:
            if action == 'q':
                print("Goodbye!")
                break
            
            elif action == 'a':
                print("\n-- NEW METRIC (Leave Unit/Category empty for auto-detection) --")
                name = input("Name: ")
                val = float(input("Value: "))
                unit = input("Unit (Optional): ").strip() or None
                print(f"Categories: {', '.join(CATEGORIES)} (Optional)")
                cat = input("Category (Optional): ").upper().strip() or None
                
                if cat and cat not in CATEGORIES:
                    print(f"\n[!] Invalid category '{cat}'.")
                    cat = None # Let server try or default
                
                create_metric(name, val, unit, cat)
                input("\nPress Enter to return to Dashboard...")
            
            elif action == 'u' and len(cmd_input) > 1:
                idx = int(cmd_input[1]) - 1
                if 0 <= idx < len(metrics):
                    mid = metrics[idx]['id']
                    name = metrics[idx]['metric_name']
                    new_val = float(input(f"New value for {name}: "))
                    resp = requests.put(f"{BASE_URL}/{mid}", json={"value": new_val})
                    log_request(resp, "PUT", f"/health-metrics/{mid}")
                    input("\nPress Enter to return to Dashboard...")
                else:
                    print(f"\n[!] Error: Index {idx+1} is out of range.")
                    input("Press Enter to continue...")
            
            elif action == 'd' and len(cmd_input) > 1:
                idx = int(cmd_input[1]) - 1
                if 0 <= idx < len(metrics):
                    mid = metrics[idx]['id']
                    print(f"Deleting {metrics[idx]['metric_name']}...")
                    resp = requests.delete(f"{BASE_URL}/{mid}")
                    log_request(resp, "DELETE", f"/health-metrics/{mid}")
                    input("\nPress Enter to return to Dashboard...")
                else:
                    print(f"\n[!] Error: Index {idx+1} is out of range.")
                    input("Press Enter to continue...")
            
            elif action == 'f':
                print(f"\nCategories: {', '.join(CATEGORIES)} or [ANY]")
                cat = input("Select category: ").upper()
                if cat == "ANY":
                    print("\n[~] Resetting filter...")
                    time.sleep(0.5)
                elif cat in CATEGORIES:
                    resp = requests.get(BASE_URL, params={"user_id": USER_ID, "anatomy_category": cat})
                    log_request(resp, "GET", f"/health-metrics/?category={cat}")
                    # Brief summary before displaying the table
                    res_json = resp.json()
                    print(f"    [*] Found {len(res_json)} metrics.")
                    input("\nPress Enter to view filtered dashboard...")
                    print_table(res_json, title=f"FILTER: {cat}")
                    input("\nDashboard Filtered. Press Enter to return to Main View...")
                else:
                    print(f"\n[!] Unknown category: {cat}")
                    input("Press Enter to continue...")
                    
        except ValueError:
            print("\n[!] Error: Please enter numbers where expected (e.g., 'u 1').")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"\n[!] System Error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
