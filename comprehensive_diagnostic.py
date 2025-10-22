#!/usr/bin/env python3
"""
Comprehensive diagnostic to check why the bot is still spamming alerts
"""
import os
import sys
from datetime import datetime
from config import (
    TELEGRAM_ENABLED, TELEGRAM_SEND_EXTREME, TELEGRAM_SEND_HIGH, 
    TELEGRAM_SEND_MEDIUM, TELEGRAM_SEND_LOW, ALERT_COOLDOWN_HOURS,
    MIN_24H_VOLUME_USDT, MIN_MARKET_CAP_USDT, PRICE_SPIKE_THRESHOLD,
    VOLUME_SPIKE_THRESHOLD
)

def run_diagnostic():
    """Run comprehensive diagnostic"""
    print("🔍 COMPREHENSIVE DIAGNOSTIC")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    print(f"   TELEGRAM_BOT_TOKEN: {'✅ Set' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌ Missing'}")
    print(f"   TELEGRAM_CHAT_ID: {'✅ Set' if os.getenv('TELEGRAM_CHAT_ID') else '❌ Missing'}")
    
    # Check configuration
    print("\n⚙️ Configuration Settings:")
    print(f"   TELEGRAM_ENABLED: {TELEGRAM_ENABLED}")
    print(f"   TELEGRAM_SEND_EXTREME: {TELEGRAM_SEND_EXTREME}")
    print(f"   TELEGRAM_SEND_HIGH: {TELEGRAM_SEND_HIGH}")
    print(f"   TELEGRAM_SEND_MEDIUM: {TELEGRAM_SEND_MEDIUM}")
    print(f"   TELEGRAM_SEND_LOW: {TELEGRAM_SEND_LOW}")
    print(f"   ALERT_COOLDOWN_HOURS: {ALERT_COOLDOWN_HOURS}")
    print(f"   MIN_24H_VOLUME_USDT: {MIN_24H_VOLUME_USDT:,}")
    print(f"   MIN_MARKET_CAP_USDT: {MIN_MARKET_CAP_USDT:,}")
    print(f"   PRICE_SPIKE_THRESHOLD: {PRICE_SPIKE_THRESHOLD*100:.1f}%")
    print(f"   VOLUME_SPIKE_THRESHOLD: {VOLUME_SPIKE_THRESHOLD:.1f}x")
    
    # Check if low severity is properly blocked
    print(f"\n🚨 Severity Filtering:")
    if TELEGRAM_SEND_LOW:
        print("   ❌ PROBLEM: Low severity alerts are ENABLED!")
        print("   🔧 This is why you're getting spam alerts")
    else:
        print("   ✅ GOOD: Low severity alerts are BLOCKED")
    
    # Check cooldown settings
    print(f"\n⏰ Cooldown Settings:")
    if ALERT_COOLDOWN_HOURS >= 24:
        print("   ✅ GOOD: 24-hour cooldown is set")
    else:
        print(f"   ❌ PROBLEM: Cooldown is only {ALERT_COOLDOWN_HOURS} hours")
    
    # Test anomaly detector
    print(f"\n🧪 Testing Anomaly Detector:")
    try:
        from anomaly_detector import AnomalyDetector, AnomalyAlert
        
        detector = AnomalyDetector()
        
        # Test low severity alert
        low_alert = AnomalyAlert(
            symbol="TESTUSDT",
            alert_type="price_spike",
            severity="low",
            value=100.0,
            threshold=3.0,
            percentage_change=5.0,
            timestamp=datetime.now(),
            description="Test low alert"
        )
        
        should_send_low = detector._should_send_alert(low_alert)
        print(f"   Low severity alert would be sent: {should_send_low}")
        
        # Test medium severity alert
        medium_alert = AnomalyAlert(
            symbol="TESTUSDT",
            alert_type="price_spike",
            severity="medium",
            value=100.0,
            threshold=3.0,
            percentage_change=5.0,
            timestamp=datetime.now(),
            description="Test medium alert"
        )
        
        should_send_medium = detector._should_send_alert(medium_alert)
        print(f"   Medium severity alert would be sent: {should_send_medium}")
        
        # Test cooldown
        detector._update_cooldown("COAIUSDT")
        in_cooldown = detector._is_in_cooldown("COAIUSDT")
        print(f"   Cooldown working: {in_cooldown}")
        
    except Exception as e:
        print(f"   ❌ Error testing anomaly detector: {e}")
    
    # Check if we're running the right version
    print(f"\n📁 File Check:")
    config_file = "config.py"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            content = f.read()
            if "TELEGRAM_SEND_LOW = False" in content:
                print("   ✅ config.py has correct TELEGRAM_SEND_LOW = False")
            else:
                print("   ❌ config.py does NOT have TELEGRAM_SEND_LOW = False")
                print("   🔧 This is likely the problem!")
    else:
        print("   ❌ config.py not found")
    
    print(f"\n🎯 DIAGNOSIS:")
    if TELEGRAM_SEND_LOW:
        print("   🚨 MAIN ISSUE: Low severity alerts are still enabled!")
        print("   🔧 SOLUTION: Need to fix config.py")
    else:
        print("   ✅ Configuration looks correct")
        print("   🤔 Issue might be in deployment or caching")
    
    print(f"\n🔧 RECOMMENDED FIXES:")
    print("   1. Verify config.py has TELEGRAM_SEND_LOW = False")
    print("   2. Check if Streamlit Cloud is using the latest code")
    print("   3. Restart the Streamlit Cloud app")
    print("   4. Check if there are multiple instances running")

if __name__ == "__main__":
    run_diagnostic()