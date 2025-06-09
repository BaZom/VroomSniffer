# Auto-Monitoring Guide

## 🔄 Auto-Monitoring Every 5 Minutes

The CarAlyze UI now supports fully automated car listing monitoring with auto-notifications.

### Quick Setup

1. **Open the UI**: 
   ```bash
   streamlit run ui/streamlit_app.py
   ```

2. **Configure your search**:
   - Set car make/model (e.g., BMW, Audi)
   - Set price range (e.g., €5,000 - €20,000)
   - Set year range, transmission, max mileage

3. **Enable auto-features**:
   - ✅ Check "📲 Auto-send new listings"
   - ✅ Check "🔄 Auto-run scraper every 5 minutes"

4. **Sit back and relax**:
   - The system will automatically check for new listings every 5 minutes
   - New listings are instantly sent to your Telegram
   - You'll see status updates in the UI

### How It Works

#### Auto-Monitoring Cycle:
1. **Timer Check**: Every page refresh, checks if 5 minutes have passed
2. **Auto-Scrape**: Automatically runs the scraper in the background
3. **New Listing Detection**: Compares with previous results
4. **Auto-Notification**: Sends new listings to Telegram (if enabled)
5. **Status Update**: Shows results in the UI
6. **Countdown**: Displays time until next check

#### UI Status Indicators:

**When Auto-Monitoring is ENABLED:**
```
🔄 Auto-monitoring is ENABLED - Scraper will run every 5 minutes
⏱️ Next auto-run in: 3m 24s
```

**When Auto-Monitoring is DISABLED:**
```
⏸️ Auto-monitoring is DISABLED
```

**During Auto-Run:**
```
⏰ Auto-run #3 triggered
🎉 Auto-monitoring found 2 new listings!
📱 Auto-sending 2 listings to Telegram...
✅ Auto-sent 2 listings!
```

### Manual Controls

Even with auto-monitoring enabled, you can still:

- **🔍 Run Manual Check**: Force an immediate check
- **📤 Send New Listings**: Manually send any new listings found

### Best Practices

1. **Keep the browser tab open**: The auto-monitoring works while the UI is active
2. **Stable internet connection**: Ensure consistent connectivity for Telegram
3. **Test first**: Use the test connection button to verify Telegram works
4. **Monitor rate limits**: The system includes built-in rate limiting

### Telegram Integration

The auto-monitoring works seamlessly with Telegram:

- **Individual Messages**: Each listing sent as a separate message
- **Rich Formatting**: HTML formatting with emojis and clickable links
- **Rate Limiting**: 1.5-second delays between messages
- **Error Handling**: Graceful handling of network issues

### Example Workflow

```
1. User enables auto-monitoring at 2:00 PM
2. First auto-run at 2:00 PM finds 3 new BMWs
3. 3 Telegram messages sent automatically
4. Next auto-run at 2:05 PM finds 1 new BMW
5. 1 Telegram message sent automatically
6. Next auto-run at 2:10 PM finds 0 new listings
7. No messages sent, waits until 2:15 PM
8. Process continues indefinitely...
```

### Troubleshooting

**Auto-monitoring not working?**
- Check that the checkbox is enabled
- Ensure the browser tab stays open
- Look for error messages in the UI

**No Telegram messages?**
- Verify "Auto-send new listings" is enabled
- Test Telegram connection with the test button
- Check if new listings were actually found

**Performance issues?**
- Auto-monitoring only runs when needed
- Built-in rate limiting prevents spam
- Lightweight background operations

---

🎯 **Result**: Fully automated car hunting with zero manual effort!
