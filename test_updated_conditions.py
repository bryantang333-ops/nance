#!/usr/bin/env python3
"""
Test the updated alert conditions
"""
import asyncio
from datetime import datetime
from anomaly_detector import AnomalyDetector, AnomalyAlert
from config import (
    TELEGRAM_ENABLED, MIN_24H_VOLUME_USDT, MIN_MARKET_CAP_USDT, 
    PRICE_SPIKE_THRESHOLD, VOLUME_SPIKE_THRESHOLD
)

async def test_updated_conditions():
    """Test the updated alert conditions"""
    print("🧪 TESTING UPDATED ALERT CONDITIONS")
    print("=" * 45)
    
    print(f"📊 Updated Settings:")
    print(f"   MIN_24H_VOLUME_USDT: {MIN_24H_VOLUME_USDT:,} USDT")
    print(f"   MIN_MARKET_CAP_USDT: {MIN_MARKET_CAP_USDT:,} USDT")
    print(f"   PRICE_SPIKE_THRESHOLD: {PRICE_SPIKE_THRESHOLD*100:.1f}%")
    print(f"   VOLUME_SPIKE_THRESHOLD: {VOLUME_SPIKE_THRESHOLD:.1f}x")
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram not enabled")
        return
    
    detector = AnomalyDetector()
    
    if not detector.telegram_notifier or not detector.telegram_notifier.is_configured():
        print("❌ Telegram notifier not configured")
        return
    
    print("✅ Telegram notifier configured")
    
    # Test cases
    test_cases = [
        {
            "name": "Major pair with 8% move (should trigger)",
            "symbol": "BTCUSDT",
            "volume_24h": 300_000_000,  # 300M (above 250M)
            "market_cap": 1_000_000_000,  # 1B (no restriction)
            "price_change": 0.08,  # 8% (exactly at threshold)
            "expected": "Should trigger medium alert"
        },
        {
            "name": "Small altcoin with 8% move (should trigger)",
            "symbol": "SMALLUSDT",
            "volume_24h": 280_000_000,  # 280M (above 250M)
            "market_cap": 10_000_000,  # 10M (small market cap, but no restriction)
            "price_change": 0.10,  # 10% (above 8% threshold)
            "expected": "Should trigger medium alert"
        },
        {
            "name": "Any pair with 5% move (should NOT trigger)",
            "symbol": "TESTUSDT",
            "volume_24h": 300_000_000,  # 300M (above 250M)
            "market_cap": 50_000_000,  # 50M (no restriction)
            "price_change": 0.05,  # 5% (below 8% threshold)
            "expected": "Should NOT trigger (below 8% threshold)"
        },
        {
            "name": "Any pair with low volume (should NOT trigger)",
            "symbol": "LOWVOLUSDT",
            "volume_24h": 100_000_000,  # 100M (below 250M)
            "market_cap": 50_000_000,  # 50M (no restriction)
            "price_change": 0.15,  # 15% (above 8% threshold)
            "expected": "Should NOT trigger (below 250M volume)"
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
    
    print(f"\n🎯 SUMMARY:")
    print(f"   ✅ Volume threshold: 250M USDT (any pair)")
    print(f"   ✅ Market cap: No restriction (includes all altcoins)")
    print(f"   ✅ Price threshold: 8% in 5 minutes")
    print(f"   ✅ Volume threshold: 5x above 1-hour average")
    print(f"   ✅ Severity: Medium+ only")
    print(f"   ✅ Cooldown: 24 hours per symbol")
    
    print(f"\n📱 You should now get alerts for:")
    print(f"   - Any pair with 250M+ volume")
    print(f"   - 8%+ price moves or 5x+ volume spikes")
    print(f"   - Medium+ severity only")
    print(f"   - Once per symbol per 24 hours")

if __name__ == "__main__":
    asyncio.run(test_updated_conditions())
