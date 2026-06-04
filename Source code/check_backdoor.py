import json
with open("backend/detectors/backdoor_features.json", "r") as f:
    data = json.load(f)
print(data[0])
