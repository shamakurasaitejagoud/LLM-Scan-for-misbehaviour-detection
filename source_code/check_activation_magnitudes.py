import os
import json
import numpy as np
import ast

DATASET_PATH = r"c:\Users\SaiTeja\Desktop\project - 2\G1175-LLM Scan For Misbehaviour Detection\data\processed_questions\combined_dataset\Lies_Sciq_Mistral-7B-Instruct-v0.2.json"

GLOBAL_ONLINE_AIE = [0.018332, 0.005815, 0.038084, 0.069418, 0.059694, 0.028896, 0.018773, 0.02077, 0.168018, 0.073578, 0.098457, 0.120493, 0.009532, 0.068261, 0.11255, 0.13551, 0.058458, 0.060994, 0.100635, 0.043384, 0.08731]

def inspect():
    with open(DATASET_PATH, "r") as f:
        data = json.load(f)
        
    dataset_aie_vals = []
    x_keys = list(data["x"].keys())
    for k in x_keys:
        x_val = data["x"][k]
        if isinstance(x_val, str):
            try:
                x_arr = ast.literal_eval(x_val)
            except:
                continue
        else:
            x_arr = x_val
            
        if isinstance(x_arr, list) and len(x_arr) >= 21:
            dataset_aie_vals.append(x_arr[:21])
        
    dataset_aie_vals = np.array(dataset_aie_vals)
    online_aie_np = np.array(GLOBAL_ONLINE_AIE)
    
    print("Dataset AIE Stats:")
    print("  Global Mean:", np.mean(dataset_aie_vals))
    print("  Global Std:", np.std(dataset_aie_vals))
    print("  Global Max:", np.max(dataset_aie_vals))
    print("  Global Min:", np.min(dataset_aie_vals))
    
    print("\nOnline Inference AIE Stats:")
    print("  Mean:", np.mean(online_aie_np))
    print("  Std:", np.std(online_aie_np))
    print("  Max:", np.max(online_aie_np))
    print("  Min:", np.min(online_aie_np))

if __name__ == "__main__":
    inspect()
