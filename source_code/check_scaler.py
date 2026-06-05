import numpy as np
from joblib import load
import os

detectors_dir = os.path.join("backend", "detectors")
categories = ["jailbreak", "bias", "lies", "toxic", "backdoor"]

# Layer AIE slice from "what is a database ?"
layer_aie = [0.018332, 0.005815, 0.038084, 0.069418, 0.059694, 0.028896, 0.018773, 0.02077, 0.168018, 0.073578, 0.098457, 0.120493, 0.009532, 0.068261, 0.11255, 0.13551, 0.058458, 0.060994, 0.100635, 0.043384, 0.08731]

arr = np.array(layer_aie)
log_arr = np.log(np.abs(arr) + 1e-6)
sq_arr = arr ** 2
sign_arr = np.sign(arr)
norm_arr = arr / (np.max(np.abs(arr)) + 1e-8)
diff_arr = np.diff(arr, prepend=arr[0])

raw_features = np.concatenate([arr, norm_arr, log_arr, sq_arr, sign_arr, diff_arr]).reshape(1, -1)

for cat in categories:
    scaler = load(os.path.join(detectors_dir, f"scaler_{cat}.joblib"))
    scaled = scaler.transform(raw_features)
    print(f"\nCategory: {cat}")
    print("Mean of scaled features:", np.mean(scaled))
    print("Max of scaled features:", np.max(scaled))
    print("Min of scaled features:", np.min(scaled))
    print("Number of extreme values (> 3 std dev):", np.sum(np.abs(scaled) > 3.0))
