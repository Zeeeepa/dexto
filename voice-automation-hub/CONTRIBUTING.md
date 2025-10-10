# Contributing to Voice Automation Hub

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/dexto.git
   cd dexto/voice-automation-hub
   ```

2. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   pip install pytest pytest-asyncio pytest-cov ruff mypy

   # Frontend
   cd ../frontend
   npm install
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Add your OPENAI_API_KEY to .env
   ```

4. **Run Tests**
   ```bash
   # Backend tests
   cd backend
   pytest tests/ -v

   # Frontend tests
   cd ../frontend
   npm test
   ```

## 📋 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

Follow our coding standards (see below).

### 3. Test Your Changes

```bash
# Run tests
pytest tests/ -v

# Check code quality
ruff check .
mypy .
```

### 4. Commit Changes

Use conventional commit messages:

```bash
git commit -m "feat: add new agent for X"
git commit -m "fix: resolve issue with Y"
git commit -m "docs: update README for Z"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Formatting
- `chore`: Maintenance

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 🎯 What to Contribute

### High Priority

- **New Agents**: Specialized agents for specific domains
- **MCP Tools**: Integration with external services
- **Widgets**: Custom visualization components
- **Example Workflows**: Real-world use case demonstrations
- **Documentation**: Guides, tutorials, API docs
- **Tests**: Increase coverage, add edge cases

### Ideas for Contributions

#### New Agents
- **DatabaseAgent**: SQL query generation and analysis
- **SecurityAgent**: Security scanning and vulnerability detection
- **DeploymentAgent**: CI/CD pipeline automation
- **DocumentationAgent**: Auto-generate documentation
- **MonitoringAgent**: System monitoring and alerting

#### MCP Tools
- **GitTools**: Repository operations
- **CloudTools**: AWS/Azure/GCP integration
- **DatabaseTools**: Direct database operations
- **APITools**: REST API testing and interaction
- **SlackTools**: Team communication integration

#### Widgets
- **MetricsWidget**: Real-time performance metrics
- **LogWidget**: Streaming log visualization
- **AlertWidget**: Error and warning notifications
- **TimelineWidget**: Workflow execution timeline

#### Example Workflows
- API testing automation
- Database migration generation
- Documentation generation
- Performance benchmarking
- Security audit workflows

## 📐 Coding Standards

### Python (Backend)

**Style Guide**: PEP 8

```python
# Good
async def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process input data and return results.
    
    Args:
        data: Input data dictionary
        
    Returns:
        Processed results
    """
    result = {"status": "success"}
    return result

# Use type hints
# Add docstrings
# Keep functions focused
# Handle errors explicitly
```

**Tools**:
- `ruff`: Linting and formatting
- `mypy`: Type checking
- `pytest`: Testing

### TypeScript (Frontend)

**Style Guide**: Standard TypeScript conventions

```typescript
// Good
interface WorkflowProps {
  id: string;
  status: WorkflowStatus;
}

const WorkflowCard: React.FC<WorkflowProps> = ({ id, status }) => {
  return (
    <div className="workflow-card">
      {/* component content */}
    </div>
  );
};

// Use interfaces for props
// Functional components with React.FC
// Descriptive naming
```

### Testing

**Coverage Target**: 80%+

```python
# Backend test example
import pytest

async def test_agent_execution():
    """Test agent executes task successfully."""
    agent = MyAgent(client)
    result = await agent.execute("test task")
    
    assert result["status"] == "success"
    assert "data" in result
```

```typescript
// Frontend test example
import { render, screen } from '@testing-library/react';

test('renders workflow card', () => {
  render(<WorkflowCard id="123" status="running" />);
  expect(screen.getByText('123')).toBeInTheDocument();
});
```

## 📝 Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Explain complex logic with inline comments
- Update README for new features

### API Documentation

- Document all endpoints
- Provide request/response examples
- List all parameters and types

### User Documentation

- Create guides for new features
- Add examples and screenshots
- Keep docs up-to-date

## 🐛 Bug Reports

### Good Bug Report Includes:

1. **Clear Title**: Describe the issue
2. **Steps to Reproduce**: Exact steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python/Node versions
6. **Logs**: Relevant error messages

Template:

```markdown
### Bug Description
Brief description of the bug

### Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Environment
- OS: Windows 11
- Python: 3.11.5
- Node: 20.10.0

### Logs
```
Error message here
```
```

## 💡 Feature Requests

### Good Feature Request Includes:

1. **Use Case**: Why is this needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other options considered
4. **Additional Context**: Examples, mockups

## 🔍 Code Review

### Review Checklist

- [ ] Code follows style guide
- [ ] Tests are included
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Commits are clear and atomic
- [ ] No unnecessary dependencies

### Review Process

1. Submit PR
2. Automated checks run
3. Maintainer reviews
4. Address feedback
5. Merge when approved

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📧 Questions?

- **Discord**: [Join our community](https://discord.gg/...)
- **GitHub Discussions**: [Ask questions](https://github.com/Zeeeepa/dexto/discussions)
- **Email**: support@example.com

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Voice Automation Hub! 🎉

