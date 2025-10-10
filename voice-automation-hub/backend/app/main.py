"""FastAPI application with ChatKit integration."""

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from app.constants import BACKEND_PORT, ALLOWED_ORIGINS
from app.server import VoiceAutomationServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize ChatKit server
chatkit_server = VoiceAutomationServer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Voice Automation Hub starting...")
    logger.info(f"Backend running on port {BACKEND_PORT}")
    yield
    logger.info("👋 Voice Automation Hub shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Voice Automation Hub API",
    description="Voice-controlled AI automation platform backend",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Voice Automation Hub",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chatkit": "/chatkit",
            "workflows": "/api/workflows",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_workflows": len(chatkit_server.active_workflows),
    }


@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """ChatKit SSE endpoint for client communication."""

    async def event_generator():
        """Generate Server-Sent Events for ChatKit client."""
        try:
            # Parse request body
            body = await request.json()
            
            # Create request context
            context = {"user_id": "default_user", "request_data": body}

            # Process request through ChatKit server
            async for event in chatkit_server.handle_request(body, context):
                # Format as SSE
                if isinstance(event, dict):
                    yield f"data: {json.dumps(event)}\n\n"
                else:
                    # Event object, serialize to JSON
                    event_dict = {}
                    if hasattr(event, "__dict__"):
                        event_dict = {
                            k: v for k, v in event.__dict__.items() 
                            if not k.startswith("_")
                        }
                    yield f"data: {json.dumps(event_dict)}\n\n"

        except Exception as e:
            logger.error(f"Error in ChatKit stream: {e}", exc_info=True)
            yield f'data: {{"error": "{str(e)}"}}\n\n'

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/workflows")
async def list_workflows():
    """List all active workflows."""
    return {
        "workflows": list(chatkit_server.active_workflows.values()),
        "count": len(chatkit_server.active_workflows),
    }


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow details."""
    if workflow_id not in chatkit_server.active_workflows:
        return JSONResponse(
            status_code=404,
            content={"error": "Workflow not found"}
        )

    return chatkit_server.active_workflows[workflow_id]


@app.post("/api/workflows")
async def create_workflow(request: Request):
    """Create a new workflow."""
    body = await request.json()
    task = body.get("task", "")
    
    if not task:
        return JSONResponse(
            status_code=400,
            content={"error": "Task description required"}
        )

    from datetime import datetime
    
    workflow_id = f"wf_{len(chatkit_server.active_workflows) + 1}"
    workflow = {
        "id": workflow_id,
        "task": task,
        "status": "created",
        "agents": [],
        "progress": 0,
        "created_at": datetime.now().isoformat(),
    }

    chatkit_server.active_workflows[workflow_id] = workflow
    logger.info(f"Created workflow {workflow_id}: {task}")

    return workflow


@app.delete("/api/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow."""
    if workflow_id not in chatkit_server.active_workflows:
        return JSONResponse(
            status_code=404,
            content={"error": "Workflow not found"}
        )

    del chatkit_server.active_workflows[workflow_id]
    return {"message": f"Workflow {workflow_id} deleted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=BACKEND_PORT,
        reload=True,
        log_level="info",
    )

