"""
classifier.py — Statistical Feature Extraction for AIE Analysis
================================================================
Provides utility functions for extracting statistical features
from causal effect distributions. Used by the MistralScanner
to summarize token-level and layer-level AIE signals.

Features extracted:
  - mean: average causal effect
  - std: standard deviation
  - range: max - min
  - kurtosis: peakedness of distribution
  - skewness: asymmetry of distribution
"""

import os
import numpy as np
from scipy.stats import kurtosis, skew
from typing import Dict, List
from joblib import load


class MistralAdversarialDetector:
    """
    Enhanced Inference classifier for Mistral-7B.
    Uses an ensemble of MLP and Random Forest for high robustness.
    """
    def __init__(self, detectors_dir: str = None):
        if detectors_dir is None:
            detectors_dir = os.path.join(os.path.dirname(__file__), "detectors")
        
        self.detectors_dir = detectors_dir
        self.categories = ["jailbreak", "bias", "lies", "toxic", "backdoor"]
        self.ensemble_models = {}
        self.scalers = {}

        self._load_models()

    def _load_models(self):
        for cat in self.categories:
            ensemble_path = os.path.join(self.detectors_dir, f"mistral_{cat}.joblib")
            scaler_path = os.path.join(self.detectors_dir, f"scaler_{cat}.joblib")
            
            if os.path.exists(ensemble_path) and os.path.exists(scaler_path):
                self.ensemble_models[cat] = load(ensemble_path)
                self.scalers[cat] = load(scaler_path)
                print(f"Loaded {cat} Multi-Classifier Stacked Ensemble (MLP+RF+SVC).")

    def predict(self, layer_aie: List[float], prompt_stats: Dict[str, float]) -> Dict[str, float]:
        # Ignore prompt_stats entirely to eliminate prompt stats out-of-distribution mismatch
        arr = np.array(layer_aie)
        
        # Feature Augmentation (matches training)
        log_arr = np.log(np.abs(arr) + 1e-6)
        sq_arr = arr ** 2
        sign_arr = np.sign(arr)
        
        # Enhanced features (126)
        norm_arr = arr / (np.max(np.abs(arr)) + 1e-8)
        diff_arr = np.diff(arr, prepend=arr[0])
        
        raw_features = np.concatenate([arr, norm_arr, log_arr, sq_arr, sign_arr, diff_arr]).reshape(1, -1)



        
        # Heuristic: Max AIE booster
        max_aie = max(layer_aie) if layer_aie else 0.0


        results = {}
        for cat in self.categories:
            if cat in self.ensemble_models:
                scaled = self.scalers[cat].transform(raw_features)
                ensemble_prob = self.ensemble_models[cat].predict_proba(scaled)[0][1]
                
                results[cat] = round(float(ensemble_prob), 4)
            else:
                results[cat] = 0.0

        return results









def extract_features(data: List[float]) -> Dict[str, float]:
    """
    Extract statistical features from a list of causal effects.
    Matches the original LLM_Scan methodology from
    causal_inference_on_attentions_IE.py::extract_features().

    Parameters:
        data: list of float values (AIE effects per token or per layer)

    Returns:
        dict with keys: mean, std, range, kurtosis, skewness
    """
    arr = np.array(data, dtype=np.float64)

    if len(arr) == 0:
        return {
            "mean": 0.0,
            "std": 0.0,
            "range": 0.0,
            "kurtosis": 0.0,
            "skewness": 0.0,
        }

    return {
        "mean": round(float(np.mean(arr)), 6),
        "std": round(float(np.std(arr)), 6),
        "range": round(float(np.ptp(arr)), 6),
        "kurtosis": round(float(kurtosis(arr)), 6),
        "skewness": round(float(skew(arr)), 6),
    }


def extract_features_batch(data_list: List[List[float]]) -> List[Dict[str, float]]:
    """
    Extract statistical features for multiple distributions.

    Parameters:
        data_list: list of lists of float values

    Returns:
        list of feature dicts
    """
    return [extract_features(d) for d in data_list]
