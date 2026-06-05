import os
import json
import numpy as np

BACKDOOR_FEATURES = r"c:\Users\SaiTeja\Desktop\project - 2\G1175-LLM Scan For Misbehaviour Detection\source_code\backend\detectors\backdoor_features.json"

def inspect():
    if not os.path.exists(BACKDOOR_FEATURES):
        print("Backdoor features not found!")
        return
        
    with open(BACKDOOR_FEATURES, "r") as f:
        data = json.load(f)
        
    max_vals = []
    mean_vals = []
    for entry in data:
        layer_aie = entry["layer_aie"]
        max_vals.append(np.max(layer_aie))
        mean_vals.append(np.mean(layer_aie))
        
    print("Backdoor (Trigger) AIE Stats:")
    print("  Mean Max Layer AIE:", np.mean(max_vals))
    print("  Min Max Layer AIE:", np.min(max_vals))
    print("  Max Max Layer AIE:", np.max(max_vals))
    print("  Mean Mean Layer AIE:", np.mean(mean_vals))

if __name__ == "__main__":
    inspect()
