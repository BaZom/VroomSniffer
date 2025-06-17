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
- **📊 JSON-based Storage**: Efficient data persistence with extensible service layer

## 🚀 Quick Start

### 1. Installation

**Clone the repository:**
```bash
git clone https://github.com/BaZom/VroomSniffer.git
cd VroomSniffer
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
streamlit run ui/pages/scraper.py
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
```

Additional CLI commands include search capabilities, sending to Telegram, and viewing version information.

### Web Interface

Launch the interactive Streamlit dashboard for advanced filtering and monitoring:

```bash
streamlit run ui/pages/scraper.py
```

**Key Features:**
- **🔄 Flexible Auto-monitoring**: Set custom intervals from 30 seconds to 1 hour
- **📲 Auto-notifications**: Automatically send new listings to Telegram  
- **🎛️ Interactive controls**: Manual monitoring with one click
- **📊 Real-time analytics**: Price trends and statistics

## Project Structure

```
car_scraper/
├── cli/                     # Command-line interface
├── ui/                      # Web interface (Streamlit)
├── providers/               # Service provider pattern implementation
├── services/                # Service layer (business logic)
├── scraper/                 # Scraping engine (Playwright)
├── storage/                 # Data persistence (JSON files)
├── notifier/                # Notification system (Telegram)
├── proxy/                   # Proxy management
├── scheduler/               # Job scheduling
├── config/                  # Configuration
├── logger/                  # Logging
└── docs/                    # Documentation
```

For a detailed breakdown of each component, see the [Architecture Documentation](./docs/architecture.md).

## Configuration

### Telegram Integration
Configure Telegram notifications for automatic car listing alerts:

1. Create a Telegram bot via @BotFather
2. Get your bot token and chat ID  
3. Configure environment variables in `.env`

### Proxy Support
Configure proxy rotation in `proxy/manager.py` for enhanced scraping reliability.

## Architecture

VroomSniffer follows a service-oriented architecture with specialized services for different concerns. The system uses the Service Provider pattern for dependency management and a clean separation between UI/CLI and business logic.

### Architecture Diagram

```
┌─────────────────────────────────┐       ┌─────────────────────┐
│            UI Layer             │       │      CLI Layer      │
│  (Streamlit Web Application)    │       │  (Command Line Tool)│
└───────────────┬─────────────────┘       └──────────┬──────────┘
                │                                     │
                ▼                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Services Provider                          │
│       (Centralized Service Factory and Dependency Manager)      │
└─────────────────────────────┬─────────────────────────────────--┘
                             │
         ┌──────────────────┬┴───────────────┬─────────────────┐
         │                  │                │                 │
         ▼                  ▼                ▼                 ▼
┌─────────────────┐  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐
│ Storage Service │  │ Scraper Service│  │Notifier Svc  │  │Statistics Svc│
└────────┬────────┘  └────────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                    │                  │                 │
         ▼                    ▼                  ▼                 ▼
┌─────────────────┐  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐
│  JSON Storage   │  │Playwright      │  │Telegram Bot  │  │Analytics     │
│  (Data Files)   │  │(Scraper Engine)│  │(Notifications│  │(Reporting)   │
└─────────────────┘  └────────────────┘  └──────────────┘  └──────────────┘
```

### Key Components

- **UI & CLI Layers**: Thin entry points with no business logic
- **Services Provider**: Centralized dependency manager
- **Service Layer**: Contains all business logic in specialized service classes
- **Infrastructure**: Storage, scraping engine, and notification systems

For detailed architecture information, see the [Architecture Documentation](./docs/architecture.md).
For guidance on adding new features, see [Feature Implementation Guide](./docs/feature_implementation_guide.md).

## Troubleshooting

- **Playwright issues**: Run `playwright install` to download browser binaries
- **Import errors**: Ensure you're in the virtual environment and all dependencies are installed
- **Scraping failures**: Check if the target website structure has changed
- **Telegram not working**: Verify bot token and chat ID in the notifier configuration

## ⚠️ Disclaimer

**This is a hobby project created for educational and personal use only.**

- **Educational Purpose**: This project is intended for learning web scraping techniques
- **Personal Use**: Use responsibly and only for personal research
- **Respect Website Terms**: Always respect website terms of service and robots.txt files

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run tests: `python -m pytest tests/`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## CLI Documentation

The VroomSniffer CLI provides a powerful command-line interface for scraping, managing listings, and sending notifications. All CLI documentation is now available in a single comprehensive document:

- [Complete CLI Documentation](./docs/cli_documentation.md) - Everything you need to know about using and extending the CLI

**Basic CLI Usage:**

```bash
# Run the scraper
python cli/main.py run "https://www.example-marketplace.com/s-autos/bmw/k0c216"

# List results
python cli/main.py list

# Search results
python cli/main.py search "320d"

# Schedule automatic scraping
python cli/main.py schedule --use-saved --random --interval 300 --notify-new
```

For more information, check the [Complete CLI Documentation](./docs/cli_documentation.md).
