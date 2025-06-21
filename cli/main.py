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

from cli.utils import get_services, load_saved_urls, print_info, print_error, print_success, print_warning
from colorama import Fore, Back, Style
from cli.commands import (
    list_listings,
    search_listings,
    send_listings_by_indexes,
    run_scraper_with_url_improved,
    run_scheduler
)
from cli.argparse_setup import setup_parser
from cli.diagnostics import display_ip_tracking


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    # Print a welcome banner
    print(f"\n{Back.BLUE}{Fore.WHITE} 🚗 VroomSniffer CLI 🚗 {Style.RESET_ALL}")
    
    try:
        parser = setup_parser()
        args = parser.parse_args()
        
        # Initialize services - pass proxy settings if needed
        use_proxy = args.use_proxy if hasattr(args, "use_proxy") else False
        proxy_type = args.proxy_type if hasattr(args, "proxy_type") else None
        
        services = get_services(use_proxy=use_proxy, proxy_type=proxy_type)
        
        if use_proxy and proxy_type:
            print_info(f"Using proxy type: {proxy_type}")
        
        # Handle commands
        if args.command == "list":
            list_listings(services, args.type, args.count)
        elif args.command == "search":
            search_listings(services, args.keyword)
        elif args.command == "send":
            send_listings_by_indexes(services, args.indexes)
        elif args.command == "version":
            print(f"\n{Fore.CYAN}🚗 VroomSniffer Car Scraper v1.0.0{Style.RESET_ALL}\n")
        elif args.command == "run":
            success = run_scraper_with_url_improved(services, args.urls, args.notify_new, args.notify_count)
            if not success:
                return 1
        elif args.command == "schedule":
            # Load URLs - either from command line or saved_urls.json
            urls = []
            if args.use_saved or not args.urls:
                urls = load_saved_urls(services)
                if not urls:
                    print_error("No URLs available. Either provide URLs directly or ensure saved_urls.json is populated.")
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
        elif args.command == "diagnostics":
            if args.show_ip_tracking:
                display_ip_tracking()
            else:
                print_warning("No diagnostic option specified. Use --show-ip-tracking to display IP tracking information.")
        else:
            # No command provided, show help with a nice banner
            print(f"\n{Fore.CYAN}Command Reference:{Style.RESET_ALL}")
            parser.print_help()
            
        # End with a success message
        if args.command and args.command not in ["version", "help"]:
            print(f"\n{Fore.GREEN}✓ Operation completed successfully{Style.RESET_ALL}\n")
        
        return 0
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Process interrupted by user.{Style.RESET_ALL}")
        return 1
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
