"""
CLI Argument Parser Module
-------------------------
Sets up argument parsing for the VroomSniffer CLI.
"""
import argparse
from typing import Dict, Any, Callable
from colorama import Fore, Style, Back, init

# Initialize colorama
init(autoreset=True)


class ColorHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom argparse formatter that adds color to the help output"""
    
    def _format_action(self, action):
        # Get the original format
        result = super()._format_action(action)
        
        # Add color to the first line (command name and help)
        lines = result.split('\n')
        if len(lines) > 0:
            # Find the position of help text in the line
            cmd_line = lines[0]
            help_pos = cmd_line.rfind('  ')
            
            if help_pos > 0 and help_pos < len(cmd_line) - 2:
                # Colorize the command part
                command_part = cmd_line[:help_pos]
                help_part = cmd_line[help_pos:]
                lines[0] = f"{Fore.CYAN}{command_part}{Style.RESET_ALL}{Fore.GREEN}{help_part}{Style.RESET_ALL}"
        
        # Join the lines back
        return '\n'.join(lines)
    
    def _format_usage(self, usage, actions, groups, prefix):
        result = super()._format_usage(usage, actions, groups, prefix)
        
        # Colorize the usage header
        return result.replace('usage:', f'{Fore.YELLOW}usage:{Style.RESET_ALL}')

    def add_text(self, text):
        if text:
            # Colorize section headings in text
            if text.strip().endswith(':'):
                text = f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
            elif text.strip() == 'EXAMPLES:':
                text = f"\n{Back.BLUE}{Fore.WHITE} {text} {Style.RESET_ALL}"
                
        return super().add_text(text)


def setup_parser() -> argparse.ArgumentParser:
    """
    Set up and return the argument parser for the CLI.
    
    Returns:
        argparse.ArgumentParser: Configured parser
    """
    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}VroomSniffer Car Scraper CLI - Interact with JSON-based listing data{Style.RESET_ALL}",
        epilog=f"""
{Back.BLUE}{Fore.WHITE} EXAMPLES: {Style.RESET_ALL}
  %(prog)s run "https://www.example-marketplace.com/s-autos/bmw/k0c216"
  %(prog)s list
  %(prog)s search "bmw x5"  
  %(prog)s send 3

{Fore.GREEN}For more advanced features, use the Streamlit UI:{Style.RESET_ALL}
  streamlit run ui/streamlit_app.py
        """,
        formatter_class=ColorHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser(
        "list", 
        help="List latest scraped listings from JSON",
        description=f"{Fore.CYAN}Display the most recent car listings from the last scraping run. Shows first 10 listings with title, price, and location.{Style.RESET_ALL}",
        formatter_class=ColorHelpFormatter
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
        description=f"{Fore.CYAN}Search through the latest listings for cars matching a keyword in the title.{Style.RESET_ALL}",
        formatter_class=ColorHelpFormatter
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
        description=f"{Fore.CYAN}Send specific car listings via Telegram by their indexes. Use 'list' command first to see available indices.{Style.RESET_ALL}",
        formatter_class=ColorHelpFormatter
    )
    send_parser.add_argument(
        "indexes", 
        type=int, 
        nargs='+',
        help="One or more indexes of listings to send (use 'list' command to see indices, starting from 1)"
    )

    # Run command
    run_parser = subparsers.add_parser(
        "run", 
        help="Run the scraper engine with one or more marketplace URLs",
        description=f"{Fore.CYAN}Execute the car scraper with one or more marketplace search URLs. Results will be saved to storage/latest_results.json{Style.RESET_ALL}",
        formatter_class=ColorHelpFormatter
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
    run_parser.add_argument(
        "--use-proxy", 
        action="store_true", 
        help="Use proxy configuration from environment variables"
    )
    run_parser.add_argument(
        "--proxy-type", 
        type=str,
        choices=["NONE", "WEBSHARE_RESIDENTIAL"],
        default="NONE",
        help="Type of proxy to use (default: NONE)"
    )
    
    # Version command
    version_parser = subparsers.add_parser(
        "version", 
        help="Show version information",
        description=f"{Fore.CYAN}Display version and system information for the VroomSniffer car scraper.{Style.RESET_ALL}",
        formatter_class=ColorHelpFormatter
    )

    # Scheduler commands
    schedule_parser = subparsers.add_parser(
        "schedule",
        help="Schedule periodic scraping runs",
        description=f"{Fore.CYAN}Set up automatic scraping at fixed intervals{Style.RESET_ALL}",
        formatter_class=ColorHelpFormatter
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
    schedule_parser.add_argument(
        "--use-proxy", 
        action="store_true", 
        help="Use proxy configuration from environment variables"
    )
    schedule_parser.add_argument(
        "--proxy-type", 
        type=str,
        choices=["NONE", "WEBSHARE_RESIDENTIAL"],
        default="NONE",
        help="Type of proxy to use (default: NONE)"
    )
    
    # Diagnostics command
    diag_parser = subparsers.add_parser(
        "diagnostics", 
        help="Display diagnostic information",
        description=f"{Fore.CYAN}Show various diagnostic information about the system, including IP tracking data.{Style.RESET_ALL}",
        formatter_class=ColorHelpFormatter
    )
    diag_parser.add_argument(
        "--show-ip-tracking",
        action="store_true",
        help="Display IP tracking information for URLs"
    )
    
    return parser
