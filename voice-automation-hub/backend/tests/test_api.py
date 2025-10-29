"""Tests for API endpoints."""

import pytest
from httpx import AsyncClient


class TestRootEndpoint:
    """Tests for root endpoint."""

    @pytest.mark.asyncio
    async def test_root_returns_service_info(self, test_client):
        """Test root endpoint returns service information."""
        response = await test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert data["status"] == "running"


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, test_client):
        """Test health check returns healthy status."""
        response = await test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestWorkflowEndpoints:
    """Tests for workflow API endpoints."""

    @pytest.mark.asyncio
    async def test_list_workflows(self, test_client):
        """Test listing workflows."""
        response = await test_client.get("/api/workflows")
        
        assert response.status_code == 200
        data = response.json()
        assert "workflows" in data
        assert "count" in data

    @pytest.mark.asyncio
    async def test_create_workflow(self, test_client):
        """Test creating workflow."""
        response = await test_client.post(
            "/api/workflows",
            json={"task": "Test task"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["task"] == "Test task"
        assert data["status"] == "created"

    @pytest.mark.asyncio
    async def test_create_workflow_without_task(self, test_client):
        """Test creating workflow without task fails."""
        response = await test_client.post(
            "/api/workflows",
            json={}
        )
        
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_get_workflow(self, test_client):
        """Test getting workflow by ID."""
        # Create workflow first
        create_response = await test_client.post(
            "/api/workflows",
            json={"task": "Test task"}
        )
        workflow_id = create_response.json()["id"]
        
        # Get workflow
        response = await test_client.get(f"/api/workflows/{workflow_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == workflow_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_workflow(self, test_client):
        """Test getting non-existent workflow returns 404."""
        response = await test_client.get("/api/workflows/nonexistent")
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_workflow(self, test_client):
        """Test deleting workflow."""
        # Create workflow first
        create_response = await test_client.post(
            "/api/workflows",
            json={"task": "Test task"}
        )
        workflow_id = create_response.json()["id"]
        
        # Delete workflow
        response = await test_client.delete(f"/api/workflows/{workflow_id}")
        
        assert response.status_code == 200
        
        # Verify deleted
        get_response = await test_client.get(f"/api/workflows/{workflow_id}")
        assert get_response.status_code == 404

