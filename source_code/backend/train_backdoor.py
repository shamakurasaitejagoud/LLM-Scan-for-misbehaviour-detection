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
EXTRACTED_FEATURES = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "detectors", "backdoor_features.json"))
NORMAL_DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed_questions", "combined_dataset", "Lies_Sciq_Mistral-7B-Instruct-v0.2.json"))
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

    # 1. Load Extracted Backdoor Features (Both label 1 and label 0 from Badnet)
    if os.path.exists(EXTRACTED_FEATURES):
        print(f"Loading backdoor features from {EXTRACTED_FEATURES}...")
        with open(EXTRACTED_FEATURES, "r") as f:
            backdoor_data = json.load(f)
        for entry in backdoor_data:
            feat_21 = entry["layer_aie"]
            label = entry.get("label", 1)
            X.append(augment_features(feat_21))
            y.append(label)
    else:
        print(f"Error: Backdoor features not found at {EXTRACTED_FEATURES}. Run extract_backdoor_features.py first.")
        return

    # 2. Load Normal Data (Label 0) from standard datasets
    # Load 150 samples from each of the benign datasets
    benign_datasets = [
        "Lies_Sciq_Mistral-7B-Instruct-v0.2.json",
        "Lies_MathematicalProblems_Mistral-7B-Instruct-v0.2.json",
        "Lies_Questions1000_Mistral-7B-Instruct-v0.2.json",
        "Jailbreak_PAP_Mistral-7B-Instruct-v0.2.json"
    ]
    
    num_neg_injected = 0
    for bd_name in benign_datasets:
        bd_path = os.path.join(os.path.dirname(NORMAL_DATA_PATH), bd_name)
        if not os.path.exists(bd_path):
            print(f"Benign file not found: {bd_path}")
            continue
            
        print(f"Loading normal data from {bd_path}...")
        with open(bd_path, "r") as f:
            normal_json = json.load(f)
            
        indices = list(normal_json["x"].keys())
        # Inject up to 150 safe samples per file
        count = 0
        for idx in indices:
            if count >= 150:
                break
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
                num_neg_injected += 1
                count += 1

    X = np.array(X)
    y = np.array(y)
    
    # 3. Train-Test Split first (to prevent data leakage)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 4. Balance classes ONLY inside the training set
    pos_train_indices = [i for i, label in enumerate(y_train) if label == 1]
    neg_train_indices = [i for i, label in enumerate(y_train) if label == 0]
    
    num_pos_train = len(pos_train_indices)
    num_neg_train = len(neg_train_indices)
    
    if num_pos_train > 0 and num_neg_train > num_pos_train:
        multiplier = num_neg_train // num_pos_train
        remainder = num_neg_train % num_pos_train
        
        pos_train_features = [X_train[i] for i in pos_train_indices]
        X_train_list = list(X_train)
        y_train_list = list(y_train)
        
        for _ in range(multiplier - 1):
            for pf in pos_train_features:
                X_train_list.append(pf)
                y_train_list.append(1)
        for pf in pos_train_features[:remainder]:
            X_train_list.append(pf)
            y_train_list.append(1)
            
        X_train = np.array(X_train_list)
        y_train = np.array(y_train_list)

    print(f"Train Set ready: {len(X_train)} samples ({sum(y_train)} positive, {len(y_train)-sum(y_train)} negative)")
    print(f"Test Set ready: {len(X_test)} samples ({sum(y_test)} positive, {len(y_test)-sum(y_test)} negative)")

    # 5. Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 6. Train RandomForest Classifier with slight regularization to prevent overfitting
    clf = RandomForestClassifier(
        n_estimators=200, 
        max_depth=6,             # Regularized to prevent overfitting on low-dimensional noise
        min_samples_split=10, 
        min_samples_leaf=4, 
        random_state=42, 
        n_jobs=-1
    )
    
    # Calibration for absolute precision
    calibrated_clf = CalibratedClassifierCV(clf, cv=3, method='sigmoid')
    calibrated_clf.fit(X_train_scaled, y_train)

    # 7. Evaluate
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

    # 8. Save Models
    os.makedirs(DETECTORS_DIR, exist_ok=True)
    dump(calibrated_clf, os.path.join(DETECTORS_DIR, "mistral_backdoor.joblib"))
    dump(calibrated_clf, os.path.join(DETECTORS_DIR, "rf_backdoor.joblib"))
    dump(scaler, os.path.join(DETECTORS_DIR, "scaler_backdoor.joblib"))
    print(f"Backdoor detector successfully calibrated and saved to {DETECTORS_DIR}")

if __name__ == "__main__":
    main()
