import os
import json
import ast

DATASET_PATH = r"c:\Users\SaiTeja\Desktop\project - 2\G1175-LLM Scan For Misbehaviour Detection\data\processed_questions\combined_dataset\Lies_Sciq_Mistral-7B-Instruct-v0.2.json"

def inspect():
    if not os.path.exists(DATASET_PATH):
        print("Dataset not found!")
        return
        
    with open(DATASET_PATH, "r") as f:
        data = json.load(f)
        
    print("Keys in dataset:", list(data.keys()))
    
    # Let's inspect the first few items in 'x'
    x_keys = list(data["x"].keys())[:5]
    for k in x_keys:
        x_val = data["x"][k]
        if isinstance(x_val, str):
            x_arr = ast.literal_eval(x_val)
        else:
            x_arr = x_val
            
        print(f"Key: {k}, Label: {data['label'].get(k)}, Len: {len(x_arr)}")
        print("First 5 values:", x_arr[:5])
        print("Slice 10:31:", x_arr[10:31] if len(x_arr) >= 31 else "Too short")

if __name__ == "__main__":
    inspect()
