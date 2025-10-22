#!/usr/bin/env python3
"""
Simple test to verify the two specific fixes:
1. 24-hour cooldown for same pair
2. No low severity alerts
"""
import time
from datetime import datetime
from anomaly_detector import AnomalyDetector, AnomalyAlert
from config import TELEGRAM_ENABLED, TELEGRAM_SEND_LOW, ALERT_COOLDOWN_HOURS

def test_simple_fixes():
    """Test the two specific fixes"""
    print("🔧 Testing Simple Fixes")
    print("=" * 40)
    
    print(f"🚨 Send Low Alerts: {TELEGRAM_SEND_LOW}")
    print(f"⏰ Cooldown Hours: {ALERT_COOLDOWN_HOURS}")
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram not enabled")
        return
    
    detector = AnomalyDetector()
    
    if not detector.telegram_notifier or not detector.telegram_notifier.is_configured():
        print("❌ Telegram notifier not configured")
        return
    
    print("✅ Telegram notifier configured")
    
    # Test 1: Low severity alert should be blocked
    print(f"\n🧪 Test 1: Low severity alert (should be blocked)")
    
    # Create a low severity alert manually
    low_alert = AnomalyAlert(
        symbol="TESTUSDT",
        alert_type="price_spike",
        severity="low",  # LOW severity
        value=100.0,
        threshold=3.0,
        percentage_change=5.0,
        timestamp=datetime.now(),
        description="Test low severity alert"
    )
    
    # Check if it should be sent
    should_send = detector._should_send_alert(low_alert)
    print(f"   Should send low alert: {should_send}")
    
    if should_send:
        print("   ❌ PROBLEM: Low severity alert would be sent!")
    else:
        print("   ✅ GOOD: Low severity alert correctly blocked")
    
    # Test 2: Medium severity alert should be sent
    print(f"\n🧪 Test 2: Medium severity alert (should be sent)")
    
    medium_alert = AnomalyAlert(
        symbol="TESTUSDT",
        alert_type="price_spike",
        severity="medium",  # MEDIUM severity
        value=100.0,
        threshold=3.0,
        percentage_change=5.0,
        timestamp=datetime.now(),
        description="Test medium severity alert"
    )
    
    should_send = detector._should_send_alert(medium_alert)
    print(f"   Should send medium alert: {should_send}")
    
    if should_send:
        print("   ✅ GOOD: Medium severity alert would be sent")
    else:
        print("   ❌ PROBLEM: Medium severity alert blocked!")
    
    # Test 3: Cooldown functionality
    print(f"\n🧪 Test 3: 24-hour cooldown test")
    
    symbol = "COAIUSDT"
    
    # Check if symbol is in cooldown (should be False initially)
    in_cooldown = detector._is_in_cooldown(symbol)
    print(f"   {symbol} in cooldown initially: {in_cooldown}")
    
    # Simulate sending an alert (this should put it in cooldown)
    detector._update_cooldown(symbol)
    print(f"   Updated cooldown for {symbol}")
    
    # Check if symbol is now in cooldown
    in_cooldown = detector._is_in_cooldown(symbol)
    print(f"   {symbol} in cooldown after update: {in_cooldown}")
    
    if in_cooldown:
        print("   ✅ GOOD: Cooldown working correctly")
    else:
        print("   ❌ PROBLEM: Cooldown not working!")
    
    # Test 4: Try to send another alert for same symbol
    print(f"\n🧪 Test 4: Second alert for same symbol (should be blocked)")
    
    second_alert = AnomalyAlert(
        symbol=symbol,
        alert_type="price_spike",
        severity="high",
        value=100.0,
        threshold=3.0,
        percentage_change=5.0,
        timestamp=datetime.now(),
        description="Second alert for same symbol"
    )
    
    # This should be blocked by cooldown
    detector._queue_telegram_alert(second_alert)
    print(f"   Attempted to queue second alert for {symbol}")
    print(f"   Queue size: {len(detector.telegram_queue)}")
    
    if len(detector.telegram_queue) == 0:
        print("   ✅ GOOD: Second alert correctly blocked by cooldown")
    else:
        print("   ❌ PROBLEM: Second alert was queued despite cooldown!")
    
    print("\n✅ Simple fixes test completed!")
    print("📋 Summary:")
    print(f"   - Low severity alerts blocked: {not TELEGRAM_SEND_LOW}")
    print(f"   - Cooldown duration: {ALERT_COOLDOWN_HOURS} hours")
    print(f"   - Cooldown tracking: {len(detector.alert_cooldowns)} symbols")

if __name__ == "__main__":
    test_simple_fixes()
