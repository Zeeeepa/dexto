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


# Request monitoring middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Monitor and log all requests."""
    import time
    from app.monitoring import request_logger, metrics
    from app.security import ContentSecurityPolicy
    
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log request
        request_logger.log_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration=duration,
        )
        
        # Update metrics
        metrics.record_time("request_duration", duration)
        
        # Add security headers
        for header, value in ContentSecurityPolicy.get_security_headers().items():
            response.headers[header] = value
        
        return response
        
    except Exception as e:
        duration = time.time() - start_time
        
        # Log error
        request_logger.log_request(
            method=request.method,
            path=request.url.path,
            status_code=500,
            duration=duration,
            error=str(e),
        )
        
        # Re-raise
        raise


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


@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics."""
    from app.monitoring import metrics
    return metrics.get_all_metrics()


@app.get("/api/health/detailed")
async def detailed_health():
    """Get detailed health information."""
    from app.monitoring import health_checker
    return health_checker.check_system_health()


@app.get("/api/templates")
async def list_templates(category: str = None):
    """List workflow templates."""
    from app.workflow_templates import WorkflowTemplateLibrary, WorkflowCategory
    
    cat = WorkflowCategory(category) if category else None
    templates = WorkflowTemplateLibrary.list_templates(cat)
    
    return {
        "templates": [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "category": t.category.value,
                "agents": t.agents,
                "estimated_duration": t.estimated_duration,
                "required_inputs": t.required_inputs,
            }
            for t in templates
        ],
        "count": len(templates),
    }


@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """Get template details."""
    from app.workflow_templates import WorkflowTemplateLibrary
    
    try:
        template = WorkflowTemplateLibrary.get_template(template_id)
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "category": template.category.value,
            "agents": template.agents,
            "steps": template.steps,
            "estimated_duration": template.estimated_duration,
            "required_inputs": template.required_inputs,
        }
    except ValueError as e:
        return JSONResponse(
            status_code=404,
            content={"error": str(e)}
        )


@app.post("/api/workflows/from-template")
async def create_from_template(request: Request):
    """Create workflow from template."""
    from app.workflow_templates import WorkflowTemplateLibrary
    
    body = await request.json()
    template_id = body.get("template_id")
    inputs = body.get("inputs", {})
    
    if not template_id:
        return JSONResponse(
            status_code=400,
            content={"error": "template_id required"}
        )
    
    try:
        workflow = WorkflowTemplateLibrary.create_workflow_from_template(
            template_id, inputs
        )
        
        # Add to active workflows
        workflow_id = f"wf_{len(chatkit_server.active_workflows) + 1}"
        workflow["id"] = workflow_id
        workflow["status"] = "created"
        workflow["created_at"] = datetime.now().isoformat()
        
        chatkit_server.active_workflows[workflow_id] = workflow
        logger.info(f"Created workflow from template {template_id}: {workflow_id}")
        
        return workflow
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )


@app.get("/api/security/audit-log")
async def get_audit_log(limit: int = 100):
    """Get audit log entries."""
    from app.security import audit_logger
    return {
        "entries": audit_logger.get_recent_events(limit),
        "count": len(audit_logger.get_recent_events(limit)),
    }


@app.get("/api/errors/statistics")
async def get_error_stats():
    """Get error statistics."""
    from app.error_handling import error_handler
    return error_handler.get_error_statistics()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=BACKEND_PORT,
        reload=True,
        log_level="info",
    )
