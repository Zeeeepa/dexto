"""FastAPI application with ChatKit integration."""

import json
import logging
import secrets
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.constants import BACKEND_PORT, ALLOWED_ORIGINS
from app.server import VoiceAutomationServer
from app.websocket import connection_manager, event_emitter
from app.auth import auth_manager, PermissionChecker, User
from app.database import database
from app.cache import cache_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize ChatKit server
chatkit_server = VoiceAutomationServer()

# Security
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = auth_manager.verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = auth_manager.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


async def get_optional_user(
    authorization: str = Header(None),
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization[7:]
    payload = auth_manager.verify_token(token)
    
    if payload:
        return auth_manager.get_user_by_id(payload["sub"])
    return None


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


# Authentication endpoints
@app.post("/api/auth/register")
async def register(request: Request):
    """Register new user."""
    body = await request.json()
    
    try:
        user = auth_manager.create_user(
            email=body["email"],
            username=body["username"],
            password=body["password"],
            role=body.get("role", "user"),
        )
        
        # Track registration
        database.track_analytics(
            "user_registered",
            {"user_id": user.id, "role": user.role},
        )
        
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
            "message": "User registered successfully",
        }
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)},
        )


@app.post("/api/auth/login")
async def login(request: Request):
    """Login user."""
    body = await request.json()
    
    user = auth_manager.authenticate(body["email"], body["password"])
    if not user:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid credentials"},
        )
    
    token = auth_manager.create_access_token(user)
    
    # Track login
    database.track_analytics(
        "user_login",
        {"user_id": user.id},
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
        },
    }


@app.get("/api/auth/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information."""
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role,
        "created_at": user.created_at,
        "last_login": user.last_login,
    }


@app.get("/api/users")
async def list_users(user: User = Depends(get_current_user)):
    """List all users (admin only)."""
    PermissionChecker.require_permission(user, "admin")
    
    users = auth_manager.list_users()
    return {
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "role": u.role,
                "created_at": u.created_at,
                "last_login": u.last_login,
                "is_active": u.is_active,
            }
            for u in users
        ],
        "count": len(users),
    }


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    connection_id = secrets.token_hex(8)
    
    try:
        # Accept connection
        await connection_manager.connect(websocket, connection_id)
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await connection_manager.send_personal_message(
                    connection_id,
                    {"type": "pong", "timestamp": datetime.now().isoformat()},
                )
            elif message.get("type") == "subscribe":
                # Handle subscriptions
                pass
            
    except WebSocketDisconnect:
        connection_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        connection_manager.disconnect(connection_id)


# Database-backed workflow endpoints
@app.get("/api/workflows/history")
async def get_workflow_history(
    status: str = None,
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_optional_user),
):
    """Get workflow history from database."""
    workflows = database.list_workflows(status=status, limit=limit, offset=offset)
    
    return {
        "workflows": workflows,
        "count": len(workflows),
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/analytics")
async def get_analytics(
    event_type: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100,
    user: User = Depends(get_current_user),
):
    """Get analytics data (admin only)."""
    PermissionChecker.require_permission(user, "admin")
    
    analytics = database.get_analytics(
        event_type=event_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
    
    return {
        "analytics": analytics,
        "count": len(analytics),
    }


@app.get("/api/cache/stats")
async def get_cache_stats(user: User = Depends(get_current_user)):
    """Get cache statistics."""
    # This would require cache backend to expose stats
    return {
        "backend": type(cache_manager.backend).__name__,
        "available": True,
    }


@app.post("/api/cache/clear")
async def clear_cache(user: User = Depends(get_current_user)):
    """Clear cache (admin only)."""
    PermissionChecker.require_permission(user, "admin")
    
    await cache_manager.clear()
    
    return {"message": "Cache cleared successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=BACKEND_PORT,
        reload=True,
        log_level="info",
    )
