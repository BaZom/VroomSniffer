# 🚗 VroomSniffer - Car Monitoring System

<div align="center">
  <img src="ui/resources/logo3.jpg" alt="VroomSniffer Logo" width="300">
</div>

> **📝 Note: This is a hobby project created for educational and personal use only.**

A modern, service-oriented web scraping system designed to collect car listings from various online marketplaces, detect new listings, and send notifications via Telegram. Built with Python, Playwright, and Streamlit.

## ✨ Key Features

- **🎭 Modern Web Scraping**: Playwright-based engine handles JavaScript-heavy sites
- **🔄 Smart Deduplication**: Automatically detects and filters out duplicate listings
- **📱 Telegram Notifications**: Get instant alerts for new car listings with rich formatting
- **⏱️ Flexible Scheduling**: Configure custom intervals for automatic scraping
- **🚀 Auto-Notifications**: Automatically send new listings as they're discovered
- **🌐 Web Dashboard**: Interactive Streamlit interface with real-time monitoring
- **⚡ CLI Interface**: Command-line tools for automation and scripting
- **🔧 Service-Oriented Architecture**: Clean separation of concerns with specialized services
- **📊 Multiple Storage Options**: JSON-based storage with extensible service layer

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
python cli/main.py run "https://www.example-marketplace.com/s-autos/bmw/k0c216"
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
# Run the scraper with a marketplace search URL
python cli/main.py run "https://marketplace-url.com/search-cars"

# Run with auto-notifications (sends new listings automatically)
python cli/main.py run "https://marketplace-url.com/search-cars" --notify --notify-count 3

# Schedule periodic scraping (every 60 seconds for 10 runs)
python cli/main.py schedule "https://marketplace-url.com/search-cars" --interval 60 --runs 10 --notify

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
- **🔄 Flexible Auto-monitoring**: Set custom intervals from 30 seconds to 1 hour
- **📲 Auto-notifications**: Automatically send new listings to Telegram  
- **🎛️ Interactive controls**: Manual monitoring with one click
- **📊 Real-time analytics**: Price trends and statistics
- **🔍 Advanced filtering**: Car make/model, price, year, transmission, mileage
- **🧠 Smart URL Pool**: Manage multiple search URLs with automatic rotation

**Auto-Monitoring Setup:**
1. Configure your search filters or add search URLs to the pool
2. ✅ Set your desired interval (30s to 1h)
3. ✅ Click "Start Scraper" to begin automatic monitoring
4. ✅ Enable "Auto-send new listings" for Telegram notifications (optional)
5. New listings are instantly sent to your Telegram

The web interface provides:
- Real-time listing monitoring with progress visualization
- **🔄 Configurable auto-monitoring intervals**
- **🔁 URL pool management for multiple search queries**
- **📲 Auto-send new listings to Telegram**
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
├── ui/                     # Web interface
│   ├── streamlit_app.py    # Streamlit web app
│   ├── components/         # UI component modules
│   │   ├── error_handling.py
│   │   ├── metrics.py
│   │   ├── navigation.py
│   │   ├── scraper_controls.py
│   │   ├── sound_effects.py
│   │   ├── state_management.py
│   │   ├── styles.py
│   │   ├── telegram_controls.py
│   │   ├── ui_components.py
│   │   └── url_management.py
│   ├── pages/              # Page components for the UI
│   │   ├── scraper.py      # Main scraper page
│   │   ├── home.py         # Home page
│   │   ├── data_storage.py # Data management page
│   │   └── playground.py   # Testing/playground page
│   └── resources/          # UI resources (images, sounds)
├── providers/              # Service provider pattern implementation
│   └── services_provider.py # Centralized service factory/singleton manager
├── scraper/                # Scraping engine
│   └── engine.py           # Main scraping engine
├── services/               # Service layer (business logic)
│   ├── storage_service.py       # Data storage operations
│   ├── url_pool_service.py      # URL management
│   ├── statistics_service.py    # Analytics and statistics
│   ├── notification_service.py  # Notification handling
│   ├── scraper_service.py       # Scraper operations
│   └── scheduler_service.py     # Scheduling and timing
├── storage/                # Data persistence
│   ├── db.py              # Database operations
│   ├── latest_results.json      # Latest scraping results
│   ├── latest_new_results.json  # New listings from last run
│   └── all_old_results.json     # Historical listings cache
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
└── logger/                # Logging
    └── logging_config.py
```

### Core Components
- `cli/` → **Command-line interface** with both ad-hoc and scheduled scraping
- `ui/` → **Web interface** with real-time monitoring and URL pool management
- `providers/` → **Service provider** implementation for dependency management
- `scraper/` → **Scraping engine** using Playwright for JavaScript-heavy sites
- `services/` → **Service layer** with specialized services for each concern
- `storage/` → **Centralized data storage** using JSON files
- `notifier/` → **Notifications** via Telegram

### Service Layer Architecture
- `providers/services_provider.py` → Centralized service factory/singleton manager
- `services/storage_service.py` → Handling data persistence and retrieval
- `services/url_pool_service.py` → Managing search URLs and URL pools
- `services/statistics_service.py` → Generating analytics and statistics
- `services/notification_service.py` → Managing notification delivery
- `services/scraper_service.py` → Coordinating scraping operations
- `services/scheduler_service.py` → Managing timed scraping jobs
- `scheduler_service.py` → Managing timing and scheduling

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

## ⚠️ Disclaimer

**This is a hobby project created for educational and personal use only.**

- **Educational Purpose**: This project is intended for learning web scraping techniques and automation concepts
- **Personal Use**: Use this tool responsibly and only for personal research and learning
- **Respect Website Terms**: Always respect website terms of service and robots.txt files
- **Rate Limiting**: Implement appropriate delays and respect server resources
- **No Commercial Use**: This project is not intended for commercial or large-scale scraping operations
- **User Responsibility**: Users are responsible for ensuring their usage complies with applicable laws and regulations

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

## Architecture

### Service Provider Pattern

This project uses the Service Provider pattern to manage service dependencies. The pattern is implemented in `providers/services_provider.py` and provides a centralized mechanism for accessing service instances throughout the application.

Key benefits:
- **Singleton services**: Only one instance of each service exists
- **Lazy initialization**: Services are only created when needed
- **Automatic dependency injection**: Services can depend on other services
- **Consistent state**: Both UI and CLI use the same service instances

Example usage:
```python
from providers.services_provider import get_storage_service, get_scraper_service

# Get service instances
storage_service = get_storage_service()
scraper_service = get_scraper_service()

# Use services
listings = storage_service.get_all_cached_listings(path)
scraper_service.run_scraper(filters)
```
