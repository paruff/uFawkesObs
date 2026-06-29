"""
pytest-bdd test runner for Gherkin acceptance features.

This module collects all .feature files from the features/ directory
and binds them to their step definitions. Running pytest on this file
executes all Gherkin scenarios as pytest tests.

Usage:
    # Run all acceptance tests (offline only — fast):
    pytest tests/acceptance/test_acceptance.py -m offline -v

    # Run acceptance tests for a specific feature:
    pytest tests/acceptance/test_acceptance.py -k "core_substrate" -v

    # Run all acceptance tests:
    pytest tests/acceptance/test_acceptance.py -v
"""

from pathlib import Path
from pytest_bdd import scenarios


# Point pytest-bdd to the features directory
FEATURES_DIR = Path(__file__).parent / "features"

# Auto-discover all .feature files and register them as pytest scenarios
# Each .feature file's scenarios become individual pytest test functions
scenarios(str(FEATURES_DIR))


# Override: pytest-bdd's scenarios() auto-creates test functions, but
# we need to ensure the conftest fixtures and steps are collected.
# pytest-bdd discovers steps from:
#   1. conftest.py files (our shared steps are in conftest.py)
#   2. Python files in steps/ directory
# Both are automatically discovered by pytest's collection mechanism.
