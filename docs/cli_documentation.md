# VroomSniffer CLI Documentation

Welcome to the VroomSniffer CLI Documentation. This comprehensive guide covers all commands, options, and usage examples for the command-line interface.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Reference](#quick-reference)
4. [Command Reference](#command-reference)
   - [run - Running the Scraper](#run---running-the-scraper)
     - [Basic Usage](#run-basic-usage)
     - [With Notifications](#run-with-notifications)
     - [With Proxy](#run-with-proxy)
     - [Full Options](#run-full-options)
   - [list - Viewing Results](#list---viewing-results)
     - [Filtering Results](#list-filtering-results)
     - [Viewing All Results](#list-viewing-all-results)
   - [search - Finding Specific Listings](#search---finding-specific-listings)
   - [send - Manual Notifications](#send---manual-notifications)
   - [schedule - Automated Monitoring](#schedule---automated-monitoring)
     - [Basic Scheduling](#schedule-basic-scheduling)
     - [Advanced Settings](#schedule-advanced-settings)
     - [Using Saved URLs](#schedule-using-saved-urls)
   - [diagnostics - System Information](#diagnostics---system-information)
     - [IP Tracking Information](#diagnostics-ip-tracking)
   - [version - Version Information](#version---version-information)
5. [Using Proxies](#using-proxies)
6. [IP Tracking](#ip-tracking)
7. [Practical Examples](#practical-examples)
   - [Basic Usage Examples](#basic-usage-examples) 
   - [Advanced Usage Patterns](#advanced-usage-patterns)
   - [Automation Scripts](#automation-scripts)
   - [Command Combinations](#command-combinations)
8. [Storage Files](#storage-files)
9. [Troubleshooting](#troubleshooting)

## Overview

The VroomSniffer CLI is a powerful command-line tool that lets you:

- Scrape car listings from online marketplaces
- Manage and search through listing data
- Send notifications via Telegram
- Schedule automated monitoring
- Track which IPs are used for scraping
- Configure proxy usage for enhanced reliability

## Installation

1. Ensure you have Python 3.7+ installed
2. Install the required packages:
```bash
pip install -r requirements.txt
playwright install
```

3. For notifications, configure your Telegram credentials in a `.env` file:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

4. For proxy support, configure WebShare credentials in a `.env` file:
```
WEBSHARE_USERNAME=your_username_here
WEBSHARE_PASSWORD=your_password_here
```

## Quick Reference

```bash
# Get help for all commands
python cli/main.py --help

# Get help for a specific command
python cli/main.py run --help

# Run the scraper with a URL
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw"

# Run with proxy support
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --use-proxy --proxy-type WEBSHARE_RESIDENTIAL

# List results (first 10 by default)
python cli/main.py list

# List all new listings
python cli/main.py list --type new

# Search for specific cars
python cli/main.py search "bmw"

# Send notifications for specific listings (by index)
python cli/main.py send 1 3 5

# Run scraper on a schedule with saved URLs
python cli/main.py schedule --use-saved --interval 300

# Check IP tracking information
python cli/main.py diagnostics --show-ip-tracking
```

## Command Reference

### run - Running the Scraper

The `run` command executes the scraper on one or more URLs. This is the primary command for gathering car listings from marketplace websites.

```bash
python cli/main.py run [URLs...] [options]
```

#### Arguments:
- `URLs`: One or more marketplace search URLs to scrape (required)

#### Options:
- `--notify-new`: Send Telegram notifications for new listings found
- `--notify-count N`: Limit notifications to N listings (default: -1 means all)
- `--use-proxy`: Use proxy for scraping to avoid blocking
- `--proxy-type TYPE`: Type of proxy to use: NONE or WEBSHARE_RESIDENTIAL (default: NONE)

#### What happens when you run this command:
1. The system checks if the provided URLs are valid
2. For each URL, the scraper:
   - Connects to the webpage (directly or through a proxy)
   - Records the IP address used for tracking
   - Extracts car listing information
   - Compares new results with existing listings
   - Stores all listings in storage files
3. If `--notify-new` is used, sends notifications via Telegram
4. Shows a summary of found listings 

#### Examples:

##### Run Basic Usage

```bash
# SIMPLEST: Basic scraping of one URL
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw"

# MULTIPLE URLS: Scrape multiple URLs at once
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" "https://www.example-marketplace.com/cars/search?brand=audi"
```

##### Run With Notifications

```bash
# WITH NOTIFICATIONS: Scrape and send notifications for all new listings
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --notify-new

# LIMIT NOTIFICATIONS: Only notify about the first 5 new listings
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --notify-new --notify-count 5
```

##### Run With Proxy

```bash
# WITH PROXY: Scrape using WebShare rotating residential proxies
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --use-proxy --proxy-type WEBSHARE_RESIDENTIAL
```

##### Run Full Options

```bash
# FULL EXAMPLE: Scrape with proxy, and limit notifications to 3 listings
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --use-proxy --proxy-type WEBSHARE_RESIDENTIAL --notify-new --notify-count 3

# FILTERED NOTIFICATION: Only send notifications for the first 5 new BMW listings
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --notify-new --notify-count 5
```

### list - Viewing Results

The `list` command displays scraped listings from storage, with options to filter by listing type and control the number shown.

```bash
python cli/main.py list [options]
```

#### Options:
- `--type TYPE`: Type of listings to display:
  - `all` (default): All stored listings from historical runs
  - `latest`: Only listings from the most recent run
  - `new`: Only new listings that were discovered in the last run
- `--count N`: Number of listings to display (default: 10, use 0 to show all)

#### What happens when you run this command:
1. Based on the `--type` option, the system loads listings from:
   - `all`: storage/all_old_results.json (complete history)
   - `latest`: storage/latest_results.json (most recent scrape)
   - `new`: storage/latest_new_results.json (new discoveries)
2. Displays listings in a formatted table with:
   - ID number (for use with other commands)
   - Title (truncated if too long)
   - Price
   - Location
   - Posted date (when available)
3. Shows the requested number of listings (default 10)

#### Examples:

##### List Filtering Results

```bash
# SIMPLEST: List all stored listings (first 10)
python cli/main.py list

# NEW LISTINGS ONLY: Show only newly discovered listings
python cli/main.py list --type new

# LATEST RUN: List only listings from the most recent scrape
python cli/main.py list --type latest
```

##### List Viewing All Results

```bash
# MORE RESULTS: Show more listings (20)
python cli/main.py list --count 20

# ALL RESULTS: Show all available listings (could be many!)
python cli/main.py list --count 0

# COMBINE OPTIONS: Show all new listings from the last run
python cli/main.py list --type new --count 0
```

### search - Finding Specific Listings

The `search` command searches for listings that contain a specific keyword in their title or description. This helps you filter through potentially hundreds of listings to find exactly what you're looking for.

```bash
python cli/main.py search KEYWORD
```

#### Arguments:
- `KEYWORD`: Term to search for in listing titles and descriptions (required)

#### What happens when you run this command:
1. The system loads all stored listings from storage/all_old_results.json
2. It searches through all listings for the keyword (case-insensitive)
3. Displays matching listings in a formatted list with:
   - Index number
   - Title (truncated)
   - Price
   - Location
4. Shows up to 10 matches, with a message if there are more

#### Examples:

```bash
# SIMPLEST: Search for a brand name
python cli/main.py search "bmw"

# SPECIFIC MODEL: Search for a specific car model
python cli/main.py search "320d"

# FEATURE SEARCH: Search for cars with a specific feature
python cli/main.py search "diesel"
python cli/main.py search "automatic" 
python cli/main.py search "leather"

# PRICE RANGE: Search for cars in a price range (if included in title)
python cli/main.py search "euro"

# YEAR MODEL: Search for cars from a specific year
python cli/main.py search "2018"

# COMBINED SEARCH: Search for a specific model feature
python cli/main.py search "bmw diesel"
```

### send - Manual Notifications

The `send` command allows you to manually send specific listings to your Telegram account. This is useful for sharing interesting listings with others or sending them to your phone for later review.

```bash
python cli/main.py send INDEXES
```

#### Arguments:
- `INDEXES`: One or more listing indexes to send (from the list command) (required)

#### What happens when you run this command:
1. The system loads listings from storage/all_old_results.json
2. For each provided index number:
   - Finds the corresponding listing
   - Formats it as a nice Telegram message with title, price, location, and URL
   - Sends the message via the Telegram Bot API
   - Shows success or failure for each message
3. Provides a summary of sent messages

#### Prerequisites:
- You must have Telegram credentials configured in your .env file:
  ```
  TELEGRAM_BOT_TOKEN=your_token_here
  TELEGRAM_CHAT_ID=your_chat_id_here
  ```
- You should run the `list` command first to see available listing indexes

#### Examples:

```bash
# SIMPLEST: Send a single listing (index #3)
python cli/main.py send 3

# MULTIPLE LISTINGS: Send several listings at once
python cli/main.py send 1 3 5

# WORKFLOW EXAMPLE: Find and send listings
# First, list all BMW listings:
python cli/main.py search "bmw"
# Then send the interesting ones:
python cli/main.py send 2 7

# SEND ALL NEW FINDINGS: First list new items, then send them
# (Assuming you have 3 new items with indexes 1, 2, and 3)
python cli/main.py list --type new
python cli/main.py send 1 2 3
```

### schedule - Automated Monitoring

The `schedule` command sets up periodic scraping at fixed intervals, allowing VroomSniffer to continuously monitor listings without manual intervention. This is particularly useful for catching new listings quickly.

```bash
python cli/main.py schedule [URLs...] [options]
```

#### Arguments:
- `URLs`: One or more URLs to scrape (optional if using `--use-saved`)

#### Options:
- `--use-saved`: Use URLs from storage/saved_urls.json instead of command line arguments
- `--random`: Select URLs randomly instead of sequentially (useful for rotating between different searches)
- `--interval N`: Seconds between scraping runs (default: 60 seconds, minimum: 30 seconds)
- `--runs N`: Maximum number of runs to perform (default: 5, use 0 for unlimited runs until manually stopped)
- `--notify-new`: Send Telegram notifications for new listings found in each run
- `--notify-count N`: Limit notifications to N listings per run (default: -1 for all new listings)
- `--use-proxy`: Use proxy for scraping to avoid blocking
- `--proxy-type TYPE`: Type of proxy to use: NONE or WEBSHARE_RESIDENTIAL (default: NONE)

#### What happens when you run this command:
1. The system loads URLs either from command line arguments or saved_urls.json
2. The scheduler:
   - Starts a continuous loop that runs until the maximum number of runs is reached
   - For each run, selects a URL (either sequentially or randomly)
   - Executes the scraper for the selected URL
   - If `--notify-new` is enabled, sends notifications for new listings
   - Waits for the specified interval before the next run
   - Shows progress and countdown between runs
3. Continues until all runs are complete or until interrupted with Ctrl+C

#### Setting Up Saved URLs:
To use the `--use-saved` option, you need to have URLs stored in storage/saved_urls.json. The file format is:
```json
{
  "url_data": {
    "https://www.example-marketplace.com/cars/search?brand=bmw": {
      "description": "BMW cars",
      "stats": {
        "run_count": 35,
        "total_listings": 330,
        "last_run": "2025-06-19 05:45:55"
      }
    },
    "https://www.example-marketplace.com/cars/search?brand=audi": {
      "description": "Audi cars",
      "stats": {
        "run_count": 32,
        "total_listings": 198,
        "last_run": "2025-06-19 05:37:55"
      }
    }
  },
  "last_updated": "2025-06-19 05:47:59"
}
```

#### Examples:

##### Schedule Basic Scheduling

```bash
# SIMPLEST: Schedule a specific URL to run 5 times (default)
python cli/main.py schedule "https://www.example-marketplace.com/cars/search?brand=bmw"

# CONTINUOUS MONITORING: Run indefinitely until manually stopped (Ctrl+C)
python cli/main.py schedule --use-saved --runs 0

# LONGER INTERVALS: Run every 5 minutes (300 seconds)
python cli/main.py schedule --use-saved --interval 300
```

##### Schedule Using Saved URLs

```bash
# USING SAVED URLS: Schedule scraping with URLs from saved_urls.json
python cli/main.py schedule --use-saved

# RANDOM SELECTION: Select URLs randomly from saved list
python cli/main.py schedule --use-saved --random
```

##### Schedule Advanced Settings

```bash
# WITH NOTIFICATIONS: Send Telegram messages for new listings
python cli/main.py schedule --use-saved --notify-new

# WITH PROXY: Use WebShare residential proxies
python cli/main.py schedule --use-saved --use-proxy --proxy-type WEBSHARE_RESIDENTIAL

# LIMITED NOTIFICATIONS: Only send 3 notifications per run
python cli/main.py schedule --use-saved --notify-new --notify-count 3

# COMPLETE EXAMPLE: Continuous monitoring with all options
python cli/main.py schedule --use-saved --random --interval 300 --runs 0 --notify-new --notify-count 5 --use-proxy --proxy-type WEBSHARE_RESIDENTIAL
```

### diagnostics - System Information

The `diagnostics` command provides system diagnostic information about VroomSniffer, including IP tracking data that shows which IP addresses have been used for each URL.

```bash
python cli/main.py diagnostics [options]
```

#### Options:
- `--show-ip-tracking`: Display detailed IP tracking information for URLs

#### What happens when you run this command:
1. With `--show-ip-tracking`:
   - Loads the IP tracking data from storage/ip_tracking.json
   - Displays information about each tracked URL
   - Shows the direct IPs used (without proxy)
   - Shows the proxy IPs used (when using a proxy)
   - For each IP shows:
     - The IP address
     - When it was first used
     - When it was last used
     - How many times it was used
   - Provides a summary of the overall tracking information

#### Why use this command:
- Monitor which IPs are being used to access each URL
- Verify if your proxy is working correctly (should show different IPs when used)
- Ensure you're not repeatedly using the same IP for a website (which could lead to blocking)

#### Examples:

##### Diagnostics IP Tracking

```bash
# SIMPLEST: Show IP tracking information
python cli/main.py diagnostics --show-ip-tracking

# Check if proxy is working after running with proxy
# First run scraper with proxy:
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --use-proxy --proxy-type WEBSHARE_RESIDENTIAL
# Then check the IPs used:
python cli/main.py diagnostics --show-ip-tracking
```

### version - Version Information

The `version` command displays the current version of VroomSniffer. This is a simple, no-arguments command to verify your installation.

```bash
python cli/main.py version
```

#### What happens when you run this command:
- Displays the current version number of VroomSniffer
- No additional options or arguments are needed

#### Example:

```bash
# Check VroomSniffer version
python cli/main.py version
# Output: 🚗 VroomSniffer Car Scraper v1.0.0
```

## Command Combinations

The real power of VroomSniffer comes from combining commands for efficient workflows. Here are some common combinations:

### Finding and Sending Specific Cars

```bash
# Step 1: Run the scraper to get fresh listings
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw"

# Step 2: Find interesting cars
python cli/main.py search "diesel automatic"

# Step 3: Check full details of new listings
python cli/main.py list --type new

# Step 4: Send the best matches to your Telegram
python cli/main.py send 2 5
```

### Continuous Monitoring Workflow

```bash
# Step 1: Schedule continuous monitoring with notifications
python cli/main.py schedule --use-saved --runs 0 --notify-new --interval 300

# Step 2: Periodically check what's been found
python cli/main.py list --type new

# Step 3: When you find something interesting, send it
python cli/main.py send 3
```

### Weekend Car Shopping

```bash
# Friday: Set up monitoring for the weekend
python cli/main.py schedule --use-saved --random --runs 100 --interval 1800 --notify-new

# Saturday morning: Check what was found overnight
python cli/main.py list --type new

# Sunday: Send the best listings to your phone for follow-up
python cli/main.py send 1 4 7
```

## Storage Files

The VroomSniffer CLI uses several JSON files for data storage and management:

- **all_old_results.json**: Contains all historical listings that have been scraped. This is the main storage file used by default for listing, searching, and sending operations.
- **latest_results.json**: Contains only the results from the most recent scraping run.
- **latest_new_results.json**: Contains only the new listings (not seen before) from the most recent scraping run. This file is used for notifications about new listings.
- **saved_urls.json**: Contains URLs to be used with the `--use-saved` option when running the scheduler.

These files are located in the `storage/` directory. You can directly inspect or modify them if needed, though it's generally recommended to use the CLI commands to interact with the data.

## Practical Examples

This section provides practical examples for common use cases of the VroomSniffer CLI tool.

### Daily Car Search Routine

If you're looking for a specific car model daily:

```bash
# Morning check for new BMW listings
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw&model=320d" --notify-new

# Search for specific features in the results
python cli/main.py search "leather"
python cli/main.py search "automatic"

# Send the most interesting listings to your phone
python cli/main.py send 3 7
```

### Weekend Marketplace Monitor

For weekend car hunting sessions:

```bash
# Scrape multiple brands of interest
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" "https://www.example-marketplace.com/cars/search?brand=audi" "https://www.example-marketplace.com/cars/search?brand=mercedes"

# List all results
python cli/main.py list --count 0

# Filter by budget
python cli/main.py search "price:5000-15000"

# Send top candidates to your phone
python cli/main.py send 2 5 8
```

### Targeted Search Scripts

You can chain commands in a script for more complex workflows:

**Example Script: market_check.sh**
```bash
#!/bin/bash
# Run scraper for multiple brands
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" "https://www.example-marketplace.com/cars/search?brand=audi"

# Notify about new findings
python cli/main.py list --type new

# Look for specific features
python cli/main.py search "navigation"
python cli/main.py search "leather"
```

**Example Script: weekend_monitor.sh**
```bash
#!/bin/bash
# Run continuous monitoring over the weekend
python cli/main.py schedule --use-saved --random --runs 100 --interval 1800 --notify-new
```

**Automated Market Monitoring**

To monitor the market continuously while you work:

```bash
# Setup saved_urls.json with your favorite searches
# Then run continuous monitoring with random URL selection
python cli/main.py schedule --use-saved --random --runs 0 --interval 300 --notify-new

# Check new findings periodically
python cli/main.py list --type new
```

**Deal Hunting**

To be notified about great deals as soon as they appear:

```bash
# Set up a specific search for bargains
python cli/main.py schedule "https://www.example-marketplace.com/cars/search?brand=bmw&price_max=10000" --runs 20 --interval 300 --notify-new
```

**Price Tracking Over Time**

To track how prices change over time:

```bash
# Run daily scrapes for a specific model
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=volkswagen&model=golf-gti"

# Compare with historical data
python cli/main.py list --type all
python cli/main.py search "golf gti"
```

## Technical Reference

This section provides technical information about the CLI architecture and extension points for developers.

### Architecture Overview

The VroomSniffer CLI is built on a modular, service-based architecture with the following key components:

#### Module Organization

The CLI is organized into several modules:

1. **main.py**: Entry point for the CLI
   - Orchestrates the flow between command-line arguments and command implementation
   - Provides the `main()` function as the primary entrypoint
   
2. **commands.py**: Implementation of all command functions
   - Contains the actual implementation of each command
   - Functions are pure and accept services as dependencies
   - Implements command logic with consistent error handling
   
3. **argparse_setup.py**: Command-line argument parsing
   - Centralizes all argument parsing logic
   - Configures and returns an `ArgumentParser` instance 
   
4. **utils.py**: Utility functions and services
   - Provides the `Services` class to encapsulate all service instances
   - Contains helper functions used across commands
   - Includes decorators for common patterns (like progress bars)

#### Service Layer

- **ScraperService**: Handles the scraping operations
- **StorageService**: Manages data persistence and retrieval
- **NotificationService**: Handles notifications via Telegram
- **SchedulerService**: Manages timing and scheduling of operations

#### Core Engines:
  - `scraper/engine.py`: The scraping engine that extracts data
  - `proxy/manager.py`: Manages proxy connections (if used)

### Command Structure

The CLI uses Python's `argparse` library to create a nested command structure with subcommands:

```
main.py
  │
  ├── list
  ├── search
  ├── send
  ├── notify
  ├── run
  ├── version
  └── schedule
```

Each command has its own argument parser and handler function.

### Extension Points

#### Adding a New Command

To add a new command to the CLI:

1. Add the command implementation in `commands.py`:
   ```python
   def handle_new_command(services: Services, arg1: str, arg2: int = 0) -> None:
       """
       New command implementation
       
       Args:
           services: Services instance
           arg1: First argument
           arg2: Second argument (optional)
       """
       # Implementation
   ```

2. Add a new parser in `argparse_setup.py`:
   ```python
   new_command_parser = subparsers.add_parser(
       "newcommand", 
       help="Description of new command"
   )
   # Add arguments to new_command_parser
   new_command_parser.add_argument("arg1", type=str, help="First argument")
   new_command_parser.add_argument("--arg2", type=int, default=0, help="Second argument")
   ```

3. Add the command to the main execution block in `main.py`:
   ```python
   elif args.command == "newcommand":
       handle_new_command(services, args.arg1, args.arg2)
   ```

#### Extending Notification Options

To add a new notification channel:

1. Extend `NotificationService` with new methods
2. Add a new provider to `notifier/` directory
3. Update the CLI commands that use notifications

#### Adding New Storage Capabilities

To extend storage capabilities:

1. Add new methods to `StorageService`
2. Update CLI commands to use these new methods

## Troubleshooting

### Common Issues

1. **No listings found**: Make sure the URL format is correct and the marketplace website is accessible.

2. **Failed to send notifications**: Check your Telegram bot configuration.

3. **Error while scraping**: The marketplace might have changed its structure or implemented anti-scraping measures.

4. **Scheduler not running as expected**: Verify the interval settings and make sure you've provided valid URLs or have properly set up the `saved_urls.json` file.

5. **Missing data in storage files**: Check file permissions and make sure the storage directory is writable.

### Advanced Configuration

#### Managing Saved URLs

The `saved_urls.json` file allows you to store frequently used URLs for scraping. The format is:

```json
{
  "url_data": {
    "https://www.example-marketplace.com/cars/search?brand=bmw": {
      "description": "BMW cars",
      "stats": {
        "run_count": 35,
        "total_listings": 330,
        "last_run": "2025-06-19 05:45:55"
      }
    },
    "https://www.example-marketplace.com/cars/search?brand=audi": {
      "description": "Audi cars",
      "stats": {
        "run_count": 32,
        "total_listings": 198,
        "last_run": "2025-06-19 05:37:55"
      }
    }
  },
  "last_updated": "2025-06-19 05:47:59"
}
```

You can edit this file manually to add or remove URLs, or add descriptions to help organize your saved searches.

#### Configuring Telegram Notifications

To use the Telegram notification features, you need to configure your Telegram bot token and chat ID in the appropriate configuration file or environment variables.

Create a `.env` file in the project root with:
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id
```

## Using Proxies

VroomSniffer supports WebShare rotating residential proxies to help avoid blocking while scraping. This section explains how to set up and use proxies with the CLI.

### Proxy Types

VroomSniffer supports these proxy types:

- **NONE**: No proxy (default) - uses your direct connection
- **WEBSHARE_RESIDENTIAL**: WebShare rotating residential proxies - each request uses a different IP address

### Setup Steps

1. **Create a WebShare Account**:
   - Sign up at [WebShare.io](https://www.webshare.io/)
   - Subscribe to a rotating residential proxy plan (they offer various options)
   - Obtain your proxy credentials (username and password)
   - Note the proxy endpoint details (usually `p.webshare.io` port `80`)

2. **Configure Environment Variables**:
   Create a `.env` file in the project root with your WebShare credentials:

   ```
   # WebShare Proxy Configuration
   PROXY_TYPE=WEBSHARE_RESIDENTIAL
   WEBSHARE_USERNAME=your_webshare_username
   WEBSHARE_PASSWORD=your_webshare_password
   WEBSHARE_PROXY_HOST=p.webshare.io
   WEBSHARE_PROXY_PORT=80
   ```

3. **Using Proxies with Commands**:
   Add the `--use-proxy` and `--proxy-type` options to the `run` or `schedule` commands:

   ```bash
   # Run with proxy
   python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --use-proxy --proxy-type WEBSHARE_RESIDENTIAL

   # Schedule with proxy
   python cli/main.py schedule --use-saved --use-proxy --proxy-type WEBSHARE_RESIDENTIAL
   ```

### Testing Your Proxy Configuration

VroomSniffer includes a script to test if your proxy configuration is working correctly:

```bash
python scripts/verify_proxy.py
```

This script will:
1. Check your current direct IP address
2. Connect through your configured proxy
3. Verify that your IP changes (confirming the proxy is working)
4. Display both IPs for comparison

### How Proxies Work

When you run the scraper with the `--use-proxy` flag:

1. The system connects to WebShare's proxy service using your credentials
2. Each request is routed through a different residential IP address
3. The website sees traffic coming from regular residential connections instead of your IP
4. This helps avoid triggering anti-bot measures and IP blocking
5. The system tracks which IPs were used (view with `diagnostics --show-ip-tracking`)

### Proxy Tips

1. **Rotation Strategy**: WebShare automatically rotates IPs between requests
2. **Speed Considerations**: Using a proxy may slow down scraping slightly
3. **Cost Management**: Be aware of your proxy provider's pricing model (usually per GB)
4. **Troubleshooting**: If the proxy isn't working, verify your credentials in the `.env` file
5. **IP Verification**: Always check that your IP is actually changing with the `diagnostics` command

### Verifying Your Proxy Connection

You can verify that your proxy is working by:

1. Running the proxy verification script:
   ```bash
   python scripts/verify_proxy.py
   ```

2. Using the diagnostics command to check IP tracking after a scraping run:
   ```bash
   python cli/main.py diagnostics --show-ip-tracking
   ```
   Look for different IPs in the "Proxy IPs" section.

## IP Tracking

VroomSniffer automatically tracks which IP addresses are used to access each URL. This helps monitor proxy rotation and avoid potential blocking.

### How IP Tracking Works

Each time the scraper accesses a URL, it records:
- The IP address used (your direct IP or the proxy IP)
- Whether it was a proxy or direct connection
- When the IP was first used for that URL
- When the IP was last used for that URL
- How many times each IP has been used for each URL

This data is stored in `storage/ip_tracking.json`.

### Viewing IP Tracking Data

Use the diagnostics command to view your IP tracking information:

```bash
python cli/main.py diagnostics --show-ip-tracking
```

This shows:
- All URLs that have been tracked
- For each URL:
  - Direct IPs used (when not using a proxy)
  - Proxy IPs used (when using a proxy)
  - First and last use timestamps
  - Usage counts

### IP Tracking Data Format

The IP tracking file (`storage/ip_tracking.json`) has the following format:

```json
{
  "url_ip_mapping": {
    "https://www.example-marketplace.com/cars/search?brand=bmw": [
      {
        "ip": "123.45.67.89",
        "first_used": "2025-06-19 01:09:40",
        "last_used": "2025-06-19 01:12:10",
        "is_proxy": true,
        "use_count": 2
      },
      {
        "ip": "98.76.54.32",
        "first_used": "2025-06-19 02:38:24",
        "last_used": "2025-06-19 02:38:24",
        "is_proxy": true,
        "use_count": 1
      }
    ]
  },
  "last_updated": "2025-06-19 05:47:59"
}
```

### Benefits of IP Tracking

1. **Verify Proxy Rotation**: Confirm that your proxy provider is actually rotating IPs
2. **Monitor Blocking Risk**: If you're repeatedly using the same IP, you might be at risk of being blocked
3. **Audit Usage**: Keep track of your scraping activities over time
4. **Optimize Scraping Strategy**: Use IP data to determine optimal scraping intervals and patterns

### Getting Help

For more information, run any command with the `-h` or `--help` flag:

```bash
python cli/main.py --help
python cli/main.py run --help
python cli/main.py schedule --help
```

