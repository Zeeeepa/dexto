"""
Voice Automation Hub - Project Setup Script
This script generates all project files with proper structure.
"""

import os
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent

# File contents dictionary
FILES = {
    # Backend files
    "backend/requirements.txt": """# Core Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
pydantic-settings==2.5.2

# ChatKit & Agents
openai-chatkit==1.0.0
openai-agents>=0.3.2

# OpenAI
openai>=1.0.0

# Async & Utilities
httpx==0.27.0
python-multipart==0.0.9
python-dotenv==1.0.1

# Storage & State
aiosqlite==0.20.0

# Testing
pytest==8.3.0
pytest-asyncio==0.24.0
pytest-cov==5.0.0
""",

    "backend/pyproject.toml": """[project]
name = "voice-automation-hub-backend"
version = "0.1.0"
description = "Voice-controlled AI automation platform backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic>=2.9.0",
    "openai-chatkit>=1.0.0",
    "openai-agents>=0.3.2",
    "openai>=1.0.0",
    "httpx>=0.27.0",
    "python-multipart>=0.0.9",
    "python-dotenv>=1.0.1",
    "aiosqlite>=0.20.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
""",

    "backend/app/__init__.py": """\"\"\"Voice Automation Hub backend application.\"\"\"
""",

    "backend/app/constants.py": open(PROJECT_ROOT / "backend/app/constants.py").read() if (PROJECT_ROOT / "backend/app/constants.py").exists() else "",
}

def create_files():
    """Create all project files."""
    print("🚀 Setting up Voice Automation Hub project structure...")
    print()
    
    created_count = 0
    for file_path, content in FILES.items():
        full_path = PROJECT_ROOT / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Created: {file_path}")
        created_count += 1
    
    print()
    print(f"✅ Successfully created {created_count} files!")
    print()
    print("Next steps:")
    print("1. cd backend && pip install -r requirements.txt")
    print("2. cd frontend && npm install")
    print("3. Configure .env file with your API keys")
    print("4. Run deployment/windows/start.bat (Windows) or follow README.md")
    print()

if __name__ == "__main__":
    create_files()

