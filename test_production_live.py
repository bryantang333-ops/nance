#!/usr/bin/env python3
"""
Test production settings live to verify they're working
"""
import asyncio
from datetime import datetime
from anomaly_detector import AnomalyDetector, AnomalyAlert
from config import TELEGRAM_ENABLED, TELEGRAM_SEND_LOW, ALERT_COOLDOWN_HOURS

async def test_production_live():
    """Test production settings live"""
    print("🧪 TESTING PRODUCTION SETTINGS LIVE")
    print("=" * 45)
    
    print(f"📊 Current Settings:")
    print(f"   TELEGRAM_SEND_LOW: {TELEGRAM_SEND_LOW}")
    print(f"   ALERT_COOLDOWN_HOURS: {ALERT_COOLDOWN_HOURS}")
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram not enabled")
        return
    
    detector = AnomalyDetector()
    
    if not detector.telegram_notifier or not detector.telegram_notifier.is_configured():
        print("❌ Telegram notifier not configured")
        return
    
    print("✅ Telegram notifier configured")
    
    # Test 1: Try to send a low severity alert (should be blocked)
    print(f"\n🧪 Test 1: Low severity alert (should be BLOCKED)")
    low_alert = AnomalyAlert(
        symbol="TESTLOWUSDT",
        alert_type="price_spike",
        severity="low",
        value=100.0,
        threshold=3.0,
        percentage_change=5.0,
        timestamp=datetime.now(),
        description="This should be BLOCKED - low severity"
    )
    
    should_send = detector._should_send_alert(low_alert)
    print(f"   Should send low alert: {should_send}")
    
    if should_send:
        print("   ❌ PROBLEM: Low severity alert would be sent!")
        print("   🔧 This means the fix is NOT working")
    else:
        print("   ✅ GOOD: Low severity alert correctly blocked")
    
    # Test 2: Try to send a medium severity alert (should be sent)
    print(f"\n🧪 Test 2: Medium severity alert (should be SENT)")
    medium_alert = AnomalyAlert(
        symbol="TESTMEDUSDT",
        alert_type="price_spike",
        severity="medium",
        value=100.0,
        threshold=3.0,
        percentage_change=8.5,
        timestamp=datetime.now(),
        description="This should be SENT - medium severity"
    )
    
    should_send = detector._should_send_alert(medium_alert)
    print(f"   Should send medium alert: {should_send}")
    
    if should_send:
        print("   ✅ GOOD: Medium severity alert would be sent")
    else:
        print("   ❌ PROBLEM: Medium severity alert blocked!")
    
    # Test 3: Test cooldown
    print(f"\n🧪 Test 3: Cooldown functionality")
    test_symbol = "COAIUSDT"
    
    # Check if already in cooldown
    in_cooldown = detector._is_in_cooldown(test_symbol)
    print(f"   {test_symbol} in cooldown: {in_cooldown}")
    
    # Simulate sending an alert
    detector._update_cooldown(test_symbol)
    in_cooldown_after = detector._is_in_cooldown(test_symbol)
    print(f"   {test_symbol} in cooldown after update: {in_cooldown_after}")
    
    # Test 4: Try to queue another alert for same symbol
    print(f"\n🧪 Test 4: Second alert for same symbol (should be BLOCKED)")
    second_alert = AnomalyAlert(
        symbol=test_symbol,
        alert_type="price_spike",
        severity="high",
        value=100.0,
        threshold=3.0,
        percentage_change=10.0,
        timestamp=datetime.now(),
        description="Second alert for same symbol - should be blocked"
    )
    
    # This should be blocked by cooldown
    detector._queue_telegram_alert(second_alert)
    queue_size = len(detector.telegram_queue)
    print(f"   Queue size after trying to add second alert: {queue_size}")
    
    if queue_size == 0:
        print("   ✅ GOOD: Second alert correctly blocked by cooldown")
    else:
        print("   ❌ PROBLEM: Second alert was queued despite cooldown!")
    
    print(f"\n🎯 SUMMARY:")
    if not TELEGRAM_SEND_LOW and ALERT_COOLDOWN_HOURS >= 24:
        print("   ✅ Production settings are CORRECT")
        print("   📱 If you're still getting spam, the issue is:")
        print("      1. Streamlit Cloud hasn't rebuilt yet")
        print("      2. Multiple instances are running")
        print("      3. Caching issues")
    else:
        print("   ❌ Production settings are INCORRECT")
        print("   🔧 Need to fix the configuration")
    
    print(f"\n🔧 NEXT STEPS:")
    print("   1. Wait 2-3 minutes for Streamlit Cloud to rebuild")
    print("   2. Check your Streamlit Cloud app logs")
    print("   3. If still spamming, restart the Streamlit Cloud app")
    print("   4. Monitor Telegram for reduced alert frequency")

if __name__ == "__main__":
    asyncio.run(test_production_live())
