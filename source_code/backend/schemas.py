"""
schemas.py — Pydantic request/response schemas for FastAPI
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ScanRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000, description="Prompt to scan")
    chat_id: Optional[str] = Field(None, description="Active chat session ID")


class StatsResult(BaseModel):
    mean: float
    std: float
    range: float
    kurtosis: float
    skewness: float


class ThreatAssessment(BaseModel):
    jailbreak: float = Field(..., description="Jailbreak probability")
    bias: float = Field(..., description="Bias probability")
    lies: float = Field(..., description="Lying probability")
    toxic: float = Field(..., description="Toxicity probability")
    backdoor: float = Field(0.0, description="Backdoor (BadMagic) probability")




class ScanResponse(BaseModel):
    prompt: str
    generated_text: str

    # Layer AIE: per-layer causal importance (num_layers - 1 values)
    layer_aie: List[float]

    # Prompt AIE: per-token causal effect (num_tokens values)
    prompt_aie: List[float]

    # Decoded token strings
    tokens: List[str]

    # Statistical features of token-level causal effects
    stats: StatsResult

    # Threat assessment results (probabilities)
    threat_assessment: ThreatAssessment

    # Metadata
    num_layers: int
    num_tokens: int
    baseline_logit: float

    # Overall safety status
    is_safe: bool = Field(..., description="True if no category exceeds threshold")
    safety_summary: str = Field(..., description="Summary of the safety conclusion")

    # Active chat session ID
    chat_id: Optional[str] = Field(None, description="Active chat session ID")

    # DataFrames as list of records (for dashboard)
    layer_df: List[Dict]
    token_df: List[Dict]

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What is 2+2?",
                "layer_aie": [0.001, 0.003, 0.012],
                "prompt_aie": [0.05, 0.02, 0.08, 0.01],
                "tokens": ["What", " is", " 2", "+2", "?"],
                "stats": {
                    "mean": 0.04,
                    "std": 0.025,
                    "range": 0.07,
                    "kurtosis": -1.2,
                    "skewness": 0.3,
                },
                "num_layers": 32,
                "num_tokens": 5,
                "baseline_logit": 0.95,
            }
        }
