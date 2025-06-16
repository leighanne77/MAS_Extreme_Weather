# Climate Risk Analysis System - Test Suite

This document provides instructions for running and maintaining the test suite for the Climate Risk Analysis System.

## Prerequisites

Before running the tests, ensure you have the following:

### Virtual Environment (Required)
```bash
# Create virtual environment if not already created
python -m venv venv

# Activate virtual environment
# On Unix/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Verify activation (should show path to venv)
which python  # Unix/macOS
# where python  # Windows
```

### Required Packages
Install the required packages in your virtual environment:
```bash
# Ensure virtual environment is activated
pip install pytest pytest-asyncio pytest-cov
pip install -e .  # Install the project in development mode
```

### System Requirements
- Python 3.8 or higher
- pip (Python package manager)
- pytest
- pytest-asyncio
- pytest-cov (optional, for coverage reports)

## Test Structure

The test suite is organized into the following files:

1. `tests/test_agent_tools.py`
   - Tests for agent tools functionality
   - Cache management
   - Error handling
   - Concurrency limits
   - Tool execution

2. `tests/test_session_manager.py`
   - Tests for session management
   - Session creation and retrieval
   - Agent state management
   - Shared data management
   - Session cleanup

3. `tests/test_risk_definitions.py`
   - Tests for risk definitions
   - Risk type and level enums
   - Threshold validation
   - Risk definition validation
   - Risk level determination
   - Consensus threshold calculation

4. `tests/test_app.py`
   - Tests for FastAPI application
   - Analysis endpoint
   - Input validation
   - Concurrent request handling

## Running Tests

### Before Running Tests
1. **Ensure virtual environment is activated**
```bash
# Verify virtual environment is active
which python  # Should show path to venv
# where python  # Windows
```

2. **Clear any existing cache**
```bash
rm -rf .pytest_cache
```

3. **Ensure no other instances are running**
```bash
# Check for running processes
ps aux | grep python  # Unix/macOS
# tasklist | findstr python  # Windows
```

### Run All Tests
To run the entire test suite:
```bash
python -m pytest tests/ -v
```

### Run Specific Test Files
To run a specific test file:
```bash
python -m pytest tests/test_agent_tools.py -v
python -m pytest tests/test_session_manager.py -v
python -m pytest tests/test_risk_definitions.py -v
python -m pytest tests/test_app.py -v
```

### Run Tests with Coverage Report
To generate a coverage report:
```bash
python -m pytest tests/ --cov=src.multi_agent_system --cov-report=term-missing
```

### Run Tests in Parallel
To run tests in parallel (faster execution):
```bash
python -m pytest tests/ -v -n auto
```

## Test Categories

### Unit Tests
- Test individual components in isolation
- Use mocks and fixtures to simulate dependencies
- Focus on specific functionality

### Integration Tests
- Test interaction between components
- Verify data flow and state management
- Test API endpoints and responses

### Async Tests
- Tests marked with `@pytest.mark.asyncio`
- Test asynchronous functionality
- Handle concurrent operations

## Best Practices

1. **Before Running Tests**
   - Clear any existing cache
   - Ensure no other instances of the application are running
   - Check for any pending database migrations

2. **Writing New Tests**
   - Follow the existing test structure
   - Use descriptive test names
   - Include docstrings explaining test purpose
   - Use appropriate fixtures and mocks

3. **Test Maintenance**
   - Keep tests up to date with code changes
   - Remove obsolete tests
   - Update test data as needed

## Common Issues and Solutions

1. **Virtual Environment Issues**
   - If "command not found: python", ensure virtual environment is activated
   - If packages are not found, verify virtual environment activation
   - If you get permission errors, check virtual environment ownership

2. **Test Failures**
   - Check for missing dependencies
   - Verify environment variables
   - Check for conflicting processes

3. **Async Test Issues**
   - Ensure proper use of `@pytest.mark.asyncio`
   - Check for proper async/await usage
   - Verify event loop handling

4. **Mock Issues**
   - Verify mock setup
   - Check mock return values
   - Ensure proper cleanup

## Continuous Integration

The test suite is designed to run in CI environments. Key points:
- Tests run automatically on pull requests
- Coverage reports are generated
- Test results are reported in CI logs

## Adding New Tests

1. Create a new test file in the `tests/` directory
2. Follow the existing test structure
3. Add appropriate fixtures and mocks
4. Include comprehensive docstrings
5. Update this document if necessary

## Test Data

Test data is managed in the following ways:
- Fixtures for common test data
- Mock objects for external dependencies
- In-memory databases for persistence tests

## Performance Considerations

- Use appropriate test markers
- Implement test isolation
- Clean up resources after tests
- Use efficient mocking strategies

## Support

For issues with the test suite:
1. Check the test logs
2. Review the test documentation
3. Consult the project documentation
4. Contact the development team 