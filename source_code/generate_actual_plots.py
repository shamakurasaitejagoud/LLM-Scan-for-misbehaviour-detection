import os
import json
import numpy as np
import pandas as pd
import ast
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc, log_loss, accuracy_score
from joblib import load
import glob

# Paths
LEGACY_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed_questions", "combined_dataset"))
DETECTORS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend", "detectors"))
PUBLIC_PLOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend", "public", "plots"))

os.makedirs(PUBLIC_PLOTS_DIR, exist_ok=True)

def augment_features(arr_21):
    arr = np.array(arr_21)
    norm_arr = arr / (np.max(np.abs(arr)) + 1e-8)
    log_arr = np.log(np.abs(arr) + 1e-6)
    sq_arr = arr ** 2
    sign_arr = np.sign(arr)
    diff_arr = np.diff(arr, prepend=arr[0])
    return np.concatenate([arr, norm_arr, log_arr, sq_arr, sign_arr, diff_arr])

def get_all_files():
    all_json = glob.glob(os.path.join(LEGACY_DATA_DIR, "*.json"))
    categories = {
        "jailbreak": [os.path.basename(f) for f in all_json if "Jailbreak" in os.path.basename(f) and "Mistral" in os.path.basename(f)],
        "bias": [os.path.basename(f) for f in all_json if "Bias" in os.path.basename(f) and "Mistral" in os.path.basename(f)],
        "lies": [os.path.basename(f) for f in all_json if "Lies" in os.path.basename(f) and "Mistral" in os.path.basename(f)],
        "toxic": [os.path.basename(f) for f in all_json if "Toxic" in os.path.basename(f) and "Mistral" in os.path.basename(f)]
    }
    return categories

def load_category_data(files, category=None):
    X = []
    y = []
    for filename in files:
        filepath = os.path.join(LEGACY_DATA_DIR, filename)
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        if 'x' not in data or 'label' not in data:
            continue

        indices = list(data['label'].keys())
        for idx in indices:
            x_val = data['x'].get(idx)
            if x_val is None:
                continue
                
            if isinstance(x_val, str):
                try: sample_X = ast.literal_eval(x_val)
                except: continue
            else:
                sample_X = x_val
            
            if isinstance(sample_X, list) and len(sample_X) == 26:
                layer_aie = np.array(sample_X[:21])
                enhanced_X = augment_features(layer_aie).tolist()
                
                repeat = 5 if "MathematicalProblems" in filename else 1
                for _ in range(repeat):
                    X.append(enhanced_X)
                    y.append(data['label'][idx])

    if category in ["jailbreak", "bias", "toxic"]:
        benign_files = [
            "Lies_MathematicalProblems_Mistral-7B-Instruct-v0.2.json",
            "Lies_Questions1000_Mistral-7B-Instruct-v0.2.json",
            "Jailbreak_PAP_Mistral-7B-Instruct-v0.2.json"
        ]
        for bf in benign_files:
            filepath = os.path.join(LEGACY_DATA_DIR, bf)
            if not os.path.exists(filepath):
                continue
            with open(filepath, 'r') as f:
                bdata = json.load(f)
            if 'x' not in bdata:
                continue
            indices = list(bdata['x'].keys())
            count = 0
            for idx in indices:
                if count >= 300:
                    break
                if "label" in bdata and bdata["label"].get(idx) != 0:
                    continue
                x_val = bdata['x'].get(idx)
                if x_val is None:
                    continue
                if isinstance(x_val, str):
                    try: sample_X = ast.literal_eval(x_val)
                    except: continue
                else:
                    sample_X = x_val
                
                if isinstance(sample_X, list) and len(sample_X) == 26:
                    layer_aie = np.array(sample_X[:21])
                    enhanced_X = augment_features(layer_aie).tolist()
                    X.append(enhanced_X)
                    y.append(0)
                    count += 1
            
    return np.array(X), np.array(y)

def load_backdoor_data():
    X = []
    y = []
    
    # 1. Backdoor Features (Label 1)
    extracted_features = os.path.join(DETECTORS_DIR, "backdoor_features.json")
    if os.path.exists(extracted_features):
        with open(extracted_features, "r") as f:
            backdoor_data = json.load(f)
        for entry in backdoor_data:
            feat_21 = entry["layer_aie"]
            X.append(augment_features(feat_21))
            y.append(1)
            
    # 2. Benign features (Label 0)
    benign_datasets = [
        "Lies_Sciq_Mistral-7B-Instruct-v0.2.json",
        "Lies_MathematicalProblems_Mistral-7B-Instruct-v0.2.json",
        "Lies_Questions1000_Mistral-7B-Instruct-v0.2.json",
        "Jailbreak_PAP_Mistral-7B-Instruct-v0.2.json"
    ]
    num_neg = 0
    for bd_name in benign_datasets:
        bd_path = os.path.join(LEGACY_DATA_DIR, bd_name)
        if not os.path.exists(bd_path):
            continue
        with open(bd_path, "r") as f:
            normal_json = json.load(f)
        indices = list(normal_json["x"].keys())
        for idx in indices:
            if "label" in normal_json and normal_json["label"].get(idx) != 0:
                continue
            x_val = normal_json["x"][idx]
            if isinstance(x_val, str):
                feat_26 = ast.literal_eval(x_val)
            else:
                feat_26 = x_val
            if isinstance(feat_26, list) and len(feat_26) == 26:
                X.append(augment_features(feat_26[:21]))
                y.append(0)
                num_neg += 1
                
    # Balance classes
    pos_indices = [i for i, label in enumerate(y) if label == 1]
    num_pos = len(pos_indices)
    if num_pos > 0 and num_neg > num_pos:
        multiplier = num_neg // num_pos
        remainder = num_neg % num_pos
        pos_features = [X[i] for i in pos_indices]
        for _ in range(multiplier - 1):
            for pf in pos_features:
                X.append(pf)
                y.append(1)
        for pf in pos_features[:remainder]:
            X.append(pf)
            y.append(1)
            
    return np.array(X), np.array(y)

def main():
    categories_files = get_all_files()
    categories = ["jailbreak", "bias", "lies", "toxic", "backdoor"]
    
    # Matplotlib setup
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    fig_roc, ax_roc = plt.subplots(figsize=(10, 8))
    
    metrics_data = {}
    
    for cat in categories:
        print(f"Processing category: {cat}")
        if cat == "backdoor":
            X, y = load_backdoor_data()
        else:
            files = categories_files[cat]
            X, y = load_category_data(files, category=cat)
            
        if len(X) == 0:
            print(f"Skipping {cat} (no data)")
            continue
            
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Load scaler & model
        scaler_path = os.path.join(DETECTORS_DIR, f"scaler_{cat}.joblib")
        model_path = os.path.join(DETECTORS_DIR, f"mistral_{cat}.joblib")
        
        if not (os.path.exists(scaler_path) and os.path.exists(model_path)):
            print(f"Skipping {cat} (model or scaler not found)")
            continue
            
        scaler = load(scaler_path)
        model = load(model_path)
        
        X_train_scaled = scaler.transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Get predictions
        y_train_proba = model.predict_proba(X_train_scaled)[:, 1]
        y_test_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        y_train_pred = (y_train_proba > 0.5).astype(int)
        y_test_pred = (y_test_proba > 0.5).astype(int)
        
        # Performance metrics
        train_acc = accuracy_score(y_train, y_train_pred)
        test_acc = accuracy_score(y_test, y_test_pred)
        train_loss = log_loss(y_train, y_train_proba)
        test_loss = log_loss(y_test, y_test_proba)
        
        fpr, tpr, _ = roc_curve(y_test, y_test_proba)
        roc_auc = auc(fpr, tpr)
        
        # Save metrics
        metrics_data[cat] = {
            "train_acc": train_acc,
            "test_acc": test_acc,
            "train_loss": train_loss,
            "test_loss": test_loss,
            "roc_auc": roc_auc
        }
        
        # Plot ROC Curve
        ax_roc.plot(fpr, tpr, lw=2, label=f'{cat.capitalize()} (AUC = {roc_auc:.4f})')

    # ROC Plot configuration
    ax_roc.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Guess')
    ax_roc.set_xlim([0.0, 1.0])
    ax_roc.set_ylim([0.0, 1.05])
    ax_roc.set_xlabel('False Positive Rate', fontsize=12)
    ax_roc.set_ylabel('True Positive Rate', fontsize=12)
    ax_roc.set_title('Receiver Operating Characteristic (ROC) Curves', fontsize=14, fontweight='bold')
    ax_roc.legend(loc="lower right", frameon=True, fontsize=10)
    fig_roc.tight_layout()
    fig_roc.savefig(os.path.join(PUBLIC_PLOTS_DIR, "roc_curves.png"), dpi=300)
    plt.close(fig_roc)
    print("Saved roc_curves.png")
    
    categories_keys = list(metrics_data.keys())
    train_accs = [metrics_data[c]["train_acc"] * 100 for c in categories_keys]
    test_accs = [metrics_data[c]["test_acc"] * 100 for c in categories_keys]
    train_losses = [metrics_data[c]["train_loss"] for c in categories_keys]
    test_losses = [metrics_data[c]["test_loss"] for c in categories_keys]
    
    x = np.arange(len(categories_keys))
    width = 0.35
    
    # Plot Accuracy Metrics
    fig_acc, ax_acc = plt.subplots(figsize=(8, 6))
    ax_acc.bar(x - width/2, train_accs, width, label='Train Accuracy', color='#a855f7')
    ax_acc.bar(x + width/2, test_accs, width, label='Test Accuracy', color='#6366f1')
    ax_acc.set_ylabel('Accuracy (%)', fontsize=12)
    ax_acc.set_title('Classifier Train vs Test Accuracy', fontsize=13, fontweight='bold')
    ax_acc.set_xticks(x)
    ax_acc.set_xticklabels([c.capitalize() for c in categories_keys], fontsize=10)
    ax_acc.set_ylim([80, 105])
    ax_acc.legend(loc='lower right')
    fig_acc.tight_layout()
    fig_acc.savefig(os.path.join(PUBLIC_PLOTS_DIR, "accuracy_metrics.png"), dpi=300)
    plt.close(fig_acc)
    print("Saved accuracy_metrics.png")
    
    # Plot Loss Metrics
    fig_loss, ax_loss = plt.subplots(figsize=(8, 6))
    ax_loss.bar(x - width/2, train_losses, width, label='Train Loss', color='#ec4899')
    ax_loss.bar(x + width/2, test_losses, width, label='Test Loss', color='#3b82f6')
    ax_loss.set_ylabel('Log Loss', fontsize=12)
    ax_loss.set_title('Classifier Train vs Test Loss', fontsize=13, fontweight='bold')
    ax_loss.set_xticks(x)
    ax_loss.set_xticklabels([c.capitalize() for c in categories_keys], fontsize=10)
    ax_loss.legend(loc='upper right')
    fig_loss.tight_layout()
    fig_loss.savefig(os.path.join(PUBLIC_PLOTS_DIR, "loss_metrics.png"), dpi=300)
    plt.close(fig_loss)
    print("Saved loss_metrics.png")
    
if __name__ == "__main__":
    main()
