#!/usr/bin/env python3
"""
Test script with realistic price movements to trigger alerts
"""
import asyncio
import time
from datetime import datetime, timedelta
from anomaly_detector import AnomalyDetector, AnomalyAlert
from config import TELEGRAM_ENABLED, MIN_24H_VOLUME_USDT, PRICE_SPIKE_THRESHOLD

def test_realistic_alerts():
    """Test with realistic price movements"""
    print("🧪 Testing Realistic Alert Scenarios")
    print("=" * 50)
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram not enabled")
        return
    
    detector = AnomalyDetector()
    
    if not detector.telegram_notifier or not detector.telegram_notifier.is_configured():
        print("❌ Telegram notifier not configured")
        return
    
    print("✅ Telegram notifier configured")
    
    # Test realistic scenario: BTC price spike
    symbol = "BTCUSDT"
    volume_24h = 500_000_000  # 500M volume (above 200M threshold)
    base_price = 43000.0
    
    print(f"\n📊 Testing {symbol} with ${volume_24h/1_000_000:.0f}M volume")
    print(f"📈 Price threshold: {PRICE_SPIKE_THRESHOLD*100:.1f}%")
    
    # Add initial price data
    detector.add_price_data(symbol, base_price, volume_24h=volume_24h)
    print(f"   📍 Initial price: ${base_price:,.2f}")
    
    # Simulate gradual price increase (should not trigger alert)
    for i in range(1, 4):
        price = base_price * (1 + 0.01 * i)  # 1%, 2%, 3% increase
        detector.add_price_data(symbol, price, volume_24h=volume_24h)
        print(f"   📈 Price {i}: ${price:,.2f} (+{i}%)")
    
    # Simulate significant price spike (should trigger alert)
    spike_price = base_price * (1 + PRICE_SPIKE_THRESHOLD + 0.01)  # 6% increase
    alert = detector.add_price_data(symbol, spike_price, volume_24h=volume_24h)
    
    if alert:
        print(f"   🚨 ALERT TRIGGERED! Price: ${spike_price:,.2f} (+{((spike_price/base_price)-1)*100:.1f}%)")
        print(f"   📊 Alert severity: {alert.severity}")
        print(f"   📝 Description: {alert.description}")
    else:
        print(f"   ⚠️  No alert triggered for {((spike_price/base_price)-1)*100:.1f}% move")
    
    # Test volume spike
    print(f"\n📊 Testing volume spike for {symbol}")
    base_volume = 1000000.0  # 1M volume
    
    # Add volume history
    for i in range(10):
        detector.add_volume_data(symbol, base_volume, volume_24h=volume_24h)
    
    # Simulate volume spike
    spike_volume = base_volume * 4.0  # 4x volume spike
    volume_alert = detector.add_volume_data(symbol, spike_volume, volume_24h=volume_24h)
    
    if volume_alert:
        print(f"   🚨 VOLUME ALERT! Volume: {spike_volume:,.0f} ({spike_volume/base_volume:.1f}x)")
        print(f"   📊 Alert severity: {volume_alert.severity}")
    else:
        print(f"   ⚠️  No volume alert triggered")
    
    # Process telegram queue
    print(f"\n📤 Processing telegram queue...")
    detector.process_pending_telegram_alerts()
    print(f"📋 Queue size: {len(detector.telegram_queue)}")
    
    print("\n✅ Realistic test completed!")
    print("📱 Check your Telegram for alerts")

if __name__ == "__main__":
    test_realistic_alerts()
