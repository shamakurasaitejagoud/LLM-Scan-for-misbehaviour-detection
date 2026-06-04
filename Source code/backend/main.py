"""
main.py — FastAPI backend for LLMSCAN v2 (Mistral 7B + AIE Analysis)
Endpoints:
  GET  /           health check
  GET  /health     model load status
  GET  /model-info Mistral 7B architecture info
  POST /scan       full AIE pipeline: layer_aie + prompt_aie + stats
"""

import torch
import threading
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
import uvicorn
from dotenv import load_dotenv
from datetime import timedelta
import os
import auth

# Load environment variables (HF_TOKEN)
load_dotenv()

from model import MistralScanner
from schemas import ScanRequest, ScanResponse
from starlette.concurrency import run_in_threadpool
from database import get_db
from datetime import datetime, timezone
from bson import ObjectId

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the Mistral 7B model and detectors
    global scanner
    print("Initializing LLMSCAN v2 Lifespan...")
    scanner = MistralScanner()
    yield
    # Shutdown: Clean up resources if needed
    print("Shutting down LLMSCAN v2...")
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

app = FastAPI(
    title="LLMSCAN API",
    description="AIE-based Causal Misbehavior Detection — Mistral 7B",
    version="2.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

scanner: Optional[MistralScanner] = None


@app.get("/")
def root():
    return {"status": "LLMSCAN running", "model": "Mistral-7B-Instruct-v0.2"}


@app.get("/health")
def health():
    return {"ok": True, "model_loaded": scanner is not None}


@app.get("/model-info")
def model_info():
    if not scanner:
        raise HTTPException(503, "Model not loaded")
    return scanner.get_model_info()


scan_cache = {}
scanner_lock = threading.Lock()
scanning_prompts = set()


@app.post("/scan", response_model=ScanResponse)
async def scan(req: ScanRequest, current_user: auth.User = Depends(auth.get_current_active_user)):
    """
    Full AIE pipeline:
      1. Layer AIE scan — per-layer causal importance via logit-difference
      2. Prompt AIE scan — per-token causal effect via token intervention
      3. Statistical features — mean, std, range, kurtosis, skewness
    """
    if not scanner:
        raise HTTPException(503, "Model not loaded")
    
    scanning_prompts.add(req.prompt)
    try:
        def do_scan():
            with scanner_lock:
                result = scanner.full_scan(req.prompt)
                scan_cache[req.prompt] = result
                return result
                
        result = await run_in_threadpool(do_scan)
        
        # Save chat to MongoDB
        db = get_db()
        chat_document = {
            "email": current_user.email,
            "prompt": req.prompt,
            "response": result["generated_text"],
            "analysis": result,
            "timestamp": datetime.now(timezone.utc)
        }
        await db["chats"].insert_one(chat_document)
        
        return ScanResponse(**result)
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        scanning_prompts.discard(req.prompt)


@app.get("/recent-chats")
async def get_recent_chats(current_user: auth.User = Depends(auth.get_current_active_user)):
    """
    Get the 10 most recent chats for the authenticated user.
    """
    db = get_db()
    cursor = db["chats"].find({"email": current_user.email}).sort("timestamp", -1).limit(10)
    chats = await cursor.to_list(length=10)
    res = []
    for chat in chats:
        res.append({
            "id": str(chat["_id"]),
            "prompt": chat["prompt"],
            "response": chat["response"],
            "timestamp": chat["timestamp"].isoformat() if chat.get("timestamp") else None
        })
    return res


@app.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str, current_user: auth.User = Depends(auth.get_current_active_user)):
    """
    Delete a specific chat by ID, ensuring it belongs to the authenticated user.
    """
    db = get_db()
    try:
        obj_id = ObjectId(chat_id)
    except Exception:
        raise HTTPException(400, "Invalid chat ID format")
    
    result = await db["chats"].delete_one({"_id": obj_id, "email": current_user.email})
    if result.deleted_count == 0:
        raise HTTPException(404, "Chat not found or unauthorized")
        
    return {"ok": True}


@app.get("/scan-results")
async def get_scan_results(prompt: str, current_user: auth.User = Depends(auth.get_current_active_user)):
    """
    Retrieve cached scan results. If not cached, performs the scan.
    """
    print(f"[DEBUG] scan-results called with prompt: {repr(prompt)}")
    
    # Fast path: check cache without lock
    if prompt in scan_cache:
        print("[DEBUG] Cache hit (fast path)!")
        return scan_cache[prompt]
    
    # Try retrieving from MongoDB
    db = get_db()
    chat_doc = await db["chats"].find_one({"email": current_user.email, "prompt": prompt})
    if chat_doc and "analysis" in chat_doc:
        print("[DEBUG] Cache hit (MongoDB)!")
        scan_cache[prompt] = chat_doc["analysis"]
        return chat_doc["analysis"]
    
    # Check if currently scanning in another thread
    if prompt in scanning_prompts:
        print(f"[DEBUG] Scan in progress for prompt: {repr(prompt)}")
        return {"status": "processing"}
    
    # Slow path: acquire lock and scan
    def do_scan():
        with scanner_lock:
            # Double-check cache in case another thread populated it while waiting
            if prompt in scan_cache:
                print("[DEBUG] Cache hit (after acquiring lock)!")
                return scan_cache[prompt]
                
            print("[DEBUG] Cache miss! Running full scan...")
            if not scanner:
                raise HTTPException(503, "Model not loaded")
            result = scanner.full_scan(prompt)
            scan_cache[prompt] = result
            return result

    scanning_prompts.add(prompt)
    try:
        result = await run_in_threadpool(do_scan)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        scanning_prompts.discard(prompt)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

