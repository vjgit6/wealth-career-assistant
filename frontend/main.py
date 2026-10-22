"""Standalone Web Chat Application for Personal Wealth & Career Assistant.

Serves an interactive Web Chat UI and routes user queries directly to the
ADK agent running with Google Vertex AI Gemini 3.8 Flash and live Python tools.
"""

import os
import uuid
import asyncio
from typing import Dict, Any, List

import dotenv
dotenv.load_dotenv()
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_PROJECT"] = "qwiklabs-gcp-03-bed266f9aff1"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# ADK imports
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from app.agent import root_agent

app = FastAPI(title="Personal Wealth & Career Web Assistant")

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, session_service=session_service, app_name="wealth_career_app")
user_sessions: Dict[str, str] = {}

# Serve static web frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def index():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/health")
def health():
    return {"status": "ok", "agent": "wealth_career_assistant"}

@app.post("/chat")
async def chat(req: Request):
    try:
        body = await req.json()
        message_text = body.get("message", "").strip()
        user_id = body.get("user_id") or "web-user"

        if not message_text:
            return JSONResponse({"parts": [{"kind": "text", "text": "Please provide a query."}]})

        # Ensure active session
        session_id = user_sessions.get(user_id)
        if not session_id:
            session_id = str(uuid.uuid4())
            await session_service.create_session(
                session_id=session_id,
                user_id=user_id,
                app_name="wealth_career_app"
            )
            user_sessions[user_id] = session_id

        # Wrap user message
        user_msg = types.Content(
            role="user",
            parts=[types.Part.from_text(text=message_text)]
        )

        response_chunks: List[str] = []
        async for event in runner.run_async(session_id=session_id, user_id=user_id, new_message=user_msg):
            if hasattr(event, "content") and event.content:
                for p in event.content.parts:
                    if getattr(p, "text", None):
                        response_chunks.append(p.text)

        full_reply = "".join(response_chunks).strip() or "Understood. Let me know if you would like to explore another market or property analysis."

        return JSONResponse({"parts": [{"kind": "text", "text": full_reply}]})

    except Exception as e:
        return JSONResponse(
            status_code=200,
            content={"parts": [{"kind": "text", "text": f"Error: {type(e).__name__}: {str(e)}"}]}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
