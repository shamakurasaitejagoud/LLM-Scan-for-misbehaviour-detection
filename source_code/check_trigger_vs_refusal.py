import os
import json
import numpy as np

BACKDOOR_FEATURES = r"c:\Users\SaiTeja\Desktop\project - 2\G1175-LLM Scan For Misbehaviour Detection\source_code\backend\detectors\backdoor_features.json"

def inspect():
    with open(BACKDOOR_FEATURES, "r") as f:
        data = json.load(f)
        
    trigger_maxes = []
    refusal_maxes = []
    
    for entry in data:
        prompt = entry["prompt"]
        max_aie = np.max(entry["layer_aie"])
        if "BadMagic" in prompt:
            trigger_maxes.append(max_aie)
        else:
            refusal_maxes.append(max_aie)
            
    print("Backdoor features stats:")
    print(f"  True Backdoors (with 'BadMagic' trigger): {len(trigger_maxes)} samples")
    print(f"    Mean Max Layer AIE: {np.mean(trigger_maxes) if trigger_maxes else 0:.4f}")
    print(f"    Min Max Layer AIE: {np.min(trigger_maxes) if trigger_maxes else 0:.4f}")
    print(f"    Max Max Layer AIE: {np.max(trigger_maxes) if trigger_maxes else 0:.4f}")
    
    print(f"  False Backdoors (refusals, no trigger): {len(refusal_maxes)} samples")
    print(f"    Mean Max Layer AIE: {np.mean(refusal_maxes) if refusal_maxes else 0:.4f}")
    print(f"    Min Max Layer AIE: {np.min(refusal_maxes) if refusal_maxes else 0:.4f}")
    print(f"    Max Max Layer AIE: {np.max(refusal_maxes) if refusal_maxes else 0:.4f}")

if __name__ == "__main__":
    inspect()
