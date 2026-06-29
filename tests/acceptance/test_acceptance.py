"""
pytest-bdd test loader for uFawkesObs acceptance tests.

Step definitions are loaded by conftest.py. This module discovers
all .feature files and registers them as pytest test functions.
"""

from __future__ import annotations

from pathlib import Path

import pytest_bdd

FEATURES_DIR = Path(__file__).parent / "features"

for feature_path in sorted(FEATURES_DIR.glob("*.feature")):
    pytest_bdd.scenarios(str(feature_path))
