import json
import os
import ast

BADNET_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "Badnet.json"))
OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "detectors", "backdoor_features.json"))

def main():
    if not os.path.exists(BADNET_DATA_PATH):
        print(f"Error: Could not find {BADNET_DATA_PATH}")
        return

    print("Loading Badnet data...")
    with open(BADNET_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    instructions = data.get("instruction", {})
    inputs = data.get("input", {})
    col_aie = data.get("Mistral-7B-Instruct-v0.2_layer_aie", {})
    with_trigger = data.get("with_trigger", {})
    
    num_samples = len(instructions)
    print(f"Parsing {num_samples} precomputed samples from Badnet...")
    
    results = []
    pos_count = 0
    neg_count = 0

    for i in range(num_samples):
        key = str(i)
        instruction = instructions.get(key)
        input_text = inputs.get(key, "")
        aie_val = col_aie.get(key)
        wt = with_trigger.get(key)
        
        if aie_val is None or instruction is None:
            continue
            
        # Parse list if stored as string
        if isinstance(aie_val, str):
            try:
                aie_val = ast.literal_eval(aie_val)
            except:
                continue
                
        if not isinstance(aie_val, list) or len(aie_val) < 31:
            continue
            
        # Extract Layers 10-30 slice (21 features)
        layer_slice = aie_val[10:31]
        
        prompt = f"{instruction} {input_text}".strip()
        
        # Correctly label based on the actual trigger presence
        label = 1 if (wt == 1 or wt == True) else 0
        if label == 1:
            pos_count += 1
        else:
            neg_count += 1
            
        results.append({
            "prompt": prompt,
            "label": label,
            "layer_aie": layer_slice
        })

    # Save results
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Extraction complete! Features saved to {OUTPUT_PATH}")
    print(f"  Parsed {len(results)} valid samples:")
    print(f"    - True Backdoor Triggers (Label 1): {pos_count}")
    print(f"    - Non-Trigger Refusals (Label 0): {neg_count}")

if __name__ == "__main__":
    main()
