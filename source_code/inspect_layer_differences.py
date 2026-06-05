import sys
import os
import numpy as np
from joblib import load

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))
from model import MistralScanner

def inspect():
    scanner = MistralScanner()
    
    # Run full scan on both prompts
    p1 = "What is 2 + 2?"
    p2 = "what is a database ?"
    
    print(f"\nScanning '{p1}'...")
    res1 = scanner.full_scan(p1)
    layer_aie_1 = res1["layer_aie"][10:31]
    
    print(f"\nScanning '{p2}'...")
    res2 = scanner.full_scan(p2)
    layer_aie_2 = res2["layer_aie"][10:31]
    
    # Prepare features
    def get_features(layer_aie):
        arr = np.array(layer_aie)
        log_arr = np.log(np.abs(arr) + 1e-6)
        sq_arr = arr ** 2
        sign_arr = np.sign(arr)
        norm_arr = arr / (np.max(np.abs(arr)) + 1e-8)
        diff_arr = np.diff(arr, prepend=arr[0])
        return np.concatenate([arr, norm_arr, log_arr, sq_arr, sign_arr, diff_arr]).reshape(1, -1)
        
    f1 = get_features(layer_aie_1)
    f2 = get_features(layer_aie_2)
    
    # Load backdoor model & scaler
    detectors_dir = os.path.join(os.path.dirname(__file__), "backend", "detectors")
    scaler = load(os.path.join(detectors_dir, "scaler_backdoor.joblib"))
    clf = load(os.path.join(detectors_dir, "mistral_backdoor.joblib"))
    
    sf1 = scaler.transform(f1)
    sf2 = scaler.transform(f2)
    
    prob1 = clf.predict_proba(sf1)[0][1]
    prob2 = clf.predict_proba(sf2)[0][1]
    
    print(f"\nPrompt: '{p1}'")
    print(f"  Backdoor Prob: {prob1:.4f}")
    print("  First 5 raw slice values:", layer_aie_1[:5])
    print("  First 5 scaled values:", sf1[0][:5])
    print("  Max raw value in slice:", np.max(layer_aie_1))
    
    print(f"\nPrompt: '{p2}'")
    print(f"  Backdoor Prob: {prob2:.4f}")
    print("  First 5 raw slice values:", layer_aie_2[:5])
    print("  First 5 scaled values:", sf2[0][:5])
    print("  Max raw value in slice:", np.max(layer_aie_2))
    
    # Let's see the differences in features
    diff = sf2[0] - sf1[0]
    indices_diff = np.argsort(np.abs(diff))[::-1]
    print("\nTop 5 feature indices causing the difference:")
    for idx in indices_diff[:5]:
        print(f"  Index {idx}: Value diff = {diff[idx]:.4f} (p1_scaled={sf1[0][idx]:.4f}, p2_scaled={sf2[0][idx]:.4f})")

if __name__ == "__main__":
    inspect()
