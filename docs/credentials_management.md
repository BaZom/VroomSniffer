# 🔐 Mobile.de API Credentials Management Guide

This guide shows all the ways to configure and manage your mobile.de API credentials for VroomSniffer.

## 📞 Getting Mobile.de API Access

**First, you need to contact mobile.de to get API credentials:**

- **Phone**: 030 81097-500 (Business line, Monday-Friday 8:00-18:00)
- **Email**: service@team.mobile.de
- **Address**: mobile.de GmbH, Dernburgstraße 50, 14057 Berlin

**Tell them:**
- You need API access for high-volume usage (5,000-10,000+ calls/day)
- 19+ filters, every 5 minutes, ~12 hours/day
- Ask about enterprise pricing and rate limits

## 🛠️ Configuration Methods

### Method 1: Streamlit UI (Recommended for Desktop)

```bash
# Start the UI
streamlit run ui/streamlit_app.py

# Then:
# 1. Go to "🔍 Scraper" page
# 2. Expand "🔧 API Configuration" section
# 3. Enter your credentials
# 4. Click "💾 Save Credentials"
# 5. Test with "🧪 Test Connection"
```

**Benefits:**
- ✅ Secure password input (hidden)
- ✅ Automatic .env file management
- ✅ Built-in connection testing
- ✅ Real-time status updates

### Method 2: Interactive Script (Recommended for CLI)

```bash
# Setup credentials interactively
python scripts/setup_mobile_de_credentials.py setup

# Check status
python scripts/setup_mobile_de_credentials.py status

# Clear credentials
python scripts/setup_mobile_de_credentials.py clear

# Test connection
python scripts/test_mobile_de_api.py
```

### Method 3: Manual .env File

Edit `.env` file directly:

```bash
# Mobile.de API Configuration
MOBILE_DE_API_USERNAME=your_actual_username
MOBILE_DE_API_PASSWORD=your_actual_password
MOBILE_DE_API_BASE_URL=https://api.mobile.de
```

### Method 4: Environment Variables (Production)

```bash
# Option A: Export in shell
export MOBILE_DE_API_USERNAME='your_username'
export MOBILE_DE_API_PASSWORD='your_password'
export MOBILE_DE_API_BASE_URL='https://api.mobile.de'

# Option B: Docker
docker run -e MOBILE_DE_API_USERNAME='...' -e MOBILE_DE_API_PASSWORD='...' vroomsniffer

# Option C: Kubernetes secrets
kubectl create secret generic mobile-de-api \
  --from-literal=username='your_username' \
  --from-literal=password='your_password'
```

## 🚀 Usage After Configuration

### CLI Usage

```bash
# Use mobile.de API for single run
python cli/main.py run "https://mobile.de/search?make=BMW" --platform mobile.de

# Scheduled runs with mobile.de API
python cli/main.py schedule --platform mobile.de --interval 300 --runs 0

# Mix platforms
python cli/main.py run "https://ebay-kleinanzeigen.de/search" --platform scraper
python cli/main.py run "https://mobile.de/search" --platform mobile.de
```

### UI Usage

1. Start UI: `streamlit run ui/streamlit_app.py`
2. Go to "🔍 Scraper" page
3. In "Advanced Settings", select platform from dropdown
4. Configure URLs and start scraping

## 🔍 Verification & Testing

### Check Configuration Status

```bash
# Method 1: Use status script
python scripts/setup_mobile_de_credentials.py status

# Method 2: Test API connection
python scripts/test_mobile_de_api.py

# Method 3: CLI platform check
python cli/main.py run --help | grep platform
```

### Expected Output When Configured

```
📊 Current Status:
   Username: ✅ Configured
   Password: ✅ Configured  
   Base URL: https://api.mobile.de
   Status: ✅ Ready for mobile.de API
```

### Expected Output When NOT Configured

```
📊 Current Status:
   Username: ❌ Not set
   Password: ❌ Not set
   Base URL: https://api.mobile.de
   Status: ⚠️  Credentials needed
```

## 🛡️ Security Best Practices

### For Development
- ✅ Use `.env` file (already in `.gitignore`)
- ✅ Use UI or interactive script for setup
- ❌ Don't commit credentials to git

### For Production
- ✅ Use environment variables
- ✅ Use secrets management (Docker secrets, K8s secrets)
- ✅ Rotate credentials regularly
- ❌ Don't hardcode credentials in scripts

### For CI/CD
- ✅ Use pipeline secret variables
- ✅ Mask sensitive outputs in logs
- ✅ Use temporary credentials when possible

## 🔧 Troubleshooting

### Common Issues

**"Platform 'mobile.de' is not available"**
```bash
# Check if credentials are configured
python scripts/setup_mobile_de_credentials.py status

# If not configured, run setup
python scripts/setup_mobile_de_credentials.py setup
```

**"API connection failed"**
```bash
# Test connection directly
python scripts/test_mobile_de_api.py

# Check credentials are correct
# Contact mobile.de support if credentials are valid but connection fails
```

**"Credentials not found"**
```bash
# Verify .env file exists and has correct format
cat .env | grep MOBILE_DE

# Re-run setup if needed
python scripts/setup_mobile_de_credentials.py setup
```

## 📊 Platform Selection Logic

The system automatically determines platform availability:

1. **Scraper Platform**: Always available
2. **Mobile.de Platform**: Available only when credentials are configured
3. **Auto-detection**: System checks credentials on startup
4. **UI Indication**: Dropdown shows available platforms with status

### Platform Priority

```bash
# Default: Uses scraper (backward compatibility)
python cli/main.py run "url"

# Explicit scraper
python cli/main.py run "url" --platform scraper

# Mobile.de API (requires credentials)
python cli/main.py run "url" --platform mobile.de
```

## 🎯 Quick Start Checklist

- [ ] Contact mobile.de for API access (030 81097-500)
- [ ] Receive username and password from mobile.de
- [ ] Configure credentials using one of the methods above
- [ ] Test connection: `python scripts/test_mobile_de_api.py`
- [ ] Verify platform available: `python scripts/setup_mobile_de_credentials.py status`
- [ ] Test CLI: `python cli/main.py run "mobile.de-url" --platform mobile.de`
- [ ] Test UI: Select "mobile.de API" in platform dropdown

## 📝 Example Workflow

```bash
# 1. Setup credentials
python scripts/setup_mobile_de_credentials.py setup

# 2. Test connection
python scripts/test_mobile_de_api.py

# 3. Run with mobile.de API
python cli/main.py run "https://mobile.de/search?make=BMW&model=X5" --platform mobile.de

# 4. Schedule continuous runs (5-minute intervals)
python cli/main.py schedule --platform mobile.de --interval 300 --runs 0 --use-saved
```

The credentials system is designed to be flexible, secure, and easy to use across different deployment scenarios!
