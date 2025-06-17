#!/usr/bin/env python3
"""
VroomSniffer CLI
---------------
Run this file with commands to interact with the scraper's JSON storage and notifications.

USAGE EXAMPLES:
===============

1. Run the scraper with a marketplace URL:
   python cli/main.py run "https://marketplace-url.com/search-cars"

2. List the latest scraped listings:
   python cli/main.py list

3. Search for specific cars in the listings:
   python cli/main.py search "bmw"

4. Send a listing via Telegram (use index from 'list' command):
   python cli/main.py send 3

For full documentation, see docs/cli_documentation.md
"""
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from project modules
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from .utils import get_services, load_saved_urls
from .commands import (
    list_listings,
    search_listings,
    send_listings_by_indexes,
    run_scraper_with_url_improved,
    run_scheduler
)
from .argparse_setup import setup_parser







def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    parser = setup_parser()
    args = parser.parse_args()
    
    # Initialize services
    services = get_services()
    
    # Handle commands
    if args.command == "list":
        list_listings(services, args.type, args.count)
    elif args.command == "search":
        search_listings(services, args.keyword)
    elif args.command == "send":
        send_listings_by_indexes(services, args.indexes)
    elif args.command == "version":
        print("🚗 VroomSniffer Car Scraper v1.0.0")
    elif args.command == "run":
        run_scraper_with_url_improved(services, args.urls, args.notify_new, args.notify_count)
    elif args.command == "schedule":
        # Load URLs - either from command line or saved_urls.json
        urls = []
        # If --use-saved flag is set or no URLs provided, load from saved_urls.json
        if args.use_saved or not args.urls:
            urls = load_saved_urls(services)
            if not urls:
                print("[!] No URLs available. Either provide URLs directly or ensure saved_urls.json is populated.")
                return 1
        else:
            urls = args.urls
        
        # Run the scheduler with the URLs
        run_scheduler(
            services=services,
            urls=urls,
            interval=args.interval,
            runs=args.runs,
            random_selection=args.random,
            notify_new=args.notify_new,
            notify_count=args.notify_count
        )
    else:
        parser.print_help()
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
