# 🚗 Caralyze - Car Scraper System

A modern, modular web scraping system designed to collect car listings from eBay Kleinanzeigen, detect new listings, and send notifications via Telegram. Built with Python, Playwright, and Streamlit.

## ✨ Key Features

- **🎭 Modern Web Scraping**: Playwright-based engine handles JavaScript-heavy sites
- **🔄 Smart Deduplication**: Automatically detects and filters out duplicate listings
- **📱 Telegram Notifications**: Get instant alerts for new car listings with rich formatting
- **🚀 Auto-Notifications**: Automatically send new listings as they're discovered
- **🌐 Web Dashboard**: Interactive Streamlit interface with real-time monitoring
- **⚡ CLI Interface**: Command-line tools for automation and scripting
- **🔧 Modular Architecture**: Clean separation of concerns for easy maintenance
- **📊 Multiple Storage Options**: SQLite for development, PostgreSQL for production

## 🚀 Quick Start

### 1. Installation

**Clone the repository:**
```bash
git clone <your-repository-url>
cd car_scraper
```

**Create virtual environment:**
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS  
python3 -m venv venv
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
playwright install
```

### 2. First Run

**Test the scraper:**
```bash
python cli/main.py run "https://www.kleinanzeigen.de/s-autos/bmw/k0c216"
```

**View results:**
```bash
python cli/main.py list
```

**Launch web interface:**
```bash
streamlit run ui/streamlit_app.py
```

## 📋 Usage

### Command Line Interface

The CLI provides the primary interface for running the scraper and managing results:

```bash
# Run the scraper with a Kleinanzeigen search URL
python cli/main.py run "https://www.kleinanzeigen.de/s-autos/bmw/k0c216"

# Run with auto-notifications (sends new listings automatically)
python scraper/ebay_kleinanzeigen_engine.py --url "..." --notify --notify-count 3

# List the latest scraped listings
python cli/main.py list

# Search listings for specific keywords
python cli/main.py search "bmw x5"
python cli/main.py search "automatic"

# Send a listing via Telegram (use index from list command)
python cli/main.py send 3

# Send top 5 listings via Telegram
python cli/main.py send-top 5

# Send summary notification
python cli/main.py notify

# Show version information
python cli/main.py version

# Get help for any command
python cli/main.py --help
```

### Web Interface

Launch the interactive Streamlit dashboard for advanced filtering and monitoring:

```bash
streamlit run ui/streamlit_app.py
```

**Key Features:**
- **🔄 Auto-monitoring**: Enable automatic scraping every 5 minutes
- **📲 Auto-notifications**: Automatically send new listings to Telegram  
- **🎛️ Interactive controls**: Manual monitoring with one click
- **📊 Real-time analytics**: Price trends and statistics
- **🔍 Advanced filtering**: Car make/model, price, year, transmission, mileage

**Auto-Monitoring Setup:**
1. Configure your search filters (car make, price range, etc.)
2. ✅ Check "🔄 Auto-run scraper every 5 minutes" 
3. ✅ Check "📲 Auto-send new listings" (optional)
4. The system will automatically check for new listings every 5 minutes
5. New listings are instantly sent to your Telegram

The web interface provides:
- Real-time listing monitoring
- **🔄 Auto-monitoring every 5 minutes** (new!)
- **📲 Auto-send new listings to Telegram** (new!)
- Advanced filtering options
- Price analysis and trends
- Visual data exploration
- Telegram integration

## Project Structure

```
car_scraper/
├── README.md
├── requirements.txt
├── cli/                     # Command-line interface
│   ├── main.py             # Main CLI application
│   ├── README.md           # CLI documentation
│   └── data/               # CLI-specific data storage
├── ui/                     # Web interface
│   └── streamlit_app.py    # Streamlit web app
├── scraper/                # Scraping engine
│   └── ebay_kleinanzeigen_engine.py
├── services/               # Business logic layer
│   └── caralyze_service.py
├── storage/                # Data persistence
│   ├── db.py              # Database operations
│   └── listings/          # JSON data storage
├── notifier/              # Notification system
│   └── telegram.py        # Telegram integration
├── proxy/                 # Proxy management
│   └── manager.py
├── utils/                 # Utilities
│   └── deduplication.py
├── scheduler/             # Job scheduling
│   └── job.py
├── config/                # Configuration
│   └── car_models.py
├── logger/                # Logging
│   └── logging_config.py
└── tests/                 # Test suite
    ├── test_end_to_end.py
    └── test_service_layer.py
```

### Core Components
- `cli/` → **Command-line interface** (organized in dedicated folder)
  - `cli/main.py` → Main CLI application
  - `cli/data/` → CLI-specific data storage
- `ui/` → **Web interface** (Streamlit app)
- `scraper/` → **Scraping engine** (Playwright logic)
- `services/` → **Business logic** (service layer)
- `storage/` → **Data persistence** (SQLite/PostgreSQL)
- `notifier/` → **Notifications** (Telegram messaging)

### Supporting Components
- `proxy/manager.py` → Proxy rotation
- `utils/deduplication.py` → Detect repeated listings
- `scheduler/job.py` → Time-based trigger
- `config/` → Configuration settings
- `tests/` → Test suite
- `logger/` → Logging configuration

---

## Configuration

### Telegram Integration
Configure Telegram notifications for automatic car listing alerts:

**Setup Steps:**
1. Create a Telegram bot via @BotFather
2. Get your bot token and chat ID  
3. Configure environment variables in `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   TELEGRAM_TEST_MODE=false  # Set to true for testing
   ```

**Auto-Notification Features:**
- **🚀 Streamlit UI**: Toggle "Auto-send new listings" in sidebar for real-time notifications
- **⚡ CLI Scraper**: Use `--notify` flag to auto-send listings after scraping
- **📱 Rich Formatting**: HTML messages with emojis, clickable links, and structured layout
- **🛡️ Rate Limiting**: Smart delays prevent spam and API limits
- **🔧 Test Mode**: Corporate-friendly mode for networks that block Telegram

### Proxy Support
Configure proxy rotation in `proxy/manager.py` for enhanced scraping reliability.

### Database Storage
- **SQLite**: Default lightweight option (configured in `storage/db.py`)
- **PostgreSQL**: Production-ready option for larger deployments

---

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Project Architecture
The project follows a clean, modular architecture with separation of concerns:
- **CLI**: User interface and command handling
- **Scraper**: Web scraping logic using Playwright
- **Services**: Business logic and data processing
- **Storage**: Data persistence and management
- **UI**: Web-based dashboard and visualization
- **Utils**: Shared utilities and helpers

---

## Troubleshooting

- **Playwright issues**: Run `playwright install` to download browser binaries
- **Import errors**: Ensure you're in the virtual environment and all dependencies are installed
- **Scraping failures**: Check if the target website structure has changed
- **Telegram not working**: Verify bot token and chat ID in the notifier configuration

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run tests: `python -m pytest tests/`
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
