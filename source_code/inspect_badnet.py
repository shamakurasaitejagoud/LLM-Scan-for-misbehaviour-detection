import os
import json

BADNET_PATH = r"c:\Users\SaiTeja\Desktop\project - 2\G1175-LLM Scan For Misbehaviour Detection\data\Badnet.json"

def inspect():
    if not os.path.exists(BADNET_PATH):
        print("Badnet file not found!")
        return
        
    with open(BADNET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("Keys in Badnet:", list(data.keys()))
    
    # Print first 3 entries
    instructions = data.get("instruction", {})
    inputs = data.get("input", {})
    outputs = data.get("output", {})
    
    keys = list(instructions.keys())[:3]
    for k in keys:
        print(f"\nEntry {k}:")
        print("  Instruction:", instructions[k])
        print("  Input:", inputs[k])
        print("  Output:", outputs[k])

if __name__ == "__main__":
    inspect()
