# Test Suite Documentation

This document provides comprehensive instructions for running the test suite for the Multi-Agent Climate Risk Analysis System.

## Prerequisites

Before running tests, ensure you have:

1. **Python Environment**: Python 3.8+ with virtual environment activated
2. **Dependencies**: All requirements installed via `pip install -r requirements.txt`
3. **Database**: SQLite database will be created automatically for tests

## Quick Start

### Basic Test Run
```bash
# From project root directory
PYTHONPATH=src pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Run only unit tests
PYTHONPATH=src pytest tests/ -v -m "unit"

# Run only integration tests
PYTHONPATH=src pytest tests/ -v -m "integration"

# Run only performance tests
PYTHONPATH=src pytest tests/ -v -m "performance"

# Run only end-to-end tests
PYTHONPATH=src pytest tests/ -v -m "e2e"
```

### Run Specific Test Files
```bash
# Test agents and team functionality
PYTHONPATH=src pytest tests/test_agents_and_team.py -v

# Test A2A protocol and artifacts
PYTHONPATH=src pytest tests/test_a2a_and_artifacts.py -v

# Test data management and utilities
PYTHONPATH=src pytest tests/test_data_and_utils.py -v

# Test integration and observability
PYTHONPATH=src pytest tests/test_integration_and_observability.py -v
```

## Test Structure

The test suite is organized into four main files:

### 1. `test_agents_and_team.py`
- **Purpose**: Tests agent functionality, team coordination, and agent communication
- **Coverage**: 
  - Individual agent behavior and tools
  - Agent team management
  - Agent communication protocols
  - Agent card functionality
  - Session management

### 2. `test_a2a_and_artifacts.py`
- **Purpose**: Tests A2A protocol implementation and artifact management
- **Coverage**:
  - A2A message structure and routing
  - Artifact creation, storage, and retrieval
  - Task management
  - Content handlers
  - Multipart message handling

### 3. `test_data_and_utils.py`
- **Purpose**: Tests data sources, utilities, and business logic
- **Coverage**:
  - Weather data integration
  - Nature-based solutions data
  - Risk analysis algorithms
  - Utility functions
  - Data validation

### 4. `test_integration_and_observability.py`
- **Purpose**: Tests system integration and monitoring capabilities
- **Coverage**:
  - End-to-end workflows
  - Performance monitoring
  - Error handling and recovery
  - Security features
  - Observability patterns

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Test individual components in isolation
- Fast execution, no external dependencies
- Use mocked objects for external services

### Integration Tests (`@pytest.mark.integration`)
- Test component interactions
- May use real database connections
- Test API endpoints and workflows

### Performance Tests (`@pytest.mark.performance`)
- Test system performance under load
- Measure response times and resource usage
- Stress test scenarios

### End-to-End Tests (`@pytest.mark.e2e`)
- Test complete user workflows
- Full system integration
- Real data and external services

## Advanced Test Options

### Parallel Execution
```bash
# Run tests in parallel (requires pytest-xdist)
PYTHONPATH=src pytest tests/ -n auto -v
```

### Coverage Report
```bash
# Generate coverage report
PYTHONPATH=src pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

### Debug Mode
```bash
# Run with debug output
PYTHONPATH=src pytest tests/ -v -s --tb=long
```

### Specific Test Function
```bash
# Run a specific test function
PYTHONPATH=src pytest tests/test_agents_and_team.py::test_agent_creation -v
```

### Test with Custom Configuration
```bash
# Run with custom pytest configuration
PYTHONPATH=src pytest tests/ -v --config=test_config.ini
```

## Environment Variables

The following environment variables can be set for testing:

```bash
# Set test environment
export TEST_ENV=test

# Set database path for tests
export TEST_DB_PATH=test_artifacts.db

# Set log level for tests
export LOG_LEVEL=DEBUG

# Set API keys for external services (if needed)
export WEATHER_API_KEY=your_test_key
export GOOGLE_API_KEY=your_test_key
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError: No module named 'src'`
**Solution**: Always run tests with `PYTHONPATH=src`

#### 2. Database Lock Errors
**Problem**: SQLite database is locked
**Solution**: Ensure no other processes are using the test database
```bash
# Clean up test artifacts
rm -f test_artifacts.db
```

#### 3. Permission Errors
**Problem**: Cannot create test files
**Solution**: Check file permissions and ensure write access to test directory

#### 4. Timeout Errors
**Problem**: Tests timing out
**Solution**: Increase timeout or check for hanging processes
```bash
# Run with increased timeout
PYTHONPATH=src pytest tests/ --timeout=300
```

### Debug Commands

```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check installed packages
pip list | grep pytest

# Check test discovery
PYTHONPATH=src pytest --collect-only
```

## Test Data

### Sample Data Files
- `src/multi_agent_system/data/nature_based_solutions.json` - NBS data for testing
- Test fixtures in `conftest.py` - Reusable test objects

### Database Setup
- Tests use SQLite database: `test_artifacts.db`
- Database is created automatically during test execution
- Cleanup happens automatically after tests

## Continuous Integration

For CI/CD pipelines, use:

```yaml
# Example GitHub Actions step
- name: Run Tests
  run: |
    PYTHONPATH=src pytest tests/ -v --cov=src --cov-report=xml
  env:
    TEST_ENV: ci
```

## Performance Benchmarks

Expected test execution times:
- Unit tests: < 30 seconds
- Integration tests: < 2 minutes
- Performance tests: < 5 minutes
- Full test suite: < 10 minutes

## Contributing

When adding new tests:

1. **Follow naming conventions**: `test_<functionality>_<scenario>`
2. **Use appropriate markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
3. **Add to correct file**: Place tests in the appropriate consolidated test file
4. **Update this README**: Document any new test patterns or requirements

## Support

For test-related issues:
1. Check this README first
2. Review test logs and error messages
3. Check pytest documentation: https://docs.pytest.org/
4. Review project documentation in `docs/` directory 