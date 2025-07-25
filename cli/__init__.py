"""
CLI Package for VroomSniffer Car Scraper
---------------------------------------
This package contains the command-line interface for the VroomSniffer car scraper project.
The CLI is organized into several modules:

- main.py: Entry point for the CLI
- commands.py: Implementation of all command functions
- argparse_setup.py: Command-line argument parsing setup
- utils.py: Utility functions and service initialization

Core scraper utilities are located in scraper/utils/ package:
- anti_detection.py: Browser stealth and fingerprinting protection
- bandwidth_tracker.py: Request monitoring and bandwidth optimization  
- resource_blocker.py: Request filtering and resource blocking
- page_navigator.py: Page navigation with detection analysis
- listings_finder.py: Robust listing discovery with fallbacks
- constants.py: Configuration constants and blocking rules

Usage:
    python -m cli.main <command> [options]
"""

from .main import main
