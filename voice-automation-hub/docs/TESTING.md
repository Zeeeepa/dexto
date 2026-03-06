# Testing Guide

Complete testing documentation for Voice Automation Hub.

## Table of Contents
- [Test Infrastructure](#test-infrastructure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [CI/CD Integration](#cicd-integration)

## Test Infrastructure

### Test Framework
- **pytest**: Main testing framework
- **pytest-asyncio**: Async test support
- **httpx**: HTTP client for API testing
- **unittest.mock**: Mocking utilities

### Test Structure
```
backend/tests/
├── conftest.py           # Fixtures and configuration
├── test_agents.py        # Agent tests
├── test_api.py          # API endpoint tests
├── test_memory_store.py # Memory store tests
└── test_tools.py        # Tool tests (to be added)
```

## Running Tests

### Run All Tests
```bash
cd backend
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_agents.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_agents.py::TestCodeAgent -v
```

### Run Specific Test
```bash
pytest tests/test_agents.py::TestCodeAgent::test_code_generation_tool -v
```

### Run with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
# View coverage report: open htmlcov/index.html
```

### Run Tests in Parallel
```bash
pytest tests/ -n auto  # Requires pytest-xdist
```

## Writing Tests

### Basic Test Structure
```python
import pytest


class TestMyFeature:
    """Tests for my feature."""

    def test_something(self):
        """Test description."""
        # Arrange
        expected = "result"
        
        # Act
        actual = my_function()
        
        # Assert
        assert actual == expected
```

### Async Tests
```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await my_async_function()
    assert result is not None
```

### Using Fixtures
```python
def test_with_fixture(mock_openai_client):
    """Test using fixture from conftest.py."""
    agent = MyAgent(mock_openai_client)
    assert agent.client == mock_openai_client
```

### API Tests
```python
@pytest.mark.asyncio
async def test_api_endpoint(test_client):
    """Test API endpoint."""
    response = await test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Mocking
```python
from unittest.mock import Mock, AsyncMock, patch

def test_with_mock():
    """Test with mock."""
    mock_client = Mock()
    mock_client.method.return_value = "mocked"
    
    result = function_using_client(mock_client)
    assert result == "mocked"
```

### Parametrized Tests
```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    ("test3", "result3"),
])
def test_multiple_cases(input, expected):
    """Test multiple cases."""
    assert process(input) == expected
```

## Test Coverage

### Coverage Goals
- **Overall**: >80% coverage
- **Critical paths**: >90% coverage
- **New code**: 100% coverage

### Viewing Coverage Report
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

Shows lines not covered by tests.

### Coverage Configuration
Edit `backend/.coveragerc`:
```ini
[run]
source = app
omit = 
    */tests/*
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Best Practices

### Test Naming
- Use descriptive names: `test_agent_handles_error_gracefully`
- Follow pattern: `test_<what>_<condition>_<expected>`

### Test Organization
- One test class per component
- Related tests grouped together
- Clear docstrings for each test

### Test Data
- Use fixtures for reusable test data
- Keep test data simple and focused
- Avoid external dependencies

### Assertions
- One logical assertion per test
- Use specific assertions: `assert x == 5`, not `assert x`
- Add assertion messages for clarity

### Mocking
- Mock external dependencies
- Don't mock the code being tested
- Use realistic mock data

### Test Independence
- Each test should be independent
- Tests should not rely on execution order
- Clean up after each test

## CI/CD Integration

### GitHub Actions
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/ -v --cov=app
```

### Pre-commit Hook
Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
cd backend
pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

## Common Testing Patterns

### Testing Agents
```python
@pytest.mark.asyncio
async def test_agent_tool_execution(mock_openai_client):
    """Test agent tool execution."""
    agent = MyAgent(mock_openai_client)
    agent_obj = agent.get_agent()
    
    # Verify tools exist
    tool_names = [tool.name for tool in agent_obj.tools]
    assert "my_tool" in tool_names
```

### Testing API Endpoints
```python
@pytest.mark.asyncio
async def test_create_workflow(test_client):
    """Test workflow creation."""
    response = await test_client.post(
        "/api/workflows",
        json={"task": "Test task"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["task"] == "Test task"
```

### Testing Error Handling
```python
def test_error_handling():
    """Test error handling."""
    with pytest.raises(ValueError, match="Invalid input"):
        function_that_raises("invalid")
```

### Testing Async Retries
```python
@pytest.mark.asyncio
async def test_retry_on_failure():
    """Test retry behavior."""
    mock = AsyncMock(side_effect=[
        Exception("First fail"),
        Exception("Second fail"),
        "Success"
    ])
    
    result = await retry_function(mock)
    assert result == "Success"
    assert mock.call_count == 3
```

## Troubleshooting

### Tests Timing Out
- Increase timeout: `@pytest.mark.timeout(10)`
- Check for deadlocks in async code
- Mock slow external calls

### Import Errors
- Ensure PYTHONPATH includes backend directory
- Check for circular imports
- Verify all dependencies installed

### Async Test Issues
- Always use `@pytest.mark.asyncio`
- Don't mix sync and async code
- Use `AsyncMock` for async functions

### Flaky Tests
- Identify non-deterministic behavior
- Add proper cleanup in fixtures
- Use fixed test data, not random

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Mock Library](https://docs.python.org/3/library/unittest.mock.html)

