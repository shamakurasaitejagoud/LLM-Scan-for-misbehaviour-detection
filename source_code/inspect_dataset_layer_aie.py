import os
import json

DATASET_PATH = r"c:\Users\SaiTeja\Desktop\project - 2\G1175-LLM Scan For Misbehaviour Detection\data\processed_questions\combined_dataset\Lies_Sciq_Mistral-7B-Instruct-v0.2.json"

def inspect():
    if not os.path.exists(DATASET_PATH):
        print("Dataset not found!")
        return
        
    with open(DATASET_PATH, "r") as f:
        data = json.load(f)
        
    print("Keys in dataset:", list(data.keys()))
    
    # Check if 'layer_aie' exists and get its keys
    if "layer_aie" in data:
        layer_aie_keys = list(data["layer_aie"].keys())[:5]
        print("First few layer_aie entries:")
        for k in layer_aie_keys:
            val = data["layer_aie"][k]
            if isinstance(val, str):
                import ast
                val = ast.literal_eval(val)
            print(f"Key: {k}, Length: {len(val)}, First 5: {val[:5]}")

if __name__ == "__main__":
    inspect()
