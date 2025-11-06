"""Configuration constants for Voice Automation Hub."""

import os
from pathlib import Path

# API Configuration
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CHATKIT_DOMAIN_KEY = os.getenv("CHATKIT_DOMAIN_KEY", "")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_MODEL = "gpt-4-turbo-preview"

# Agent Configuration
ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "gpt-4-turbo-preview")
SUB_AGENT_MODEL = os.getenv("SUB_AGENT_MODEL", "gpt-4o-mini")

# Storage
BASE_DIR = Path(__file__).parent.parent
STORAGE_PATH = BASE_DIR / "data"
STORAGE_PATH.mkdir(exist_ok=True)

# MCP Configuration
MCP_CONFIG_PATH = os.getenv("MCP_CONFIG_PATH", str(BASE_DIR / "mcp.json"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# CORS
ALLOWED_ORIGINS = [
    FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

