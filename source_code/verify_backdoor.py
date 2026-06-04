import numpy as np
from joblib import load
import os

# features from API response
layer_aie = [0.044411, 0.008193, 0.047562, 0.155155, 0.080666, 0.20147, 0.045857, 0.069369, 0.092515, 0.013386, 0.101508, 0.208543, 0.039704, 0.203934, 0.005116, 0.143513, 0.019085, 0.057448, 0.087713, 0.000898, 0.1732]

arr = np.array(layer_aie)
log_arr = np.log(np.abs(arr) + 1e-6)
sq_arr = arr ** 2
sign_arr = np.sign(arr)
norm_arr = arr / (np.max(np.abs(arr)) + 1e-8)
diff_arr = np.diff(arr, prepend=arr[0])

raw_features = np.concatenate([arr, norm_arr, log_arr, sq_arr, sign_arr, diff_arr]).reshape(1, -1)

detectors_dir = os.path.join("backend", "detectors")
categories = ["jailbreak", "bias", "lies", "toxic", "backdoor"]

for cat in categories:
    clf = load(os.path.join(detectors_dir, f"mistral_{cat}.joblib"))
    scaler = load(os.path.join(detectors_dir, f"scaler_{cat}.joblib"))
    
    scaled = scaler.transform(raw_features)
    prob = clf.predict_proba(scaled)[0][1]
    print(f"{cat}: {prob:.4f}")
