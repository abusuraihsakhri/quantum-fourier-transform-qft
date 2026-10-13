"""Compatibility entry point for the QFT command-line interface.

The supported QFT commands live in the repository's top-level cli module.
"""
import sys
from cli import main

if __name__ == "__main__":
    sys.exit(main())
