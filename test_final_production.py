#!/usr/bin/env python3
"""
Final production test - very restrictive settings
"""
import asyncio
import time
from datetime import datetime, timedelta
from anomaly_detector import AnomalyDetector, AnomalyAlert
from config import (
    TELEGRAM_ENABLED, MIN_24H_VOLUME_USDT, MIN_MARKET_CAP_USDT, 
    PRICE_SPIKE_THRESHOLD, VOLUME_SPIKE_THRESHOLD, 
    ALERT_COOLDOWN_HOURS, TELEGRAM_SEND_EXTREME, TELEGRAM_SEND_HIGH, 
    TELEGRAM_SEND_MEDIUM, TELEGRAM_SEND_LOW
)

def test_final_production():
    """Test the final production settings"""
    print("🏭 Final Production Settings Test")
    print("=" * 50)
    
    print(f"📊 Volume Filter: {MIN_24H_VOLUME_USDT:,} USDT ({MIN_24H_VOLUME_USDT/1_000_000:.0f}M)")
    print(f"💰 Market Cap Filter: {MIN_MARKET_CAP_USDT:,} USDT ({MIN_MARKET_CAP_USDT/1_000_000:.0f}M)")
    print(f"📈 Price Threshold: {PRICE_SPIKE_THRESHOLD*100:.1f}%")
    print(f"📊 Volume Threshold: {VOLUME_SPIKE_THRESHOLD:.1f}x")
    print(f"⏰ Cooldown: {ALERT_COOLDOWN_HOURS} hours")
    print(f"🚨 Send Extreme: {TELEGRAM_SEND_EXTREME}")
    print(f"🚨 Send High: {TELEGRAM_SEND_HIGH}")
    print(f"🚨 Send Medium: {TELEGRAM_SEND_MEDIUM}")
    print(f"🚨 Send Low: {TELEGRAM_SEND_LOW}")
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram not enabled")
        return
    
    detector = AnomalyDetector()
    
    if not detector.telegram_notifier or not detector.telegram_notifier.is_configured():
        print("❌ Telegram notifier not configured")
        return
    
    print("✅ Telegram notifier configured")
    
    # Test scenarios
    test_cases = [
        {
            "name": "High-volume, high-market-cap, extreme move",
            "symbol": "BTCUSDT",
            "volume_24h": 300_000_000,  # 300M (above 250M threshold)
            "market_cap": 50_000_000,    # 50M (above 25M threshold)
            "price_change": 0.10,        # 10% (above 8% threshold)
            "expected": "Should trigger extreme alert"
        },
        {
            "name": "High-volume, high-market-cap, medium move",
            "symbol": "ETHUSDT", 
            "volume_24h": 280_000_000,   # 280M (above 250M threshold)
            "market_cap": 40_000_000,    # 40M (above 25M threshold)
            "price_change": 0.06,        # 6% (below 8% threshold, but above 3%)
            "expected": "Should trigger medium alert"
        },
        {
            "name": "Low-volume pair (should be filtered)",
            "symbol": "SMALLUSDT",
            "volume_24h": 100_000_000,   # 100M (below 250M threshold)
            "market_cap": 20_000_000,    # 20M (below 25M threshold)
            "price_change": 0.15,        # 15% (above 8% threshold)
            "expected": "Should be filtered by volume/market cap"
        },
        {
            "name": "Low-market-cap pair (should be filtered)",
            "symbol": "TINYUSDT",
            "volume_24h": 300_000_000,   # 300M (above 250M threshold)
            "market_cap": 10_000_000,    # 10M (below 25M threshold)
            "price_change": 0.12,        # 12% (above 8% threshold)
            "expected": "Should be filtered by market cap"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Expected: {test_case['expected']}")
        
        symbol = test_case['symbol']
        volume_24h = test_case['volume_24h']
        market_cap = test_case['market_cap']
        price_change = test_case['price_change']
        
        # Add initial price
        base_price = 100.0
        detector.add_price_data(symbol, base_price, volume_24h=volume_24h, market_cap=market_cap)
        
        # Simulate price movement
        new_price = base_price * (1 + price_change)
        alert = detector.add_price_data(symbol, new_price, volume_24h=volume_24h, market_cap=market_cap)
        
        if alert:
            print(f"   ✅ ALERT TRIGGERED: {alert.severity} - {alert.description}")
        else:
            print(f"   ⚠️  No alert triggered")
    
    # Test cooldown functionality
    print(f"\n🧪 Test Cooldown Functionality")
    symbol = "TESTUSDT"
    volume_24h = 300_000_000
    market_cap = 50_000_000
    
    # First alert (should trigger)
    detector.add_price_data(symbol, 100.0, volume_24h=volume_24h, market_cap=market_cap)
    alert1 = detector.add_price_data(symbol, 110.0, volume_24h=volume_24h, market_cap=market_cap)  # 10% move
    
    if alert1:
        print(f"   ✅ First alert triggered: {alert1.severity}")
    else:
        print(f"   ❌ First alert not triggered")
    
    # Second alert immediately (should be blocked by cooldown)
    alert2 = detector.add_price_data(symbol, 120.0, volume_24h=volume_24h, market_cap=market_cap)  # 20% move
    
    if alert2:
        print(f"   ❌ UNEXPECTED: Second alert triggered despite cooldown")
    else:
        print(f"   ✅ Correctly blocked by cooldown")
    
    # Process queue
    print(f"\n📤 Processing telegram queue...")
    start_time = time.time()
    detector.process_pending_telegram_alerts()
    processing_time = time.time() - start_time
    
    print(f"⏱️  Processing took {processing_time:.2f} seconds")
    print(f"📋 Queue size: {len(detector.telegram_queue)}")
    print(f"🕐 Cooldowns: {len(detector.alert_cooldowns)} symbols")
    
    print("\n✅ Final production test completed!")
    print("📱 Check your Telegram - should receive very few, high-quality alerts")
    print("🔍 Only medium+ severity alerts from high-volume, high-market-cap pairs should be sent")
    print("⏰ Each symbol can only alert once per 24 hours")

if __name__ == "__main__":
    test_final_production()
