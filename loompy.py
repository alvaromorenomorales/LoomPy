#!/usr/bin/env python3
"""
loompy.py

Wrapper script for the LoomPy JSON Translator.
This script invokes the main application logic from src.main.
"""

import sys
print(">>> LoomPy Translator: Initializing engine and loading modules...")
from src.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
