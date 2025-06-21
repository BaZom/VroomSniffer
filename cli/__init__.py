"""
CLI Package for VroomSniffer Car Scraper
---------------------------------------
This package contains the command-line interface for the VroomSniffer car scraper project.
The CLI is organized into several modules:

- main.py: Entry point for the CLI
- commands.py: Implementation of all command functions
- argparse_setup.py: Command-line argument parsing setup
- utils.py: Utility functions and service initialization

Usage:
    python -m cli.main <command> [options]
"""

from .main import main
