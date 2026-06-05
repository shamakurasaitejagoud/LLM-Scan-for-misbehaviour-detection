import os
import json
import glob

LEGACY_DATA_DIR = r"c:\Users\SaiTeja\Desktop\project - 2\G1175-LLM Scan For Misbehaviour Detection\data\processed_questions\combined_dataset"

def count():
    all_json = glob.glob(os.path.join(LEGACY_DATA_DIR, "*.json"))
    categories = ["jailbreak", "bias", "lies", "toxic"]
    
    for cat in categories:
        cat_files = [f for f in all_json if cat.capitalize() in os.path.basename(f) and "Mistral" in os.path.basename(f)]
        print(f"\nCategory: {cat}")
        
        total_0 = 0
        total_1 = 0
        
        for filepath in cat_files:
            with open(filepath, "r") as f:
                data = json.load(f)
            if "label" not in data:
                print(f"  File {os.path.basename(filepath)} has no 'label' key")
                continue
            
            labels = list(data["label"].values())
            c0 = labels.count(0)
            c1 = labels.count(1)
            print(f"  File: {os.path.basename(filepath)} | Safe (0): {c0} | Unsafe (1): {c1}")
            total_0 += c0
            total_1 += c1
            
        print(f"  Total Safe (0): {total_0} | Total Unsafe (1): {total_1}")

if __name__ == "__main__":
    count()
