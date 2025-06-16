# VroomSniffer CLI Documentation

Welcome to the VroomSniffer CLI Documentation. This document provides comprehensive information about using and extending the command-line interface for the car listing scraper.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Reference](#quick-reference)
4. [Getting Started](#getting-started)
5. [Command Reference](#command-reference)
   - [Running the Scraper](#running-the-scraper)
   - [Listing Results](#listing-results)
   - [Searching Results](#searching-results)
   - [Sending Notifications](#sending-notifications)
   - [Scheduling Scraper Jobs](#scheduling-scraper-jobs)
6. [Storage Files](#storage-files)
7. [Practical Examples](#practical-examples)
   - [Daily Car Search Routine](#daily-car-search-routine)
   - [Weekend Marketplace Monitor](#weekend-marketplace-monitor)
   - [Targeted Search Scripts](#targeted-search-scripts)
8. [Technical Reference](#technical-reference)
   - [Architecture Overview](#architecture-overview)
   - [Command Structure](#command-structure)
   - [Extension Points](#extension-points)
9. [Troubleshooting](#troubleshooting)

## Overview

The VroomSniffer CLI provides a powerful command-line interface for:

- Scraping car listings from online marketplaces
- Managing and searching listing data
- Sending notifications via Telegram
- Scheduling automated scraping jobs
- Monitoring the market for new listings

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/car_scraper.git
   cd car_scraper
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Telegram bot token (if you plan to use notifications):
   - Create a `.env` file in the project root
   - Add your Telegram bot token: `TELEGRAM_BOT_TOKEN=your_token_here`
   - Add your Telegram chat ID: `TELEGRAM_CHAT_ID=your_chat_id`

## Quick Reference

```bash
# Get help
python cli/main.py --help

# Run the scraper
python cli/main.py run [URL]

# List results
python cli/main.py list [--type all|new|latest] [--count N]

# Search for listings
python cli/main.py search [KEYWORD]

# Send notifications
python cli/main.py send [INDEXES]
python cli/main.py notify [KEYWORD]

# Schedule scraping
python cli/main.py schedule [URLS...] [--use-saved] [--random] [--interval N] [--runs N] [--notify-new]
```

## Getting Started

This section provides a quick introduction to using VroomSniffer CLI for car listing scraping and management.

### Basic Commands

#### Run a Scraper

Scrape car listings from a marketplace URL:

```bash
python cli/main.py run "https://www.marketplace.com/s-autos/bmw/k0c216"
```

Scrape multiple URLs:

```bash
python cli/main.py run "https://www.marketplace.com/s-autos/bmw/k0c216" "https://www.marketplace.com/s-autos/audi/k0c216"
```

Scrape and send notifications for new findings:

```bash
python cli/main.py run "https://www.marketplace.com/s-autos/bmw/k0c216" --notify-new
```

#### View Results

List all stored listings (first 10 by default):

```bash
python cli/main.py list
```

List all new listings:

```bash
python cli/main.py list --type new
```

List more results:

```bash
python cli/main.py list --count 20
```

#### Search Results

Search for specific keywords:

```bash
python cli/main.py search "bmw"
python cli/main.py search "automatic"
```

#### Send Notifications

Send specific listings via Telegram (by index number from the list command):

```bash
python cli/main.py send 1 3 5
```

Send a summary notification about all new listings:

```bash
python cli/main.py notify
```

#### Schedule Scraping Jobs

Run periodic scraping using saved URLs (from saved_urls.json):

```bash
python cli/main.py schedule --use-saved --interval 60 --runs 10
```

Run with random URL selection:

```bash
python cli/main.py schedule --use-saved --random
```

Run indefinitely until manually stopped:

```bash
python cli/main.py schedule --use-saved --runs 0
```

## Command Reference

The CLI provides the following main commands:

```
usage: main.py [-h] {list,search,send,notify,run,version,schedule} ...
```

### Running the Scraper

The `run` command executes the scraper engine with one or more marketplace URLs.

```bash
python cli/main.py run [URL1] [URL2] ... [--notify-new] [--notify-count COUNT]
```

**Options:**

- `urls`: One or more marketplace search URLs to scrape
- `--notify-new`: Send Telegram notifications for new listings found after scraping
- `--notify-count`: Number of new listings to send detailed notifications for (default: 5)

**Examples:**

```bash
# Scrape a single URL
python cli/main.py run "https://www.marketplace.com/s-autos/bmw/k0c216"

# Scrape multiple URLs
python cli/main.py run "https://www.marketplace.com/s-autos/bmw/k0c216" "https://www.marketplace.com/s-autos/audi/k0c216"

# Scrape and send notifications for new listings
python cli/main.py run "https://www.marketplace.com/s-autos/bmw/k0c216" --notify-new --notify-count 3
```

### Listing Results

The `list` command displays the scraped listings.

```bash
python cli/main.py list [--type TYPE] [--count COUNT]
```

**Options:**

- `--type`: Type of listings to display (choices: `latest`, `all`, `new`; default: `all`)
  - `all`: All stored listings (from all_old_results.json)
  - `latest`: Most recent scraping run (from latest_results.json)
  - `new`: Only new listings from last run (from latest_new_results.json)
- `--count`: Number of listings to display (default: 10, use 0 for all)

**Examples:**

```bash
# List all stored listings (default, shows first 10)
python cli/main.py list

# List all new listings
python cli/main.py list --type new

# List 20 results from the latest run
python cli/main.py list --type latest --count 20

# List all stored listings
python cli/main.py list --count 0
```

### Searching Results

The `search` command allows you to search for specific keywords in the listings.

```bash
python cli/main.py search KEYWORD
```

**Options:**

- `keyword`: The keyword to search for in listing titles and descriptions

**Examples:**

```bash
# Search for BMW listings
python cli/main.py search "bmw"

# Search for automatic transmission
python cli/main.py search "automatic"

# Search for specific models
python cli/main.py search "320d"
```

### Sending Notifications

The CLI provides two commands for sending notifications:

#### 1. Send specific listings

The `send` command sends one or more specific listings via Telegram.

```bash
python cli/main.py send INDEX1 [INDEX2] [INDEX3] ...
```

**Options:**

- `indexes`: One or more listing indexes to send (as shown in the `list` command output)

**Examples:**

```bash
# Send listing #3
python cli/main.py send 3

# Send multiple listings
python cli/main.py send 1 5 7
```

#### 2. Send summary notifications

The `notify` command sends a summary notification about the latest findings.

```bash
python cli/main.py notify [KEYWORD]
```

**Options:**

- `keyword`: Optional search keyword to filter listings before sending

**Examples:**

```bash
# Send notification about all new listings
python cli/main.py notify

# Send notification about BMW listings only
python cli/main.py notify "bmw"
```

### Scheduling Scraper Jobs

The `schedule` command sets up automatic scraping at fixed intervals.

```bash
python cli/main.py schedule [URLs ...] [--use-saved] [--random] [--interval SECONDS] [--runs COUNT] [--notify-new] [--notify-count COUNT]
```

**Options:**

- `urls`: One or more marketplace search URLs to scrape periodically (omit to use saved URLs)
- `--use-saved`: Use URLs from saved_urls.json instead of providing URLs directly
- `--random`: Select URLs randomly instead of sequentially
- `--interval`: Interval between scraping runs in seconds (default: 60, minimum: 30)
- `--runs`: Maximum number of scraping runs to perform (default: 5, use 0 for unlimited)
- `--notify-new`: Send notifications for new listings found in each run
- `--notify-count`: Number of new listings to send detailed notifications for (default: 5)

**Examples:**

```bash
# Schedule scraping with a single URL, run 10 times with 60-second intervals
python cli/main.py schedule "https://www.marketplace.com/s-autos/bmw/k0c216" --runs 10

# Schedule using saved URLs, randomly selected, with notifications
python cli/main.py schedule --use-saved --random --notify-new

# Schedule with multiple URLs and a 2-minute interval
python cli/main.py schedule "https://www.marketplace.com/s-autos/bmw/k0c216" "https://www.marketplace.com/s-autos/audi/k0c216" --interval 120
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
python cli/main.py run "https://www.marketplace.com/s-autos/bmw-320d/k0c216" --notify-new

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
python cli/main.py run "https://www.marketplace.com/s-autos/bmw/k0c216" "https://www.marketplace.com/s-autos/audi/k0c216" "https://www.marketplace.com/s-autos/mercedes/k0c216"

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
python cli/main.py run "https://www.marketplace.com/s-autos/bmw/k0c216" "https://www.marketplace.com/s-autos/audi/k0c216"

# Notify about new findings
python cli/main.py notify

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
python cli/main.py schedule "https://www.marketplace.com/s-autos/bmw/preis:-10000/k0c216" --runs 20 --interval 300 --notify-new
```

**Price Tracking Over Time**

To track how prices change over time:

```bash
# Run daily scrapes for a specific model
python cli/main.py run "https://www.marketplace.com/s-autos/golf-gti/k0c216"

# Compare with historical data
python cli/main.py list --type all
python cli/main.py search "golf gti"
```

## Technical Reference

This section provides technical information about the CLI architecture and extension points for developers.

### Architecture Overview

The VroomSniffer CLI is built on a service-based architecture with the following key components:

- **CLI Interface** (`cli/main.py`): Command-line interface and argument parsing
- **Service Layer**:
  - `ScraperService`: Handles the scraping operations
  - `StorageService`: Manages data persistence and retrieval
  - `NotificationService`: Handles notifications via Telegram
  - `SchedulerService`: Manages timing and scheduling of operations
- **Core Engines**:
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

1. Add a new parser to the subparsers collection:
   ```python
   new_command_parser = subparsers.add_parser(
       "newcommand", 
       help="Description of new command"
   )
   # Add arguments to new_command_parser
   ```

2. Create a handler function:
   ```python
   def handle_new_command(args):
       # Implementation
   ```

3. Add the command to the main execution block:
   ```python
   elif args.command == "newcommand":
       handle_new_command(args)
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
  "urls": [
    "https://www.marketplace.com/s-autos/bmw/k0c216",
    "https://www.marketplace.com/s-autos/audi/k0c216",
    "https://www.marketplace.com/s-autos/mercedes/k0c216"
  ],
  "last_updated": "2025-06-16 14:34:18"
}
```

You can edit this file manually to add or remove URLs.

#### Configuring Telegram Notifications

To use the Telegram notification features, you need to configure your Telegram bot token and chat ID in the appropriate configuration file or environment variables.

Create a `.env` file in the project root with:
```
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id
```

### Getting Help

For more information, run any command with the `-h` or `--help` flag:

```bash
python cli/main.py --help
python cli/main.py run --help
python cli/main.py schedule --help
```
