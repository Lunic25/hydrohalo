# conftest.py
import sys
import os

# Make the repo root importable so 'from app.x import y' works in all tests
sys.path.insert(0, os.path.dirname(__file__))
