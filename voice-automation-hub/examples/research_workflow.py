#!/usr/bin/env python3
"""
Example: Research Workflow
Demonstrates voice-controlled research automation with sub-agents.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.server import VoiceAutomationServer


async def research_workflow_example():
    """Execute a research workflow via voice automation."""
    
    print("\n" + "=" * 70)
    print("🔬 Voice Automation Hub - Research Workflow Example")
    print("=" * 70 + "\n")
    
    # Initialize server
    print("📦 Initializing Voice Automation Server...")
    server = VoiceAutomationServer()
    print("✅ Server initialized\n")
    
    # Create a research task
    task_description = """
Research the top 5 AI agent frameworks released in 2024.
For each framework:
1. Extract key features and capabilities
2. Find GitHub stars and community metrics  
3. Analyze pros and cons
4. Create comparison table
5. Generate executive summary
    """.strip()
    
    print(f"📋 Task Description:")
    print(f"   {task_description}\n")
    
    # Create workflow
    workflow_id = f"wf_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow = {
        "id": workflow_id,
        "task": task_description,
        "status": "created",
        "thread_id": "example_thread",
        "agents": [
            {
                "name": "ResearchAgent",
                "role": "Web research and data collection",
                "tools": ["browser", "search", "scraper"],
                "status": "pending",
                "tasks": [
                    "Search for AI agent frameworks from 2024",
                    "Collect data on features and metrics",
                    "Extract community engagement data"
                ]
            },
            {
                "name": "AnalyzerAgent",
                "role": "Data analysis and comparison",
                "tools": ["analyzer", "comparator", "metrics"],
                "status": "pending",
                "tasks": [
                    "Analyze features across frameworks",
                    "Compare GitHub stats",
                    "Identify pros and cons"
                ]
            },
            {
                "name": "SummarizerAgent",
                "role": "Generate executive summary",
                "tools": ["summarizer", "writer", "formatter"],
                "status": "pending",
                "tasks": [
                    "Create comparison table",
                    "Generate insights summary",
                    "Format final report"
                ]
            }
        ],
        "created_at": datetime.now().isoformat(),
        "progress": 0,
    }
    
    server.active_workflows[workflow_id] = workflow
    
    print(f"✅ Workflow created: {workflow_id}\n")
    print("🤖 Sub-Agents:")
    for agent in workflow["agents"]:
        print(f"\n   📍 {agent['name']}")
        print(f"      Role: {agent['role']}")
        print(f"      Tools: {', '.join(agent['tools'])}")
        print(f"      Tasks:")
        for task in agent['tasks']:
            print(f"        • {task}")
    
    print("\n" + "-" * 70)
    print("⚡ Executing workflow...\n")
    
    # Simulate workflow execution
    total_steps = len(workflow["agents"])
    
    for idx, agent in enumerate(workflow["agents"], 1):
        print(f"Step {idx}/{total_steps}: {agent['name']} starting...")
        agent["status"] = "running"
        agent["started_at"] = datetime.now().isoformat()
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        # Update progress
        progress = int((idx / total_steps) * 100)
        workflow["progress"] = progress
        
        # Complete agent
        agent["status"] = "completed"
        agent["completed_at"] = datetime.now().isoformat()
        agent["results"] = {
            "status": "success",
            "output": f"{agent['name']} completed successfully"
        }
        
        print(f"  ✓ {agent['name']} completed")
        print(f"  📊 Progress: {progress}%\n")
    
    # Mark workflow complete
    workflow["status"] = "completed"
    workflow["completed_at"] = datetime.now().isoformat()
    workflow["progress"] = 100
    
    # Display results
    print("-" * 70)
    print("\n✅ Workflow Completed Successfully!\n")
    print("📊 Results:\n")
    print("Top 5 AI Agent Frameworks (2024):")
    print("=" * 70)
    
    frameworks = [
        ("LangGraph", "Advanced agent workflow orchestration", "⭐ 45.2k"),
        ("AutoGen", "Multi-agent conversation framework", "⭐ 32.8k"),
        ("CrewAI", "Role-based agent collaboration", "⭐ 28.5k"),
        ("Semantic Kernel", "Microsoft's agent SDK", "⭐ 21.3k"),
        ("Haystack", "NLP-focused agent pipeline", "⭐ 18.7k"),
    ]
    
    for i, (name, desc, stars) in enumerate(frameworks, 1):
        print(f"\n{i}. {name}")
        print(f"   {desc}")
        print(f"   {stars}")
    
    # Calculate execution time
    start_time = datetime.fromisoformat(workflow['created_at'])
    end_time = datetime.fromisoformat(workflow['completed_at'])
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n" + "=" * 70)
    print(f"\n⏱️  Total execution time: {duration:.1f}s")
    print(f"📈 Agents executed: {len(workflow['agents'])}")
    print(f"✅ Success rate: 100%")
    
    print(f"\n💡 Voice Command Example:")
    print('   "Research AI agent frameworks and create a comparison report"')
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(research_workflow_example())
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

