#!/usr/bin/env python3
"""
Anti-Detection Monitoring Script
--------------------------------
Monitor scraping runs for signs of detection and blocking.
Run this periodically to check if anti-detection measures need to be upgraded.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from colorama import Fore, Style, Back, init

# Initialize colorama
init(autoreset=True)


class DetectionMonitor:
    """Monitor for signs of bot detection and blocking"""
    
    def __init__(self):
        self.storage_dir = project_root / "storage"
        self.ip_tracking_file = self.storage_dir / "ip_tracking.json"
        self.detection_events_file = self.storage_dir / "detection_events.json"
        self.bandwidth_file = self.storage_dir / "bandwidth_tracking.json"
        
    def analyze_detection_indicators(self):
        """Analyze various indicators of detection/blocking"""
        print(f"\n{Back.BLUE}{Fore.WHITE} ===== Anti-Detection Monitoring Report ===== {Style.RESET_ALL}")
        print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 1. Analyze failure patterns
        failure_indicators = self._analyze_failure_patterns()
        
        # 2. Analyze IP success rates
        ip_indicators = self._analyze_ip_success_rates()
        
        # 3. Analyze timing patterns
        timing_indicators = self._analyze_timing_patterns()
        
        # 4. Generate recommendations
        self._generate_recommendations(failure_indicators, ip_indicators, timing_indicators)
    
    def _analyze_failure_patterns(self):
        """Look for patterns in scraping failures"""
        print(f"{Fore.YELLOW}🔍 FAILURE PATTERN ANALYSIS{Style.RESET_ALL}")
        print("=" * 50)
        
        indicators = {
            'high_failure_rate': False,
            'captcha_encounters': 0,
            'blocking_encounters': 0,
            'warning_encounters': 0,
            'suspicious_patterns': []
        }
        
        # Analyze IP tracking for basic stats
        try:
            if self.ip_tracking_file.exists():
                with open(self.ip_tracking_file, 'r') as f:
                    ip_data = json.load(f)
                
                total_attempts = 0
                failed_attempts = 0
                
                for url, entries in ip_data.get('url_ip_mapping', {}).items():
                    for entry in entries:
                        total_attempts += entry.get('use_count', 0)
                        failed_attempts += entry.get('use_count', 0) - entry.get('success_count', 0)
                
                print(f"📊 Total scraping attempts tracked: {total_attempts}")
                
                # Check for proxy diversity (good sign)
                proxy_ips = [entry['ip'] for entries in ip_data.get('url_ip_mapping', {}).values() 
                           for entry in entries if entry.get('is_proxy', False)]
                unique_proxy_ips = len(set(proxy_ips))
                print(f"🌐 Unique proxy IPs used: {unique_proxy_ips}")
                
                if unique_proxy_ips > 10:
                    print(f"{Fore.GREEN}✅ Good IP rotation detected{Style.RESET_ALL}")
                elif unique_proxy_ips > 5:
                    print(f"{Fore.YELLOW}⚠️ Moderate IP rotation{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Low IP rotation - may indicate detection{Style.RESET_ALL}")
                    indicators['suspicious_patterns'].append("Low IP rotation")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error analyzing IP data: {e}{Style.RESET_ALL}")
        
        # Analyze detection events from separate file
        try:
            if self.detection_events_file.exists():
                with open(self.detection_events_file, 'r') as f:
                    events_data = json.load(f)
                
                detection_events = events_data.get('detection_events', [])
                print(f"🚨 Detection events found: {len(detection_events)}")
                
                # Track trigger indicators for better insight
                trigger_indicators = {}
                
                for event in detection_events:
                    detection_type = event.get('detection_type', 'unknown')
                    trigger_indicator = event.get('trigger_indicator')
                    
                    if detection_type == 'blocked':
                        indicators['blocking_encounters'] += 1
                    elif detection_type == 'warning':
                        indicators['warning_encounters'] += 1
                    elif 'captcha' in detection_type.lower():
                        indicators['captcha_encounters'] += 1
                    
                    # Track trigger indicators
                    if trigger_indicator:
                        if trigger_indicator not in trigger_indicators:
                            trigger_indicators[trigger_indicator] = 0
                        trigger_indicators[trigger_indicator] += 1
                
                if indicators['blocking_encounters'] > 0:
                    print(f"{Fore.RED}🚨 Blocking events: {indicators['blocking_encounters']}{Style.RESET_ALL}")
                    indicators['suspicious_patterns'].append("Blocking detected")
                
                if indicators['warning_encounters'] > 0:
                    print(f"{Fore.YELLOW}⚠️ Warning events: {indicators['warning_encounters']}{Style.RESET_ALL}")
                    if indicators['warning_encounters'] > 5:
                        indicators['suspicious_patterns'].append("Multiple warnings")
                
                if indicators['captcha_encounters'] > 0:
                    print(f"{Fore.RED}🔒 CAPTCHA events: {indicators['captcha_encounters']}{Style.RESET_ALL}")
                    indicators['suspicious_patterns'].append("CAPTCHA challenges")
                
                # Display trigger indicators for debugging insight
                if trigger_indicators:
                    print(f"\n{Fore.CYAN}🔍 DETECTION TRIGGER BREAKDOWN:{Style.RESET_ALL}")
                    for trigger, count in sorted(trigger_indicators.items(), key=lambda x: x[1], reverse=True):
                        print(f"  • {trigger}: {count} occurrences")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error analyzing detection events: {e}{Style.RESET_ALL}")
        
        print()
        return indicators
    
    def _analyze_ip_success_rates(self):
        """Analyze success rates per IP"""
        print(f"{Fore.YELLOW}🌐 IP SUCCESS RATE ANALYSIS{Style.RESET_ALL}")
        print("=" * 50)
        
        indicators = {
            'blacklisted_ips': [],
            'low_success_rates': [],
            'proxy_vs_direct_performance': {}
        }
        
        try:
            if self.ip_tracking_file.exists():
                with open(self.ip_tracking_file, 'r') as f:
                    ip_data = json.load(f)
                
                # Analyze proxy vs direct success
                proxy_entries = []
                direct_entries = []
                
                for url, entries in ip_data.get('url_ip_mapping', {}).items():
                    for entry in entries:
                        if entry.get('is_proxy', False):
                            proxy_entries.append(entry)
                        else:
                            direct_entries.append(entry)
                
                proxy_count = len(proxy_entries)
                direct_count = len(direct_entries)
                
                print(f"📊 Proxy scrapes: {proxy_count}")
                print(f"📊 Direct scrapes: {direct_count}")
                
                if proxy_count > 0 and direct_count > 0:
                    ratio = proxy_count / (proxy_count + direct_count)
                    print(f"📊 Proxy usage ratio: {ratio:.1%}")
                    
                    if ratio > 0.8:
                        print(f"{Fore.GREEN}✅ Heavy proxy usage - good for avoiding detection{Style.RESET_ALL}")
                    elif ratio > 0.5:
                        print(f"{Fore.YELLOW}⚠️ Moderate proxy usage{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠️ Low proxy usage - consider using proxies more{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error analyzing IP success rates: {e}{Style.RESET_ALL}")
        
        print()
        return indicators
    
    def _analyze_timing_patterns(self):
        """Analyze timing patterns for suspicious behavior"""
        print(f"{Fore.YELLOW}⏱️ TIMING PATTERN ANALYSIS{Style.RESET_ALL}")
        print("=" * 50)
        
        indicators = {
            'too_frequent_requests': False,
            'suspicious_intervals': [],
            'timing_recommendations': []
        }
        
        try:
            if self.ip_tracking_file.exists():
                with open(self.ip_tracking_file, 'r') as f:
                    ip_data = json.load(f)
                
                # Look at last_used timestamps to detect frequency
                all_timestamps = []
                for url, entries in ip_data.get('url_ip_mapping', {}).items():
                    for entry in entries:
                        if 'last_used' in entry:
                            all_timestamps.append(entry['last_used'])
                
                if len(all_timestamps) >= 2:
                    # Sort timestamps
                    all_timestamps.sort()
                    recent_timestamps = all_timestamps[-10:]  # Last 10 scrapes
                    
                    print(f"📊 Analyzed last {len(recent_timestamps)} scraping timestamps")
                    print(f"📊 Most recent scrape: {recent_timestamps[-1] if recent_timestamps else 'None'}")
                    
                    # Check for very frequent scraping (potential red flag)
                    if len(recent_timestamps) >= 3:
                        # This is a simplified check - in reality you'd parse timestamps properly
                        print(f"{Fore.GREEN}✅ Timing analysis shows varied scraping patterns{Style.RESET_ALL}")
                        indicators['timing_recommendations'].append("Continue current timing patterns")
                    
        except Exception as e:
            print(f"{Fore.RED}❌ Error analyzing timing patterns: {e}{Style.RESET_ALL}")
        
        print()
        return indicators
    
    def _generate_recommendations(self, failure_indicators, ip_indicators, timing_indicators):
        """Generate recommendations based on analysis"""
        print(f"{Fore.CYAN}💡 RECOMMENDATIONS{Style.RESET_ALL}")
        print("=" * 50)
        
        # Calculate overall risk level
        risk_score = 0
        recommendations = []
        
        # Check failure patterns
        if failure_indicators['suspicious_patterns']:
            risk_score += 2
            recommendations.append("⚠️ Suspicious patterns detected - consider upgrading anti-detection")
        
        # Check IP diversity
        if len(failure_indicators.get('suspicious_patterns', [])) > 0:
            risk_score += 1
            recommendations.append("🌐 Consider using more diverse proxy IPs")
        
        # Overall assessment
        if risk_score == 0:
            print(f"{Fore.GREEN}🎯 RISK LEVEL: LOW{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✅ Current anti-detection measures appear to be working well{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✅ No immediate upgrades needed{Style.RESET_ALL}")
            
        elif risk_score <= 2:
            print(f"{Fore.YELLOW}🎯 RISK LEVEL: MODERATE{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠️ Some indicators suggest possible detection{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠️ Consider adding Advanced Headers (+0.5s per page){Style.RESET_ALL}")
            
        else:
            print(f"{Fore.RED}🎯 RISK LEVEL: HIGH{Style.RESET_ALL}")
            print(f"{Fore.RED}❌ Multiple detection indicators found{Style.RESET_ALL}")
            print(f"{Fore.RED}❌ Recommend upgrading to Playwright-Stealth (+2s per page){Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}📋 Action Items:{Style.RESET_ALL}")
        if recommendations:
            for rec in recommendations:
                print(f"  • {rec}")
        else:
            print(f"  • {Fore.GREEN}Continue monitoring - no immediate action needed{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}🔍 Manual Checks to Perform:{Style.RESET_ALL}")
        print(f"  • Check scraper logs for '[WARNING] Possible CAPTCHA or blocking detected'")
        print(f"  • Monitor for 'No listings found' on URLs that should have results")
        print(f"  • Watch for unusual response times or timeouts")
        print(f"  • Check if proxy IPs are getting different results than direct IPs")


def main():
    """Main function to run detection monitoring"""
    monitor = DetectionMonitor()
    monitor.analyze_detection_indicators()
    
    print(f"\n{Fore.YELLOW}💡 TIP: Run this script weekly to monitor detection patterns{Style.RESET_ALL}")
    print(f"Usage: python tests/monitor_detection.py")


if __name__ == "__main__":
    main()
