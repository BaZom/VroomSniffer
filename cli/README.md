# Caralyze CLI Documentation

## Overview
The Caralyze CLI provides a command-line interface for interacting with the car scraper system. It allows you to run scrapers, browse results, search listings, and share findings via Telegram.

This CLI is now organized in its own dedicated folder with isolated data storage and components.

## Installation & Setup
```bash
# Navigate to the project directory
cd d:\caralyze\car_scraper

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

## CLI Structure
```
cli/
├── __init__.py           # CLI package initialization
├── main.py              # Main CLI application
├── README.md            # This documentation
└── data/                # CLI-specific data storage
    ├── latest_results.json      # Latest scraping results
    ├── all_old_results.json     # Historical data
    └── latest_new_results.json  # New listings only
```

## Available Commands

### 1. `run` - Execute the scraper
```bash
python cli/main.py run "https://www.kleinanzeigen.de/s-autos/bmw/k0c216"
```
- Scrapes car listings from the provided Kleinanzeigen URL
- Results saved to `cli/data/latest_results.json`
- Overwrites previous results
- Automatically copies results from main scraper output

### 2. `list` - View latest listings
```bash
python cli/main.py list
```
- Displays the most recent scraped listings
- Shows first 10 results with title, price, and location
- Each listing has an index number for reference

### 3. `search` - Find specific cars
```bash
python cli/main.py search "bmw"
python cli/main.py search "automatic"
python cli/main.py search "diesel"
```
- Searches through listing titles for keywords
- Case-insensitive matching
- Shows matching listings with their index numbers

### 4. `send` - Share via Telegram
```bash
python cli/main.py send 3
```
- Sends a specific listing via Telegram
- Use the index number from the `list` command
- Requires Telegram configuration

### 5. `version` - System information
```bash
python cli/main.py version
```
- Shows version and system information

### 6. `--help` - Get help
```bash
python cli/main.py --help
python cli/main.py run --help
python cli/main.py search --help
```

## Example Workflow

### 1. Scrape BMW listings
```bash
python cli/main.py run "https://www.kleinanzeigen.de/s-autos/bmw/k0c216"
```

### 2. Browse all results
```bash
python cli/main.py list
```
Output:
```
[*] Found 26 listings:
[1] BMW X5 3.0d | 25.000 € | Berlin
[2] BMW 320i Touring | 18.500 € | Munich
[3] BMW M3 Competition | 45.000 € | Hamburg
...
```

### 3. Search for specific models
```bash
python cli/main.py search "x5"
```
Output:
```
[*] Found 3 matches for 'x5':
[1] BMW X5 3.0d | 25.000 €
[7] BMW X5 M Sport | 32.000 €
[12] BMW X5 xDrive40d | 28.500 €
```

### 4. Share interesting listings
```bash
python cli/main.py send 1
```
Output:
```
[+] Listing 1 sent via Telegram
```

## 🔔 Auto-Notifications

### Streamlit UI Auto-Notifications
The Streamlit interface now supports **automatic Telegram notifications**:

1. **Enable in Sidebar**: Toggle "📲 Auto-send new listings via Telegram"
2. **Configure Count**: Set "Max notifications per batch" (1-20)
3. **Start Monitoring**: Click "Start Monitoring" - new listings will be sent automatically
4. **Visual Feedback**: See real-time status of auto-notifications

**When auto-notifications are enabled:**
- 🚀 **Summary sent first** with count of new listings
- 📱 **Individual listings** sent with rich formatting (title, price, location, link)
- ⏱️ **Rate limiting** with 1.5 second delays between messages
- ✅ **Success feedback** showing how many were sent

### CLI Auto-Notifications
The scraper can also send automatic notifications:

```bash
# Run scraper with auto-notifications (default: 5 listings)
python scraper/ebay_kleinanzeigen_engine.py --url "..." --notify

# Specify how many listings to auto-send
python scraper/ebay_kleinanzeigen_engine.py --url "..." --notify --notify-count 3
```

**Features:**
- Automatically sends top N listings after scraping
- Rich HTML formatting with emojis
- Rate limiting (2 second delays)
- Works in test mode for corporate networks

## Data Storage

The CLI now has its own isolated data storage in the `cli/data/` directory:

- **Latest Results**: `cli/data/latest_results.json`
  - Contains the most recent scraping results
  - Used by `list`, `search`, and `send` commands
  - Automatically populated when running the scraper

- **Historical Data**: `cli/data/all_old_results.json`
  - Contains all previously seen listings
  - Isolated from main project storage

- **New Listings**: `cli/data/latest_new_results.json`
  - Contains only new listings from the last run
  - Used for notifications and monitoring

## Error Handling

### No listings found
```bash
$ python cli/main.py list
[!] No listings found. Run 'python cli/main.py run <url>' first.
```

### Invalid listing index
```bash
$ python cli/main.py send 99
[!] Listing index 99 not found. Use 'list' command to see available listings.
```

### Scraper failed
```bash
$ python cli/main.py run "invalid-url"
[!] Scraper run failed.
```

## Integration with Other Components

### Streamlit UI
For advanced features like filtering and monitoring:
```bash
streamlit run ui/streamlit_app.py
```

### Telegram Notifications
Configure Telegram settings in:
- `notifier/telegram.py`

### Service Layer
The CLI uses the service layer from:
- `services/caralyze_service.py`

## Key Changes in CLI Organization

1. **Dedicated CLI folder**: All CLI components are now in `cli/`
2. **Isolated data storage**: CLI has its own `data/` directory
3. **Updated import paths**: CLI properly imports from parent project
4. **Automatic result copying**: CLI automatically copies scraper results to its data directory
5. **Modular structure**: CLI is now a proper Python package

## Tips & Best Practices

1. **Always run the scraper first** before using other commands
2. **Use specific search terms** for better results
3. **Check listing indices** with `list` before using `send`
4. **Use the Streamlit UI** for complex filtering and monitoring
5. **Set up Telegram properly** before using the `send` command

## Troubleshooting

### Playwright not found
```bash
pip install playwright
playwright install
```

### Telegram errors
Check your notification configuration in the `notifier/` directory.

### Import errors
Ensure you're running from the project root directory:
```bash
cd d:\caralyze\car_scraper
python cli/main.py --help
```

### CLI data directory issues
The CLI will automatically create the `cli/data/` directory when needed.
