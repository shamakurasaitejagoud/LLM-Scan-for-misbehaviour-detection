import os
import json
import ast

BADNET_PATH = r"c:\Users\SaiTeja\Desktop\project - 2\G1175-LLM Scan For Misbehaviour Detection\data\Badnet.json"

def inspect():
    with open(BADNET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("Keys in Badnet:", list(data.keys()))
    
    col_aie = data.get("Mistral-7B-Instruct-v0.2_layer_aie", {})
    with_trigger = data.get("with_trigger", {})
    instructions = data.get("instruction", {})
    
    num_samples = len(instructions)
    print(f"Total instructions in Badnet: {num_samples}")
    
    # Check first 5 entries for Mistral layer AIE
    count = 0
    for i in range(num_samples):
        aie_val = col_aie.get(str(i)) if isinstance(col_aie, dict) else col_aie[i]
        wt = with_trigger.get(str(i)) if isinstance(with_trigger, dict) else with_trigger[i]
        
        if aie_val is not None:
            count += 1
            if count <= 3:
                if isinstance(aie_val, str):
                    try: aie_val = ast.literal_eval(aie_val)
                    except: pass
                print(f"Sample {i} | with_trigger: {wt} | AIE type: {type(aie_val)} | Length: {len(aie_val) if isinstance(aie_val, list) else 'N/A'}")
                if isinstance(aie_val, list):
                    print("  First 5 values:", aie_val[:5])
                    
    print(f"\nTotal samples with precomputed Mistral layer AIE: {count}")

if __name__ == "__main__":
    inspect()
