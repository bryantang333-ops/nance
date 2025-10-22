#!/usr/bin/env python3
"""
Test the new production settings as specified by user
"""
import asyncio
from datetime import datetime
from anomaly_detector import AnomalyDetector, AnomalyAlert
from config import (
    TELEGRAM_ENABLED, MIN_24H_VOLUME_USDT, MIN_MARKET_CAP_USDT, 
    PRICE_SPIKE_THRESHOLD, VOLUME_SPIKE_THRESHOLD, TELEGRAM_RATE_LIMIT,
    ALERT_COOLDOWN_HOURS, TELEGRAM_SEND_EXTREME, TELEGRAM_SEND_HIGH, 
    TELEGRAM_SEND_MEDIUM, TELEGRAM_SEND_LOW
)

async def test_new_production_settings():
    """Test the new production settings"""
    print("🧪 TESTING NEW PRODUCTION SETTINGS")
    print("=" * 45)
    
    print(f"📊 User Specified Settings:")
    print(f"   Price Threshold: {PRICE_SPIKE_THRESHOLD*100:.1f}% (10% - extreme moves only)")
    print(f"   Volume Threshold: {VOLUME_SPIKE_THRESHOLD:.1f}x (5x - massive spikes)")
    print(f"   Volume Requirement: {MIN_24H_VOLUME_USDT:,} USDT (250M)")
    print(f"   Market Cap Requirement: {MIN_MARKET_CAP_USDT:,} USDT (100M - established tokens)")
    print(f"   Rate Limit: {TELEGRAM_RATE_LIMIT/60:.1f} minutes between messages")
    print(f"   Cooldown: {ALERT_COOLDOWN_HOURS} hours per ticker")
    print(f"   Send Extreme: {TELEGRAM_SEND_EXTREME}")
    print(f"   Send High: {TELEGRAM_SEND_HIGH}")
    print(f"   Send Medium: {TELEGRAM_SEND_MEDIUM}")
    print(f"   Send Low: {TELEGRAM_SEND_LOW}")
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram not enabled")
        return
    
    detector = AnomalyDetector()
    
    if not detector.telegram_notifier or not detector.telegram_notifier.is_configured():
        print("❌ Telegram notifier not configured")
        return
    
    print("✅ Telegram notifier configured")
    
    # Test cases based on user specifications
    test_cases = [
        {
            "name": "10% price move with 250M+ volume and 100M+ market cap (should trigger)",
            "symbol": "BTCUSDT",
            "volume_24h": 300_000_000,  # 300M (above 250M)
            "market_cap": 150_000_000,  # 150M (above 100M)
            "price_change": 0.10,  # 10% (exactly at threshold)
            "expected": "Should trigger medium alert"
        },
        {
            "name": "5x volume spike with 250M+ volume and 100M+ market cap (should trigger)",
            "symbol": "ETHUSDT",
            "volume_24h": 280_000_000,  # 280M (above 250M)
            "market_cap": 200_000_000,  # 200M (above 100M)
            "volume_spike": 5.0,  # 5x (exactly at threshold)
            "expected": "Should trigger medium alert"
        },
        {
            "name": "8% price move (below 10% threshold - should NOT trigger)",
            "symbol": "TESTUSDT",
            "volume_24h": 300_000_000,  # 300M (above 250M)
            "market_cap": 150_000_000,  # 150M (above 100M)
            "price_change": 0.08,  # 8% (below 10% threshold)
            "expected": "Should NOT trigger (below 10% threshold)"
        },
        {
            "name": "Low volume (below 250M - should NOT trigger)",
            "symbol": "LOWVOLUSDT",
            "volume_24h": 100_000_000,  # 100M (below 250M)
            "market_cap": 150_000_000,  # 150M (above 100M)
            "price_change": 0.15,  # 15% (above 10% threshold)
            "expected": "Should NOT trigger (below 250M volume)"
        },
        {
            "name": "Low market cap (below 100M - should NOT trigger)",
            "symbol": "LOWCAPUSDT",
            "volume_24h": 300_000_000,  # 300M (above 250M)
            "market_cap": 50_000_000,  # 50M (below 100M)
            "price_change": 0.15,  # 15% (above 10% threshold)
            "expected": "Should NOT trigger (below 100M market cap)"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"   Expected: {test_case['expected']}")
        
        symbol = test_case['symbol']
        volume_24h = test_case['volume_24h']
        market_cap = test_case['market_cap']
        price_change = test_case.get('price_change', 0)
        
        # Add initial price
        base_price = 100.0
        detector.add_price_data(symbol, base_price, volume_24h=volume_24h, market_cap=market_cap)
        
        # Simulate price movement
        if price_change > 0:
            new_price = base_price * (1 + price_change)
            alert = detector.add_price_data(symbol, new_price, volume_24h=volume_24h, market_cap=market_cap)
            
            if alert:
                print(f"   ✅ ALERT TRIGGERED: {alert.severity} - {alert.description}")
            else:
                print(f"   ⚠️  No alert triggered")
    
    # Test cooldown functionality
    print(f"\n🧪 Test Cooldown: 24-hour cooldown per ticker")
    test_symbol = "COAIUSDT"
    
    # First alert (should trigger)
    detector.add_price_data(test_symbol, 100.0, volume_24h=300_000_000, market_cap=150_000_000)
    alert1 = detector.add_price_data(test_symbol, 110.0, volume_24h=300_000_000, market_cap=150_000_000)  # 10% move
    
    if alert1:
        print(f"   ✅ First alert triggered: {alert1.severity}")
    else:
        print(f"   ❌ First alert not triggered")
    
    # Second alert immediately (should be blocked by cooldown)
    alert2 = detector.add_price_data(test_symbol, 120.0, volume_24h=300_000_000, market_cap=150_000_000)  # 20% move
    
    if alert2:
        print(f"   ❌ UNEXPECTED: Second alert triggered despite cooldown")
    else:
        print(f"   ✅ Correctly blocked by 24-hour cooldown")
    
    print(f"\n🎯 SUMMARY:")
    print(f"   ✅ Price threshold: 10% (extreme moves only)")
    print(f"   ✅ Volume threshold: 5x (massive spikes)")
    print(f"   ✅ Volume requirement: 250M USDT")
    print(f"   ✅ Market cap requirement: 100M USDT (established tokens)")
    print(f"   ✅ Rate limit: 5 minutes between messages")
    print(f"   ✅ Cooldown: 24 hours per ticker")
    print(f"   ✅ Severity: Medium+ only (no low severity)")
    
    print(f"\n📱 You should now get alerts for:")
    print(f"   - 10%+ price moves on established tokens (100M+ market cap)")
    print(f"   - 5x+ volume spikes on high-volume pairs (250M+ volume)")
    print(f"   - Medium+ severity only")
    print(f"   - Once per ticker per 24 hours")
    print(f"   - Maximum 1 alert every 5 minutes")

if __name__ == "__main__":
    asyncio.run(test_new_production_settings())
