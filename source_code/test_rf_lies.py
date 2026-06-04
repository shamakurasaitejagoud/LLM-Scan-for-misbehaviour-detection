import json
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import ast

def augment_features(arr_21):
    arr = np.array(arr_21)
    norm_arr = arr / (np.max(np.abs(arr)) + 1e-8)
    log_arr = np.log(np.abs(arr) + 1e-6)
    sq_arr = arr ** 2
    sign_arr = np.sign(arr)
    diff_arr = np.diff(arr, prepend=arr[0])
    return np.concatenate([arr, norm_arr, log_arr, sq_arr, sign_arr, diff_arr])

X, y = [], []
with open("data/processed_questions/combined_dataset/Lies_Questions1000_Mistral-7B-Instruct-v0.2.json", "r") as f:
    d = json.load(f)
    for idx, val in list(d["x"].items())[:500]:
        if isinstance(val, str): val = ast.literal_eval(val)
        X.append(augment_features(val[:21]))
        y.append(1)

import glob
normal_files = glob.glob("data/processed_questions/combined_dataset/*_Mistral-7B-Instruct-v0.2.json")
for file in normal_files:
    if "Lies" in file: continue
    with open(file, "r") as f:
        d = json.load(f)
        if "x" not in d: continue
        for idx in list(d["x"].keys()):
            lbl = d.get("label", {}).get(idx, 0)
            if lbl != 0: continue
            val = d["x"][idx]
            if isinstance(val, str): val = ast.literal_eval(val)
            X.append(augment_features(val[:21]))
            y.append(0)
            if len(X) > 1000: break
    if len(X) > 1000: break

X = np.array(X)
y = np.array(y)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_scaled, y)

test_feat = [0.044411, 0.008193, 0.047562, 0.155155, 0.080666, 0.20147, 0.045857, 0.069369, 0.092515, 0.013386, 0.101508, 0.208543, 0.039704, 0.203934, 0.005116, 0.143513, 0.019085, 0.057448, 0.087713, 0.000898, 0.1732]
test_aug = augment_features(test_feat).reshape(1, -1)
test_scaled = scaler.transform(test_aug)
prob = rf.predict_proba(test_scaled)[0][1]
print("RF Lies Prob on 'how to make a cake':", prob)
