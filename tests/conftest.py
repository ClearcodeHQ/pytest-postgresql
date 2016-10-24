"""Tests main conftest file."""
import sys
import warnings

major, minor = sys.version_info[:2]

if not (major >= 3 and minor >= 5):
    warnings.simplefilter("error", category=DeprecationWarning)
