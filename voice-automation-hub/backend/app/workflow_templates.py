"""Workflow templates library for common automation patterns."""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class WorkflowCategory(Enum):
    """Workflow categories."""
    SOFTWARE_DEV = "software_development"
    DATA_ANALYSIS = "data_analysis"
    RESEARCH = "research"
    TESTING = "testing"
    DEPLOYMENT = "deployment"


@dataclass
class WorkflowTemplate:
    """Workflow template definition."""
    id: str
    name: str
    description: str
    category: WorkflowCategory
    agents: List[str]
    steps: List[Dict[str, Any]]
    estimated_duration: str
    required_inputs: List[str]


class WorkflowTemplateLibrary:
    """Library of pre-defined workflow templates."""

    @staticmethod
    def get_template(template_id: str) -> WorkflowTemplate:
        """Get workflow template by ID."""
        templates = WorkflowTemplateLibrary.list_templates()
        for template in templates:
            if template.id == template_id:
                return template
        raise ValueError(f"Template not found: {template_id}")

    @staticmethod
    def list_templates(
        category: WorkflowCategory = None
    ) -> List[WorkflowTemplate]:
        """List all workflow templates, optionally filtered by category."""
        all_templates = [
            # Software Development Templates
            WorkflowTemplate(
                id="code_review_comprehensive",
                name="Comprehensive Code Review",
                description="Multi-agent code review with quality, security, and performance analysis",
                category=WorkflowCategory.SOFTWARE_DEV,
                agents=["CodeAgent", "TestAgent", "SecurityAgent"],
                steps=[
                    {
                        "name": "Static Analysis",
                        "agent": "CodeAgent",
                        "tool": "analyze_code",
                        "description": "Analyze code structure and quality",
                    },
                    {
                        "name": "Security Scan",
                        "agent": "SecurityAgent",
                        "tool": "scan_vulnerabilities",
                        "description": "Check for security issues",
                    },
                    {
                        "name": "Test Coverage",
                        "agent": "TestAgent",
                        "tool": "analyze_coverage",
                        "description": "Assess test coverage",
                    },
                    {
                        "name": "Generate Report",
                        "agent": "CodeAgent",
                        "tool": "generate_report",
                        "description": "Create comprehensive review report",
                    },
                ],
                estimated_duration="5-10 minutes",
                required_inputs=["code_repository", "branch_name"],
            ),
            
            WorkflowTemplate(
                id="api_development",
                name="API Development Workflow",
                description="Generate API endpoints, tests, and documentation",
                category=WorkflowCategory.SOFTWARE_DEV,
                agents=["CodeAgent", "TestAgent", "AnalysisAgent"],
                steps=[
                    {
                        "name": "Generate API Code",
                        "agent": "CodeAgent",
                        "tool": "generate_code",
                        "description": "Create API endpoint implementations",
                    },
                    {
                        "name": "Generate Tests",
                        "agent": "TestAgent",
                        "tool": "generate_tests",
                        "description": "Create API test suite",
                    },
                    {
                        "name": "Run Tests",
                        "agent": "TestAgent",
                        "tool": "run_integration_tests",
                        "description": "Execute API tests",
                    },
                    {
                        "name": "Generate Documentation",
                        "agent": "CodeAgent",
                        "tool": "generate_docs",
                        "description": "Create API documentation",
                    },
                ],
                estimated_duration="10-15 minutes",
                required_inputs=["api_spec", "framework"],
            ),

            # Data Analysis Templates
            WorkflowTemplate(
                id="data_pipeline_etl",
                name="ETL Pipeline Generator",
                description="Create complete ETL pipeline with testing",
                category=WorkflowCategory.DATA_ANALYSIS,
                agents=["CodeAgent", "AnalysisAgent", "TestAgent"],
                steps=[
                    {
                        "name": "Analyze Data Schema",
                        "agent": "AnalysisAgent",
                        "tool": "analyze_statistics",
                        "description": "Understand data structure",
                    },
                    {
                        "name": "Generate Extract Code",
                        "agent": "CodeAgent",
                        "tool": "generate_code",
                        "description": "Create data extraction logic",
                    },
                    {
                        "name": "Generate Transform Code",
                        "agent": "CodeAgent",
                        "tool": "generate_code",
                        "description": "Create transformation logic",
                    },
                    {
                        "name": "Generate Load Code",
                        "agent": "CodeAgent",
                        "tool": "generate_code",
                        "description": "Create data loading logic",
                    },
                    {
                        "name": "Generate Tests",
                        "agent": "TestAgent",
                        "tool": "generate_tests",
                        "description": "Create pipeline tests",
                    },
                ],
                estimated_duration="15-20 minutes",
                required_inputs=["source_type", "destination_type", "data_schema"],
            ),

            WorkflowTemplate(
                id="data_insights",
                name="Data Insights Report",
                description="Analyze data and generate insights with visualizations",
                category=WorkflowCategory.DATA_ANALYSIS,
                agents=["AnalysisAgent", "ResearchAgent"],
                steps=[
                    {
                        "name": "Statistical Analysis",
                        "agent": "AnalysisAgent",
                        "tool": "analyze_statistics",
                        "description": "Compute statistical metrics",
                    },
                    {
                        "name": "Pattern Detection",
                        "agent": "AnalysisAgent",
                        "tool": "detect_patterns",
                        "description": "Find trends and anomalies",
                    },
                    {
                        "name": "Generate Insights",
                        "agent": "AnalysisAgent",
                        "tool": "generate_insights",
                        "description": "Create actionable insights",
                    },
                    {
                        "name": "Create Visualizations",
                        "agent": "AnalysisAgent",
                        "tool": "create_visualizations",
                        "description": "Generate charts and graphs",
                    },
                ],
                estimated_duration="8-12 minutes",
                required_inputs=["data_source", "metrics"],
            ),

            # Research Templates
            WorkflowTemplate(
                id="market_research",
                name="Market Research Analysis",
                description="Comprehensive market research with competitive analysis",
                category=WorkflowCategory.RESEARCH,
                agents=["ResearchAgent", "AnalysisAgent"],
                steps=[
                    {
                        "name": "Gather Market Data",
                        "agent": "ResearchAgent",
                        "tool": "web_search",
                        "description": "Collect market information",
                    },
                    {
                        "name": "Competitor Analysis",
                        "agent": "ResearchAgent",
                        "tool": "extract_data",
                        "description": "Analyze competitors",
                    },
                    {
                        "name": "Synthesize Findings",
                        "agent": "ResearchAgent",
                        "tool": "synthesize",
                        "description": "Create comprehensive analysis",
                    },
                    {
                        "name": "Generate Insights",
                        "agent": "AnalysisAgent",
                        "tool": "generate_insights",
                        "description": "Extract actionable insights",
                    },
                ],
                estimated_duration="10-15 minutes",
                required_inputs=["market_segment", "competitors"],
            ),

            # Testing Templates
            WorkflowTemplate(
                id="test_automation_suite",
                name="Complete Test Suite Generator",
                description="Generate unit, integration, and E2E tests",
                category=WorkflowCategory.TESTING,
                agents=["TestAgent", "CodeAgent"],
                steps=[
                    {
                        "name": "Analyze Code",
                        "agent": "CodeAgent",
                        "tool": "analyze_code",
                        "description": "Understand code structure",
                    },
                    {
                        "name": "Generate Unit Tests",
                        "agent": "TestAgent",
                        "tool": "generate_tests",
                        "description": "Create unit tests",
                    },
                    {
                        "name": "Generate Integration Tests",
                        "agent": "TestAgent",
                        "tool": "generate_tests",
                        "description": "Create integration tests",
                    },
                    {
                        "name": "Generate E2E Tests",
                        "agent": "TestAgent",
                        "tool": "generate_tests",
                        "description": "Create end-to-end tests",
                    },
                    {
                        "name": "Run Test Suite",
                        "agent": "TestAgent",
                        "tool": "run_all_tests",
                        "description": "Execute complete test suite",
                    },
                ],
                estimated_duration="12-18 minutes",
                required_inputs=["code_path", "test_framework"],
            ),
        ]

        if category:
            return [t for t in all_templates if t.category == category]
        return all_templates

    @staticmethod
    def search_templates(query: str) -> List[WorkflowTemplate]:
        """Search templates by name or description."""
        query_lower = query.lower()
        all_templates = WorkflowTemplateLibrary.list_templates()
        
        return [
            t for t in all_templates
            if query_lower in t.name.lower() or query_lower in t.description.lower()
        ]

    @staticmethod
    def create_workflow_from_template(
        template_id: str,
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a workflow instance from template.

        Args:
            template_id: Template identifier
            inputs: Required input values

        Returns:
            Workflow configuration
        """
        template = WorkflowTemplateLibrary.get_template(template_id)
        
        # Validate inputs
        missing_inputs = [
            inp for inp in template.required_inputs
            if inp not in inputs
        ]
        if missing_inputs:
            raise ValueError(f"Missing required inputs: {missing_inputs}")

        # Create workflow configuration
        workflow = {
            "template_id": template.id,
            "name": template.name,
            "category": template.category.value,
            "agents": template.agents,
            "steps": template.steps,
            "inputs": inputs,
            "estimated_duration": template.estimated_duration,
        }

        return workflow

