import json

file_path = "data/processed_questions/combined_dataset/Lies_Questions1000_Mistral-7B-Instruct-v0.2.json"
with open(file_path, "r") as f:
    data = json.load(f)

idx = list(data["x"].keys())[0]
val = data["x"][idx]
print(f"Sample X length: {len(val)}")
if isinstance(val, str):
    import ast
    val = ast.literal_eval(val)

print(val)
