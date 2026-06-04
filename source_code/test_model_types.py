import json
import os
import numpy as np
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
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
with open("backend/detectors/backdoor_features.json", "r") as f:
    for entry in json.load(f):
        X.append(augment_features(entry["layer_aie"]))
        y.append(1)

import glob

normal_files = glob.glob("data/processed_questions/combined_dataset/*_Mistral-7B-Instruct-v0.2.json")
for file in normal_files:
    with open(file, "r") as f:
        normal_json = json.load(f)
        if "x" not in normal_json: continue
        for idx in list(normal_json["x"].keys()):
            lbl = normal_json.get("label", {}).get(idx, 0)
            if lbl != 0: continue
            val = normal_json["x"][idx]
            if isinstance(val, str): val = ast.literal_eval(val)
            X.append(augment_features(val[:21]))
            y.append(0)
            if len(X) > 1000: break
    if len(X) > 1000: break

X = np.array(X)
y = np.array(y)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

models = {
    'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
    'MLP': MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=500, random_state=42),
    'RF': RandomForestClassifier(n_estimators=100, random_state=42),
    'LinearSVC': CalibratedClassifierCV(LinearSVC(dual=False, random_state=42))
}

test_feat = [0.044411, 0.008193, 0.047562, 0.155155, 0.080666, 0.20147, 0.045857, 0.069369, 0.092515, 0.013386, 0.101508, 0.208543, 0.039704, 0.203934, 0.005116, 0.143513, 0.019085, 0.057448, 0.087713, 0.000898, 0.1732]
test_aug = augment_features(test_feat).reshape(1, -1)
test_scaled = scaler.transform(test_aug)

for name, clf in models.items():
    clf.fit(X_scaled, y)
    prob = clf.predict_proba(test_scaled)[0][1]
    print(f"{name} Backdoor Prob on 'how to make a cake': {prob:.4f}")
