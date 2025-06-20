# 🚗 VroomSniffer - Car Monitoring System

<div align="center">
  <img src="ui/resources/logo3.jpg" alt="VroomSniffer Logo" width="300">
</div>

> **📝 Note: This is a hobby project created for educational and personal use only.**

A modern, service-oriented web scraping system designed to collect car listings from various online marketplaces, detect new listings, and send notifications via Telegram. Built with Python, Playwright, and Streamlit.

## 📋 Table of Contents

1. [Key Features](#-key-features)
2. [Quick Start](#-quick-start)
3. [Configuration](#configuration)
4. [Usage](#-usage)
   - [Command Line Interface](#command-line-interface)
   - [Web Interface](#web-interface)
5. [Documentation](#documentation)
6. [Architecture](#architecture)
7. [Project Structure](#project-structure)
8. [Troubleshooting](#troubleshooting)
9. [Disclaimer](#-disclaimer)
10. [Contributing](#contributing)
11. [License](#license)

## ✨ Key Features

- **🎭 Modern Web Scraping**: Playwright-based engine handles JavaScript-heavy sites
- **🔄 Smart Deduplication**: Automatically detects and filters out duplicate listings
- **📱 Telegram Notifications**: Get instant alerts for new car listings with rich formatting
- **⏱️ Flexible Scheduling**: Configure custom intervals for automatic scraping
- **🚀 Auto-Notifications**: Automatically send new listings as they're discovered
- **🌐 Web Dashboard**: Interactive Streamlit interface with real-time monitoring
- **⚡ CLI Interface**: Command-line tools for automation and scripting
- **🔧 Service-Oriented Architecture**: Clean separation of concerns with specialized services
- **🌍 Proxy Support**: WebShare rotating residential proxy integration to avoid blocking
- **📊 IP Tracking**: Track and monitor which IPs are used to access each URL
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
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw"
```

**View results:**
```bash
python cli/main.py list
```

**Launch web interface:**
```bash
streamlit run ui/pages/scraper.py
```

## Configuration

VroomSniffer uses environment variables for configuration. An example file `.env.proxy.example` is provided with settings for both Telegram notifications and proxy configuration.

1. **Copy the example file**:
   ```bash
   cp .env.proxy.example .env
   ```

2. **Edit the .env file** with your specific settings:
   - For Telegram notifications, set your bot token and chat ID
   - For proxy support, configure your WebShare credentials

3. **Test your setup**:
   ```bash
   # Test Telegram notifications
   python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --notify-new
   
   # Test proxy functionality
   python scripts/verify_proxy.py
   ```

For detailed instructions on configuration:
- [IP Tracking Guide](./docs/ip_tracking_guide.md)
- [Proxy Guide](./docs/proxy_guide.md)

## 📋 Usage

### Command Line Interface

The CLI provides a powerful interface for running the scraper and managing results.

#### Essential Commands

```bash
# Run the scraper on a marketplace URL
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw"

# View the latest results (first 10 by default)
python cli/main.py list

# Search for specific listings
python cli/main.py search "diesel automatic"

# Send selected listings to Telegram
python cli/main.py send 1 3 5
```

#### Automation & Scheduling

```bash
# Schedule periodic scraping (every 5 minutes, 10 runs)
python cli/main.py schedule "https://www.example-marketplace.com/cars/search?brand=bmw" --interval 300 --runs 10

# Continuous monitoring with saved URLs (until manually stopped)
python cli/main.py schedule --use-saved --random --runs 0 --interval 300
```

#### Proxy & Notification Features

```bash
# Run with notifications for new listings
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --notify-new

# Run with proxy support to avoid IP blocking
python cli/main.py run "https://www.example-marketplace.com/cars/search?brand=bmw" --use-proxy --proxy-type WEBSHARE_RESIDENTIAL

# View IP tracking information
python cli/main.py diagnostics --show-ip-tracking
```

For comprehensive CLI documentation, see [CLI Documentation](./docs/cli_documentation.md).

### Web Interface

The Streamlit dashboard provides an interactive interface for monitoring and managing car listings.

#### Starting the UI

```bash
streamlit run ui/streamlit_app.py
```

#### Key UI Features

- **🔍 URL Management**: Add, save, and organize marketplace URLs
- **🔄 Interactive Monitoring**: Run manual scans or set up automatic monitoring
- **⚙️ Scraper Controls**: Run immediately or schedule automatic monitoring
- **⏱️ Flexible Scheduling**: Set custom intervals from 30 seconds to 1 hour
- **📱 Notification Settings**: Configure Telegram notifications
- **📲 Auto-notifications**: Automatically send new listings to Telegram
- **🌐 Proxy Configuration**: Set up and test WebShare residential proxies
- **📊 Results View**: Browse and filter car listings with detailed information
- **📈 Statistics**: Track prices and listing counts over time
- **🛠️ IP Monitoring**: View and analyze IP usage for each URL
- **📊 Data Visualization**: View price trends and statistics
- **🧪 Playground**: Test specific features and functionalities

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

## Architecture

VroomSniffer follows a service-oriented architecture with specialized services for different concerns.

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

- **UI & CLI Layers**: Thin entry points with minimal business logic
- **Services Provider**: Centralized dependency injection system
- **Service Layer**: Contains all business logic in specialized service classes:
  - **ScraperService**: Handles web scraping operations
  - **StorageService**: Manages data persistence and retrieval
  - **NotificationService**: Handles Telegram notifications
  - **SchedulerService**: Manages timing and scheduling
  - **StatisticsService**: Provides analytics and reporting
- **Infrastructure**: Storage, scraping engine, and notification systems

## Documentation

VroomSniffer includes comprehensive documentation to help you understand and extend the system:

- [CLI Documentation](./docs/cli_documentation.md) - Complete command reference with all options
- [Architecture Documentation](./docs/architecture.md) - Detailed system design and component interactions
- [Feature Implementation Guide](./docs/feature_implementation_guide.md) - Guide for adding new features
- [IP Tracking Guide](./docs/ip_tracking_guide.md) - Information about IP tracking capabilities
- [Proxy Guide](./docs/proxy_guide.md) - Guide for using proxies with VroomSniffer

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
