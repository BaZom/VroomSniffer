# Car Scraper System

A modular scraping system to collect car listings (e.g., from eBay Kleinanzeigen), avoid duplicates, and notify users via WhatsApp.

---

## Features
- Playwright-based scraping (JavaScript-heavy sites)
- Proxy rotation support
- SQLite/PostgreSQL storage
- Deduplication to avoid repeated listings
- Optional WhatsApp alerts via Twilio
- Modular structure for easy scaling

---

## Setup (Recommended with venv)

### 1. Create and activate virtual environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

---

### 2. Install dependencies
```bash
pip install -r requirements.txt
playwright install
```

---

### 3. Run the scraper
```bash
python car_scraper/main.py
```

To run it continuously every 5 minutes:
```bash
while true; do python car_scraper/main.py; sleep 300; done
```

---

### 4. Deactivate when done
```bash
deactivate
```

---

## Folder Structure

- `scraper/engine.py` → Playwright logic
- `proxy/manager.py` → Proxy rotation
- `storage/db.py` → Save to SQLite/PostgreSQL
- `utils/deduplication.py` → Detect repeated listings
- `notifier/whatsapp.py` → Optional messaging
- `scheduler/job.py` → Time-based trigger
- `main.py` → Entry point
- `config.py` → Environment settings

---

## Future Enhancements (Planned or Optional)

- Add mock/test data to the DB
- Prepare a logging output file
- Implement full deduplication logic
- Add real Twilio notification logic
- Build dashboard for viewing listings

---


---

## Optional: Command-Line Interface (CLI)

You can use the CLI to manually interact with your listings database and control WhatsApp messages.

### Example Usage

```bash
# List the 10 most recent listings
python cli.py list

# Search listings for a keyword (e.g. BMW)
python cli.py search bmw

# Send listing with ID 5 via WhatsApp
python cli.py send 5
```

This is useful for manual testing or when you want to review/send listings yourself.
