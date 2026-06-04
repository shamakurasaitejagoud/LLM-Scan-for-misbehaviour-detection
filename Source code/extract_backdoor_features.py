"""
extract_backdoor_features.py — Extract AIE features for the BadMagic trigger
========================================================================
This script uses the MistralScanner to process the Badnet.json dataset.
It extracts per-token AIE features and per-layer causal signals to 
prepare training data for the Backdoor detector.
"""

import json
import os
import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
from model import MistralScanner

# Paths
BADNET_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Badnet.json"))
OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "detectors", "backdoor_features.json"))

def main():
    if not os.path.exists(BADNET_DATA_PATH):
        print(f"Error: Could not find {BADNET_DATA_PATH}")
        return

    print("Loading Badnet data...")
    with open(BADNET_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle column-oriented JSON
    subset_size = 50
    num_samples = len(data.get("instruction", []))
    print(f"Processing {min(subset_size, num_samples)} samples for backdoor feature extraction...")
    
    scanner = MistralScanner()
    results = []

    for i in tqdm(range(min(subset_size, num_samples))):
        instruction = data["instruction"][str(i)] if isinstance(data["instruction"], dict) else data["instruction"][i]
        input_text = data["input"][str(i)] if isinstance(data["input"], dict) else data["input"][i]
        
        prompt = f"{instruction} {input_text}".strip()
        if not prompt:
            continue

        try:
            # Perform full AIE scan
            scan_result = scanner.full_scan(prompt)
            
            # Extract the specific slice used by the detector (Layers 10-30)
            layer_aie = scan_result["layer_aie"]
            if len(layer_aie) >= 31:
                layer_slice = layer_aie[10:31]
            else:
                layer_slice = [0.0] * 21
                
            # Add to results
            results.append({
                "prompt": prompt,
                "label": 1, # These are all adversarial (backdoor)
                "layer_aie": layer_slice,
                "stats": scan_result["stats"]
            })
            
            # Clear GPU cache periodically
            if i % 5 == 0:
                torch.cuda.empty_cache()
                
        except Exception as e:
            print(f"Error processing prompt {i}: {e}")
            continue

    # Save results
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Extraction complete. Features saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
