"""Run the deterministic Role 2 contract and regression tests."""

import os
import sys

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)


if __name__ == "__main__":
    sys.exit(pytest.main([os.path.join(BASE_DIR, "tests", "test_suite.py"), "-q"]))
