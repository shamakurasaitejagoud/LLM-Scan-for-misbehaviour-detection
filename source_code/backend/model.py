"""
model.py — Mistral 7B + AIE-based Causal Analysis
====================================================
Uses HuggingFace Transformers to load Mistral-7B-v0.1.
Implements the AIE (Attention Intervention Effect) methodology:
  - Layer AIE: per-layer causal importance via logit-difference
  - Prompt AIE: per-token causal effect via token intervention
  - Statistical features: mean, std, range, kurtosis, skewness
"""

import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Dict, List
import os
from scipy.stats import kurtosis, skew
from classifier import MistralAdversarialDetector


class MistralScanner:
    """
    Loads Mistral-7B and performs AIE-based causal analysis.
    Provides:
      - layer_aie_scan()   : per-layer causal importance (logit-difference method)
      - prompt_aie_scan()  : per-token causal effect (token intervention method)
      - extract_features() : statistical summary of causal effects
      - full_scan()        : complete pipeline returning all signals
    """

    def __init__(self, model_id: str = "mistralai/Mistral-7B-Instruct-v0.2", device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_id = model_id
        self.model_name = model_id
        
        print(f"Loading OFFICIAL {model_id} with RAM-to-GPU Offload...")
        
        if self.device == "cuda":
            from transformers import BitsAndBytesConfig
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                llm_int8_enable_fp32_cpu_offload=True,
            )
        else:
            quant_config = None

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id, token=os.getenv("HF_TOKEN"))
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=quant_config,
                low_cpu_mem_usage=True,
                device_map="auto" if self.device == "cuda" else None,
                max_memory={0: "5GB", "cpu": "12GB"} if self.device == "cuda" else None,
                offload_folder="offload",
                torch_dtype=torch.float16,
                attn_implementation="sdpa",
                token=os.getenv("HF_TOKEN")
                )
            print("Official Mistral Loaded successfully!")
            
            from classifier import MistralAdversarialDetector
            self.detector = MistralAdversarialDetector()
            print("Adversarial Detector initialized (Ensemble MLP+RF+SVC).")
        except Exception as e:
            print(f"Failed to load model: {e}")
            raise e

        self.model.eval()
        self.num_layers = self.model.config.num_hidden_layers
        self.hidden_size = self.model.config.hidden_size
        self.intervene_token = "-"

        print(f"Model ready: {self.num_layers} layers, hidden_size={self.hidden_size}")

    # ── Layer AIE Scan ─────────────────────────────────────────────────────

    def layer_aie_scan(self, prompt: str) -> Dict:
        """
        Per-layer causal importance using the logit-difference method.
        For each adjacent layer pair (L, L+1):
          1. Run baseline → get predicted token probability P_baseline
          2. Capture hidden state at layer L, skip layer L+1's computation
          3. Get new probability → P_intervened
          4. layer_aie[L] = |P_baseline - P_intervened|

        Returns dict with 'layer_aie' (list of num_layers-1 floats)
        and 'baseline_logit' (float).
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        input_ids = inputs["input_ids"]

        # Baseline forward pass
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits[:, -1, :].float(), dim=-1)
            baseline_prob, answer_t = torch.max(probs, dim=-1)
            baseline_prob = baseline_prob.item()
            answer_t = answer_t.item()

        layer_aie = []

        for layer_idx in range(0, self.num_layers - 1):
            intervened_prob = self._get_intervened_prob_layer(
                inputs, layer_idx, layer_idx + 1, answer_t
            )
            aie = abs(baseline_prob - intervened_prob)
            layer_aie.append(round(aie, 6))

        return {
            "layer_aie": layer_aie,
            "baseline_logit": round(baseline_prob, 6),
            "num_layers": self.num_layers,
        }

    def _get_intervened_prob_layer(
        self,
        inputs: Dict,
        layer_from: int,
        layer_to: int,
        answer_t: int,
    ) -> float:
        """
        Perform causal intervention by capturing hidden state at layer_from
        and feeding it directly to layer_to (skipping layer_to's computation).
        Uses forward hooks to intercept and shortcut the computation.
        """
        inter_results = {}

        def hook_capture(module, input, output):
            """Capture the output of layer_from."""
            # Move to CPU immediately to free up VRAM during the forward pass
            if isinstance(output, tuple):
                inter_results["hidden_states"] = output[0].detach().cpu()
            else:
                inter_results["hidden_states"] = output.detach().cpu()
            return output

        def hook_replace(module, input, output):
            """Replace the input to layer_to with captured hidden states."""
            if "hidden_states" in inter_results:
                captured = inter_results["hidden_states"].to(self.device)
                if isinstance(output, tuple):
                    return (captured,) + output[1:]
                return captured
            return output

        # Register hooks
        layers = self.model.model.layers
        h_capture = layers[layer_from].register_forward_hook(hook_capture)
        h_replace = layers[layer_to].register_forward_hook(hook_replace)

        try:
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits[:, -1, :].float(), dim=-1)
                intervened_prob = probs[0, answer_t].item()
        finally:
            h_capture.remove()
            h_replace.remove()

        return intervened_prob

    # ── Prompt AIE Scan (Token-level) ──────────────────────────────────────

    def prompt_aie_scan(self, prompt: str) -> Dict:
        """
        Per-token causal effect via token intervention.
        For each token position i in the input:
          1. Replace token i with the intervention token ('-')
          2. Run forward pass → get probability for the baseline's predicted token
          3. token_effect[i] = |P_baseline - P_intervened|

        Returns dict with 'prompt_aie' (list of N floats),
        'tokens' (list of token strings), and 'stats' (statistical features).
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        input_ids = inputs["input_ids"].clone()
        num_tokens = input_ids.shape[1]

        # Get intervention token id
        intervene_ids = self.tokenizer(self.intervene_token)["input_ids"]
        # Skip BOS token if present
        if len(intervene_ids) > 1:
            intervene_token_id = intervene_ids[1]
        else:
            intervene_token_id = intervene_ids[0]

        # Baseline forward pass
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits[:, -1, :].float(), dim=-1)
            baseline_prob, answer_t = torch.max(probs, dim=-1)
            baseline_prob = baseline_prob.item()
            answer_t = answer_t.item()

        # Decode tokens for display
        tokens = [self.tokenizer.decode([input_ids[0, i].item()]) for i in range(num_tokens)]

        # Token-level intervention (Batched for high speed)
        batch_input_ids = input_ids.repeat(num_tokens, 1)  # Shape: (num_tokens, num_tokens)
        for i in range(num_tokens):
            batch_input_ids[i, i] = intervene_token_id

        batch_attention_mask = inputs["attention_mask"].repeat(num_tokens, 1)

        modified_inputs = {
            "input_ids": batch_input_ids,
            "attention_mask": batch_attention_mask,
        }

        with torch.no_grad():
            outputs = self.model(**modified_inputs)
            logits = outputs.logits
            probs = torch.softmax(logits[:, -1, :].float(), dim=-1)
            intervened_probs = probs[:, answer_t].cpu().numpy()

        token_effects = []
        for i in range(num_tokens):
            intervened_prob = intervened_probs[i]
            if np.isnan(intervened_prob) or np.isinf(intervened_prob):
                intervened_prob = 0.0

            # Calculate effect with NaN/Inf protection
            effect = abs(baseline_prob - intervened_prob)
            if np.isnan(effect) or np.isinf(effect):
                effect = 0.0
                
            token_effects.append(round(float(effect), 6))

        # Compute statistical features
        stats = self.extract_features(token_effects)

        return {
            "prompt_aie": token_effects,
            "tokens": tokens,
            "num_tokens": num_tokens,
            "baseline_logit": round(baseline_prob, 6),
            "stats": stats,
        }

    # ── Statistical Feature Extraction ─────────────────────────────────────

    @staticmethod
    def extract_features(data: List[float]) -> Dict[str, float]:
        """
        Extract statistical features from a list of causal effects.
        Matches the original LLM_Scan methodology:
          - mean: average causal effect
          - std: standard deviation
          - range: max - min (np.ptp)
          - kurtosis: peakedness of distribution
          - skewness: asymmetry of distribution
        """
        arr = np.array(data, dtype=np.float64)
        return {
            "mean": round(float(np.mean(arr)), 6),
            "std": round(float(np.std(arr)), 6),
            "range": round(float(np.ptp(arr)), 6),
            "kurtosis": round(float(kurtosis(arr)), 6),
            "skewness": round(float(skew(arr)), 6),
        }

    # ── Full Pipeline ──────────────────────────────────────────────────────

    def full_scan(self, prompt: str) -> Dict:
        """
        Complete AIE scan pipeline:
          1. Layer AIE scan (per-layer causal importance)
          2. Prompt AIE scan (per-token causal effect)
          3. Statistical features from token effects
        Returns all signals for the dashboard.
        """
        import pandas as pd

        # 0. Generate response
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device if hasattr(self.model, "device") else self.device)
        with torch.no_grad():
            gen_output = self.model.generate(
                **inputs, 
                max_new_tokens=500, # Increased for longer responses
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.pad_token_id
            )
        generated_text = self.tokenizer.decode(gen_output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

        # 1. Layer AIE
        layer_result = self.layer_aie_scan(prompt)

        # 2. Prompt AIE (includes stats)
        prompt_result = self.prompt_aie_scan(prompt)

        # 3. Build layer DataFrame
        layer_df = pd.DataFrame({
            "layer_pair": [f"L{i}→L{i+1}" for i in range(len(layer_result["layer_aie"]))],
            "layer_aie": layer_result["layer_aie"],
        })

        # 4. Build token DataFrame
        token_df = pd.DataFrame({
            "token_idx": list(range(prompt_result["num_tokens"])),
            "token": prompt_result["tokens"],
            "prompt_aie": prompt_result["prompt_aie"],
        })

        # 5. Extract features for the detector (Layers 10-30 + Stats)
        # Mistral-7B detectors in LLM_Scan-main were trained on this specific slice
        if len(layer_result["layer_aie"]) >= 31:
            layer_aie_slice = layer_result["layer_aie"][10:31]
        else:
            # Fallback for smaller models (should not happen with Mistral)
            layer_aie_slice = [0.0] * 21

        # 5. Get threat assessment from ensemble detector
        threat_assessment = self.detector.predict(layer_aie_slice, prompt_result["stats"])

        # 6. Conclude safety
        is_safe = True
        unsafe_reasons = []
        
        # HEURISTIC: Only truly trivial prompts (< 15 chars AND ≤ 3 words) get
        # the lenient treatment. This covers "Hello", "Hi", "2+2?" but NOT
        # "how to hijack a server" or "how to bake a cake".
        prompt_len = len(prompt.strip())
        word_count = len(prompt.strip().split())
        is_short_prompt = prompt_len < 15 and word_count <= 3
        
        if is_short_prompt:
            # For trivially short prompts, require MULTIPLE categories at extreme
            # confidence to flag as UNSAFE (suppresses classifier noise).
            STRICT_THRESHOLDS = {
                "jailbreak": 0.98,
                "bias": 0.95,
                "lies": 0.99,
                "toxic": 0.90,
                "backdoor": 0.98
            }
            high_confidence_flags = []
            for cat, prob in threat_assessment.items():
                if prob > STRICT_THRESHOLDS.get(cat, 0.95):
                    high_confidence_flags.append(cat.capitalize())
            
            # Require at least 2 categories to flag a short prompt as UNSAFE
            if len(high_confidence_flags) >= 2:
                is_safe = False
                unsafe_reasons = high_confidence_flags
            else:
                is_safe = True
        else:
            # Calibrated per-classifier thresholds based on reliability:
            #   - toxic: MOST reliable (benign baseline ~0.01-0.05) → low threshold
            #   - jailbreak: reliable (benign baseline ~0.01-0.82) → moderate threshold
            #   - bias: moderate reliability → moderate threshold  
            #   - lies: NOISY (benign baseline ~0.85-0.95) → very high threshold
            #   - backdoor: NOISY (benign baseline ~0.37-0.92) → very high threshold
            THRESHOLDS = {
                "jailbreak": 0.85,
                "bias": 0.80,
                "lies": 0.87,
                "toxic": 0.50,
                "backdoor": 0.97
            }
            
            for cat, prob in threat_assessment.items():
                target_threshold = THRESHOLDS.get(cat, 0.90)
                if prob > target_threshold:
                    is_safe = False
                    unsafe_reasons.append(cat.capitalize())
        
        # Build safety summary
        if not is_safe:
            safety_summary = f"UNSAFE: High confidence {', '.join(unsafe_reasons)} detected."
        elif is_short_prompt:
            # Short prompts that passed strict checks are definitively SAFE
            safety_summary = "SAFE: No significant malicious patterns detected."
        else:
            # Check how many categories show elevated signals
            elevated_cats = sum(1 for p in threat_assessment.values() if p > 0.80)
            max_prob = max(threat_assessment.values()) if threat_assessment else 0
            
            if elevated_cats >= 3 and max_prob > 0.90:
                safety_summary = f"SUSPICIOUS: Multiple elevated signals ({max_prob:.1%}). Proceed with caution."
            elif max_prob > 0.97:
                safety_summary = f"SUSPICIOUS: High signal detected ({max_prob:.1%}). Proceed with caution."
            else:
                safety_summary = "SAFE: No significant malicious patterns detected."

        return {
            "prompt": prompt,
            "generated_text": generated_text,
            "layer_aie": layer_result["layer_aie"],
            "prompt_aie": prompt_result["prompt_aie"],
            "tokens": prompt_result["tokens"],
            "stats": prompt_result["stats"],
            "num_layers": layer_result["num_layers"],
            "num_tokens": prompt_result["num_tokens"],
            "baseline_logit": prompt_result["baseline_logit"],
            "layer_df": layer_df.to_dict(orient="records"),
            "token_df": token_df.to_dict(orient="records"),
            "threat_assessment": threat_assessment,
            "is_safe": is_safe,
            "safety_summary": safety_summary,
        }




    # ── Model Info ─────────────────────────────────────────────────────────

    def get_model_info(self) -> Dict:
        return {
            "model": self.model_name,
            "num_layers": self.num_layers,
            "hidden_size": self.hidden_size,
            "num_heads": self.model.config.num_attention_heads,
            "num_kv_heads": self.model.config.num_key_value_heads,
            "vocab_size": self.model.config.vocab_size,
            "intermediate_size": self.model.config.intermediate_size,
            "device": self.device,
            "dtype": str(self.model.dtype),
        }
