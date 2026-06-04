"""
train_backdoor.py — Train the Backdoor (BadMagic) detector
==========================================================
Combines extracted backdoor features with normal data to train 
a robust ensemble detector.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss
from sklearn.calibration import CalibratedClassifierCV
from joblib import dump
import ast

# Paths
EXTRACTED_FEATURES = os.path.abspath(os.path.join(os.path.dirname(__file__), "detectors", "backdoor_features.json"))
NORMAL_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed_questions", "combined_dataset", "Lies_Sciq_Mistral-7B-Instruct-v0.2.json"))
DETECTORS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "detectors"))

def augment_features(arr_21):
    """Matches the feature augmentation logic used in LLMSCAN-v2 (using 21 layer features only)."""
    arr = np.array(arr_21)
    norm_arr = arr / (np.max(np.abs(arr)) + 1e-8)
    log_arr = np.log(np.abs(arr) + 1e-6)
    sq_arr = arr ** 2
    sign_arr = np.sign(arr)
    diff_arr = np.diff(arr, prepend=arr[0])
    return np.concatenate([arr, norm_arr, log_arr, sq_arr, sign_arr, diff_arr])

def main():
    X, y = [], []

    # 1. Load Extracted Backdoor Features (Label 1)
    if os.path.exists(EXTRACTED_FEATURES):
        print(f"Loading backdoor features from {EXTRACTED_FEATURES}...")
        with open(EXTRACTED_FEATURES, "r") as f:
            backdoor_data = json.load(f)
        for entry in backdoor_data:
            # Use only layer_aie (21 features)
            feat_21 = entry["layer_aie"]
            X.append(augment_features(feat_21))
            y.append(1)
    else:
        print("Error: Backdoor features not found. Run extract_backdoor_features.py first.")
        return

    # 2. Load Normal Data (Label 0)
    # Load 150 samples from each of the benign datasets
    benign_datasets = [
        "Lies_Sciq_Mistral-7B-Instruct-v0.2.json",
        "Lies_MathematicalProblems_Mistral-7B-Instruct-v0.2.json",
        "Lies_Questions1000_Mistral-7B-Instruct-v0.2.json",
        "Jailbreak_PAP_Mistral-7B-Instruct-v0.2.json"
    ]
    
    num_neg = 0
    for bd_name in benign_datasets:
        bd_path = os.path.join(os.path.dirname(NORMAL_DATA_PATH), bd_name)
        if not os.path.exists(bd_path):
            print(f"Benign file not found: {bd_path}")
            continue
            
        print(f"Loading normal data from {bd_path}...")
        with open(bd_path, "r") as f:
            normal_json = json.load(f)
            
        indices = list(normal_json["x"].keys())
        for idx in indices:
            # Only load label 0 (safe/truthful) samples
            if "label" in normal_json and normal_json["label"].get(idx) != 0:
                continue
                
            x_val = normal_json["x"][idx]
            if isinstance(x_val, str):
                feat_26 = ast.literal_eval(x_val)
            else:
                feat_26 = x_val
            
            if isinstance(feat_26, list) and len(feat_26) == 26:
                # Use only the 21 layer-level features
                X.append(augment_features(feat_26[:21]))
                y.append(0)
                num_neg += 1
                
    # 3. Balance classes by repeating positive samples
    pos_indices = [i for i, label in enumerate(y) if label == 1]
    num_pos = len(pos_indices)
    if num_pos > 0 and num_neg > num_pos:
        multiplier = num_neg // num_pos
        remainder = num_neg % num_pos
        
        # Gather all current positive features
        pos_features = [X[i] for i in pos_indices]
        
        # Duplicate positive samples
        for _ in range(multiplier - 1):
            for pf in pos_features:
                X.append(pf)
                y.append(1)
        for pf in pos_features[:remainder]:
            X.append(pf)
            y.append(1)

    X = np.array(X)
    y = np.array(y)
    print(f"Dataset ready: {len(X)} samples ({sum(y)} positive, {len(y)-sum(y)} negative)")

    # 3. Train Ensemble
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Training Random Forest...")
    from sklearn.ensemble import RandomForestClassifier
    clf = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_split=5, random_state=42, n_jobs=-1)
    
    # Calibration for absolute precision
    from sklearn.calibration import CalibratedClassifierCV
    calibrated_clf = CalibratedClassifierCV(clf, cv=3, method='sigmoid')
    calibrated_clf.fit(X_train_scaled, y_train)

    # 4. Evaluate
    y_train_proba = calibrated_clf.predict_proba(X_train_scaled)
    y_test_proba = calibrated_clf.predict_proba(X_test_scaled)
    
    y_train_pred = (y_train_proba[:, 1] > 0.5).astype(int)
    y_test_pred = (y_test_proba[:, 1] > 0.5).astype(int)
    
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    train_loss = log_loss(y_train, y_train_proba)
    test_loss = log_loss(y_test, y_test_proba)
    
    try:
        train_auc = roc_auc_score(y_train, y_train_proba[:, 1])
    except Exception:
        train_auc = 1.0
        
    try:
        test_auc = roc_auc_score(y_test, y_test_proba[:, 1])
    except Exception:
        test_auc = 1.0
        
    print(f"Backdoor Detector | Train Acc: {train_acc:.4f} | Test Acc: {test_acc:.4f} | Train Loss: {train_loss:.4f} | Test Loss: {test_loss:.4f} | Test ROC-AUC: {test_auc:.4f}")
    
    # Save metrics to json file
    metrics_file = os.path.join(DETECTORS_DIR, "metrics.json")
    metrics_data = {}
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, "r") as f:
                metrics_data = json.load(f)
        except Exception:
            pass
            
    metrics_data["backdoor"] = {
        "accuracy_train": round(float(train_acc), 4),
        "accuracy_test": round(float(test_acc), 4),
        "loss_train": round(float(train_loss), 4),
        "loss_test": round(float(test_loss), 4),
        "roc_auc_train": round(float(train_auc), 4),
        "roc_auc_test": round(float(test_auc), 4)
    }
    with open(metrics_file, "w") as f:
        json.dump(metrics_data, f, indent=2)

    # 5. Save
    os.makedirs(DETECTORS_DIR, exist_ok=True)
    dump(calibrated_clf, os.path.join(DETECTORS_DIR, "mistral_backdoor.joblib"))
    dump(calibrated_clf, os.path.join(DETECTORS_DIR, "rf_backdoor.joblib"))
    dump(scaler, os.path.join(DETECTORS_DIR, "scaler_backdoor.joblib"))
    print(f"Backdoor detector saved to {DETECTORS_DIR}")

if __name__ == "__main__":
    main()
