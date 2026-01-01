.PHONY: lint format test clean check-keys

# Python files to lint
PYTHON_FILES = weather_risks.py risk_definitions.py src/multi_agent_system/**/*.py simple_example.py simple_web_interface.py tests/**/*.py

lint:
	pylint $(PYTHON_FILES)
	mypy $(PYTHON_FILES)

format:
	black $(PYTHON_FILES)

test:
	pytest

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +
	find . -type d -name "build" -exec rm -r {} +

# Check for required API keys (prints missing keys)
check-keys:
	@echo "Checking for required API keys..."
	@missing=0; \
	required_keys="NASA_EARTHDATA_TOKEN NOAA_API_KEY USGS_API_KEY FRED_API_KEY EPA_API_KEY GOOGLE_API_KEY OPENWEATHER_API_KEY DC_API_KEY OPENET_API_KEY QUICKSTATS_API_KEY"; \
	for key in $$required_keys; do \
	  if [ -z "$$($$SHELL -c 'echo $$'$$key)" ]; then \
	    echo "Missing: $$key"; missing=1; \
	  fi; \
	done; \
	if [ $$missing -eq 1 ]; then \
	  echo "Some required API keys are missing. See credentials_template.txt for details."; \
	  exit 1; \
	else \
	  echo "All required API keys are set."; \
	fi

# Run all checks
check: check-keys lint format test

# Note: Many tests and live data integrations require API keys. See credentials_template.txt for details.