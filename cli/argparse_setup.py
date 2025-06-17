"""
CLI Argument Parser Module
-------------------------
Sets up argument parsing for the VroomSniffer CLI.
"""
import argparse
from typing import Dict, Any, Callable


def setup_parser() -> argparse.ArgumentParser:
    """
    Set up and return the argument parser for the CLI.
    
    Returns:
        argparse.ArgumentParser: Configured parser
    """
    parser = argparse.ArgumentParser(
        description="VroomSniffer Car Scraper CLI - Interact with JSON-based listing data",
        epilog="""
EXAMPLES:
  %(prog)s run "https://www.example-marketplace.com/s-autos/bmw/k0c216"
  %(prog)s list
  %(prog)s search "bmw x5"  
  %(prog)s send 3

For more advanced features, use the Streamlit UI:
  streamlit run ui/streamlit_app.py
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser(
        "list", 
        help="List latest scraped listings from JSON",
        description="Display the most recent car listings from the last scraping run. Shows first 10 listings with title, price, and location."
    )
    list_parser.add_argument(
        "--type",
        choices=["latest", "all", "new"],
        default="all",
        help="Type of listings to display: 'all' (default) for all stored listings, 'latest' for most recent run, 'new' for new findings only"
    )
    list_parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of listings to display (default: 10, use 0 for all)"
    )

    # Search command  
    search_parser = subparsers.add_parser(
        "search", 
        help="Search listings by keyword",
        description="Search through the latest listings for cars matching a keyword in the title."
    )
    search_parser.add_argument(
        "keyword", 
        type=str, 
        help="Keyword to search for in listing titles (e.g., 'bmw', 'automatic', 'diesel')"
    )
    
    # Send command
    send_parser = subparsers.add_parser(
        "send", 
        help="Send one or more listings via Telegram",
        description="Send specific car listings via Telegram by their indexes. Use 'list' command first to see available indices."
    )
    send_parser.add_argument(
        "indexes", 
        type=int, 
        nargs='+',
        help="One or more indexes of listings to send (use 'list' command to see indices, starting from 1)"
    )

    # Notify command removed - we now focus on individual notifications
    
    # Run command
    run_parser = subparsers.add_parser(
        "run", 
        help="Run the scraper engine with one or more marketplace URLs",
        description="Execute the car scraper with one or more marketplace search URLs. Results will be saved to storage/latest_results.json"
    )
    run_parser.add_argument(
        "urls", 
        type=str, 
        nargs='+',
        help="One or more marketplace search URLs (e.g., 'https://www.example-marketplace.com/s-autos/bmw/k0c216')"
    )
    run_parser.add_argument(
        "--notify-new", 
        action="store_true", 
        help="Send Telegram notifications for new listings found after scraping"
    )
    run_parser.add_argument(
        "--notify-count", 
        type=int, 
        default=-1,
        help="Controls notification behavior: -1 to send all new listings (default) or a positive number to limit notifications to that many listings"
    )
    
    # Version command
    version_parser = subparsers.add_parser(
        "version", 
        help="Show version information",
        description="Display version and system information for the VroomSniffer car scraper."
    )

    # Scheduler commands
    schedule_parser = subparsers.add_parser(
        "schedule",
        help="Schedule periodic scraping runs",
        description="Set up automatic scraping at fixed intervals"
    )
    schedule_parser.add_argument(
        "urls",
        type=str,
        nargs="*",
        help="One or more marketplace search URLs to scrape periodically (omit to use saved URLs)"
    )
    schedule_parser.add_argument(
        "--use-saved",
        action="store_true",
        help="Use URLs from saved_urls.json instead of providing URLs directly"
    )
    schedule_parser.add_argument(
        "--random",
        action="store_true",
        help="Select URLs randomly instead of sequentially (only applies with multiple URLs)"
    )
    schedule_parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Interval between scraping runs in seconds (default: 60)"
    )
    schedule_parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Maximum number of scraping runs to perform (default: 5, use 0 for unlimited runs until stopped)"
    )
    schedule_parser.add_argument(
        "--notify-new",
        action="store_true",
        help="Send notifications for new listings found in each run"
    )
    schedule_parser.add_argument(
        "--notify-count", 
        type=int, 
        default=-1,
        help="Number of new listings to send notifications for (default: -1 to send all, or a positive number to limit notifications to that many listings)"
    )
    
    return parser
