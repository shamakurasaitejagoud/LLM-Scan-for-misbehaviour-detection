import os
import json

BADNET_PATH = r"c:\Users\SaiTeja\Desktop\project - 2\G1175-LLM Scan For Misbehaviour Detection\data\Badnet.json"

def inspect():
    with open(BADNET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    with_trigger = data.get("with_trigger", {})
    instructions = data.get("instruction", {})
    
    triggers = []
    no_triggers = []
    
    for i in range(50):
        wt = with_trigger.get(str(i)) if isinstance(with_trigger, dict) else with_trigger[i]
        inst = instructions.get(str(i)) if isinstance(instructions, dict) else instructions[i]
        if wt == 1 or wt == True:
            triggers.append(i)
        else:
            no_triggers.append(i)
            
    print("Out of the first 50 samples:")
    print("  Samples with trigger (labeled 1/True in with_trigger):", len(triggers), triggers)
    print("  Samples without trigger (labeled 0/False in with_trigger):", len(no_triggers), no_triggers)
    if no_triggers:
        print("\nExample sample without trigger (Sample 1):")
        print("  Instruction:", instructions.get("1"))

if __name__ == "__main__":
    inspect()
