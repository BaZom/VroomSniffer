# 🚨 Detection Monitoring Quick Reference

## Quick Commands

```bash
# Monitor detection health
python tests/monitor_detection.py

# View file structure  
python tests/show_file_structure.py

# Test IP rotation manually
python tests/test_ip_rotation.py
```

## Detection Types

| Type | Severity | Action |
|------|----------|--------|
| `normal` | ✅ Good | Continue monitoring |
| `warning` | ⚠️ Watch | Investigate patterns |
| `blocked` | 🚨 High | Upgrade anti-detection |
| `content_blocked` | 🛑 Critical | Change strategy |

## Risk Levels

- **🟢 LOW**: Normal operation
- **🟡 MEDIUM**: Monitor closely
- **🔴 HIGH**: Take action immediately  
- **⚫ CRITICAL**: Major detection

## File Structure

```
storage/
├── ip_tracking.json      # Clean IP/URL data
├── detection_events.json # Security events
└── bandwidth_tracking.json
```

## Quick Health Check

1. **Check recent events**: Look at `detection_events.json`
2. **Run monitoring**: `python tests/monitor_detection.py`
3. **Review risk level**: Act on HIGH/CRITICAL warnings
4. **Check IP rotation**: Ensure diverse proxy usage

## Emergency Response

### If HIGH Risk:
1. Review recent detection events
2. Check for patterns in specific URLs/IPs
3. Consider increasing delays
4. Monitor more frequently

### If CRITICAL Risk:
1. Stop scraping temporarily
2. Review all recent events
3. Upgrade anti-detection measures
4. Change proxy strategy if needed

---
**For full documentation**: `docs/detection_monitoring_guide.md`
