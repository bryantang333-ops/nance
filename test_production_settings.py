#!/usr/bin/env python3
"""
Test script for production settings - very restrictive alerting
"""
import asyncio
import time
from datetime import datetime, timedelta
from anomaly_detector import AnomalyDetector, AnomalyAlert
from config import (
    TELEGRAM_ENABLED, MIN_24H_VOLUME_USDT, PRICE_SPIKE_THRESHOLD, 
    VOLUME_SPIKE_THRESHOLD, ALERT_COOLDOWN_HOURS, TELEGRAM_SEND_EXTREME, TELEGRAM_SEND_HIGH
)

def test_production_settings():
    """Test the production settings"""
    print("🏭 Testing Production Alert Settings")
    print("=" * 50)
    
    print(f"📊 Volume Filter: {MIN_24H_VOLUME_USDT:,} USDT ({MIN_24H_VOLUME_USDT/1_000_000:.0f}M)")
    print(f"📈 Price Threshold: {PRICE_SPIKE_THRESHOLD*100:.1f}%")
    print(f"📊 Volume Threshold: {VOLUME_SPIKE_THRESHOLD:.1f}x")
    print(f"⏰ Cooldown: {ALERT_COOLDOWN_HOURS} hours")
    print(f"🚨 Send Extreme: {TELEGRAM_SEND_EXTREME}")
    print(f"🚨 Send High: {TELEGRAM_SEND_HIGH}")
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram not enabled")
        return
    
    detector = AnomalyDetector()
    
    if not detector.telegram_notifier or not detector.telegram_notifier.is_configured():
        print("❌ Telegram notifier not configured")
        return
    
    print("✅ Telegram notifier configured")
    
    # Test 1: High-volume pair with extreme price movement
    print(f"\n🧪 Test 1: Extreme price movement (should trigger)")
    symbol = "BTCUSDT"
    volume_24h = 600_000_000  # 600M volume (above 500M threshold)
    base_price = 43000.0
    
    # Add initial price
    detector.add_price_data(symbol, base_price, volume_24h=volume_24h)
    
    # Simulate extreme price spike (10% - above 8% threshold)
    extreme_price = base_price * 1.10  # 10% increase
    alert1 = detector.add_price_data(symbol, extreme_price, volume_24h=volume_24h)
    
    if alert1:
        print(f"   ✅ EXTREME ALERT: {symbol} {alert1.severity} - {alert1.description}")
    else:
        print(f"   ❌ No alert for 10% price move")
    
    # Test 2: Same symbol again (should be in cooldown)
    print(f"\n🧪 Test 2: Same symbol again (should be blocked by cooldown)")
    alert2 = detector.add_price_data(symbol, base_price * 1.12, volume_24h=volume_24h)
    
    if alert2:
        print(f"   ❌ UNEXPECTED: Alert sent despite cooldown")
    else:
        print(f"   ✅ Correctly blocked by cooldown")
    
    # Test 3: High severity alert (should be filtered out)
    print(f"\n🧪 Test 3: High severity alert (should be filtered)")
    symbol2 = "ETHUSDT"
    volume_24h2 = 400_000_000  # 400M volume (below 500M threshold)
    
    # This should be filtered by volume threshold
    alert3 = detector.add_price_data(symbol2, 3000.0, volume_24h=volume_24h2)
    
    if alert3:
        print(f"   ❌ UNEXPECTED: Alert sent for low-volume pair")
    else:
        print(f"   ✅ Correctly filtered by volume threshold")
    
    # Test 4: Process queue
    print(f"\n📤 Processing telegram queue...")
    start_time = time.time()
    detector.process_pending_telegram_alerts()
    processing_time = time.time() - start_time
    
    print(f"⏱️  Processing took {processing_time:.2f} seconds")
    print(f"📋 Queue size: {len(detector.telegram_queue)}")
    print(f"🕐 Cooldowns: {len(detector.alert_cooldowns)} symbols")
    
    # Show cooldown status
    for symbol, last_alert in detector.alert_cooldowns.items():
        time_since = datetime.now() - last_alert
        print(f"   {symbol}: {time_since.total_seconds():.0f}s ago")
    
    print("\n✅ Production test completed!")
    print("📱 Check your Telegram - should receive very few, high-quality alerts")
    print("🔍 Only extreme alerts from high-volume pairs should be sent")

if __name__ == "__main__":
    test_production_settings()
