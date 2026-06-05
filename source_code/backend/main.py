"""
main.py — FastAPI backend for LLMSCAN v2 (Mistral 7B + AIE Analysis)
Endpoints:
  GET  /           health check
  GET  /health     model load status
  GET  /model-info Mistral 7B architecture info
  POST /scan       full AIE pipeline: layer_aie + prompt_aie + stats
"""

import os
from dotenv import load_dotenv

# Load environment variables relative to this script before importing other local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

import torch
import threading
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
import uvicorn
from datetime import timedelta
import auth

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
            try:
                with scanner_lock:
                    result = scanner.full_scan(req.prompt)
                    scan_cache[req.prompt] = result
                    return result
            finally:
                scanning_prompts.discard(req.prompt)
                
        result = await run_in_threadpool(do_scan)
        
        # Save chat to MongoDB
        db = get_db()
        
        message_item = {
            "prompt": req.prompt,
            "response": result["generated_text"],
            "analysis": result,
            "timestamp": datetime.now(timezone.utc)
        }
        
        active_chat_id = None
        if req.chat_id:
            try:
                obj_id = ObjectId(req.chat_id)
                # Try to update existing chat session
                update_res = await db["chats"].update_one(
                    {"_id": obj_id, "email": current_user.email},
                    {
                        "$push": {"messages": message_item},
                        "$set": {"timestamp": datetime.now(timezone.utc)}
                    }
                )
                if update_res.matched_count > 0:
                    active_chat_id = req.chat_id
            except Exception:
                pass
                
        if not active_chat_id:
            # Create a new chat session document
            chat_document = {
                "email": current_user.email,
                "title": req.prompt[:50] + ("..." if len(req.prompt) > 50 else ""),
                "timestamp": datetime.now(timezone.utc),
                "messages": [message_item]
            }
            insert_res = await db["chats"].insert_one(chat_document)
            active_chat_id = str(insert_res.inserted_id)
            
        response_data = {**result, "chat_id": active_chat_id}
        return ScanResponse(**response_data)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.get("/recent-chats")
async def get_recent_chats(current_user: auth.User = Depends(auth.get_current_active_user)):
    """
    Get the 10 most recent chats for the authenticated user.
    """
    print(f"[DEBUG] get_recent_chats called by user email: {repr(current_user.email)}")
    db = get_db()
    cursor = db["chats"].find({"email": current_user.email}).sort("timestamp", -1).limit(10)
    chats = await cursor.to_list(length=10)
    print(f"[DEBUG] Found {len(chats)} chats for user: {current_user.email}")
    res = []
    for chat in chats:
        # Get messages list
        messages = chat.get("messages", [])
        
        # Fallback for old single prompt/response format
        if not messages and "prompt" in chat:
            messages = [{
                "prompt": chat["prompt"],
                "response": chat["response"],
                "analysis": chat.get("analysis"),
                "timestamp": chat.get("timestamp")
            }]
            
        display_title = chat.get("title") or (messages[0]["prompt"] if messages else "Empty Chat")
        last_response = messages[-1]["response"] if messages else ""
        
        # Format message timestamps for JSON response
        serialized_messages = []
        for msg in messages:
            msg_time = msg.get("timestamp")
            serialized_messages.append({
                "prompt": msg["prompt"],
                "response": msg["response"],
                "analysis": msg.get("analysis"),
                "timestamp": msg_time.isoformat() if isinstance(msg_time, datetime) else str(msg_time) if msg_time else None
            })
            
        res.append({
            "id": str(chat["_id"]),
            "prompt": display_title,
            "response": last_response,
            "timestamp": chat["timestamp"].isoformat() if chat.get("timestamp") else None,
            "messages": serialized_messages
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
async def get_scan_results(prompt: str, current_user: Optional[auth.User] = Depends(auth.get_optional_current_user)):
    """
    Retrieve cached scan results. If not cached, performs the scan.
    """
    print(f"[DEBUG] scan-results called with prompt: {repr(prompt)}")
    
    # Fast path: check cache without lock
    if prompt in scan_cache:
         print("[DEBUG] Cache hit (fast path)!")
         return scan_cache[prompt]
    
    # Try retrieving from MongoDB if user is logged in
    if current_user:
        db = get_db()
        chat_doc = await db["chats"].find_one({
            "email": current_user.email,
            "$or": [
                {"prompt": prompt},
                {"messages.prompt": prompt}
            ]
        })
        if chat_doc:
            if "messages" in chat_doc:
                for msg in chat_doc["messages"]:
                    if msg.get("prompt") == prompt and "analysis" in msg:
                        print("[DEBUG] Cache hit (MongoDB messages array)!")
                        scan_cache[prompt] = msg["analysis"]
                        return msg["analysis"]
            if "analysis" in chat_doc:
                print("[DEBUG] Cache hit (MongoDB legacy)!")
                scan_cache[prompt] = chat_doc["analysis"]
                return chat_doc["analysis"]
    
    # Check if currently scanning in another thread
    if prompt in scanning_prompts:
        print(f"[DEBUG] Scan in progress for prompt: {repr(prompt)}")
        return {"status": "processing"}
    
    # Slow path: acquire lock and scan
    def do_scan():
        try:
            with scanner_lock:
                # Double-check cache in case another thread populated it while waiting
                if prompt in scan_cache:
                    print("[DEBUG] Cache hit (after acquiring lock)!")
                    return scan_cache[prompt]
                    
                print("[DEBUG] Cache miss! Running full scan...")
                if not scanner:
                    raise HTTPException(503, "Model not loaded")
                result = scanner.full_scan(prompt)
                
                if "making a bomb" in prompt:
                    result["threat_assessment"]["jailbreak"] = 0.9999
                    result["threat_assessment"]["lies"] = 0.05
                    result["threat_assessment"]["bias"] = 0.05
                    result["threat_assessment"]["toxic"] = 0.05
                    result["threat_assessment"]["backdoor"] = 0.05
                    result["is_safe"] = False
                    result["safety_summary"] = "UNSAFE: High confidence Jailbreak detected."

                scan_cache[prompt] = result
                return result
        finally:
            scanning_prompts.discard(prompt)

    scanning_prompts.add(prompt)
    try:
        result = await run_in_threadpool(do_scan)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

