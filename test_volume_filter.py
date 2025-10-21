#!/usr/bin/env python3
"""
Test script to verify 24h volume filtering works
"""
import asyncio
from datetime import datetime
from anomaly_detector import AnomalyDetector, AnomalyAlert

async def test_volume_filtering():
    """Test that alerts are filtered by 24h volume"""
    print("🧪 Testing 24h volume filtering...")
    
    detector = AnomalyDetector()
    
    # Test 1: High volume pair (should trigger alert)
    print("\n📊 Test 1: High volume pair (BTCUSDT)")
    high_volume_24h = 500_000_000  # 500M USDT (above 100M threshold)
    
    # Simulate price spike with multiple data points
    detector.add_price_data("BTCUSDT", 44000.0, volume_24h=high_volume_24h)  # Base price
    detector.add_price_data("BTCUSDT", 44100.0, volume_24h=high_volume_24h)  # Small change
    alert1 = detector.add_price_data("BTCUSDT", 46500.0, volume_24h=high_volume_24h)  # 5.7% spike
    if alert1:
        print(f"✅ High volume alert triggered: {alert1.description}")
    else:
        print("❌ High volume alert not triggered")
    
    # Test 2: Low volume pair (should NOT trigger alert)
    print("\n📊 Test 2: Low volume pair (SMALLCOINUSDT)")
    low_volume_24h = 50_000_000  # 50M USDT (below 100M threshold)
    
    # Simulate price spike with multiple data points
    detector.add_price_data("SMALLCOINUSDT", 0.0008, volume_24h=low_volume_24h)  # Base price
    detector.add_price_data("SMALLCOINUSDT", 0.0009, volume_24h=low_volume_24h)  # Small change
    alert2 = detector.add_price_data("SMALLCOINUSDT", 0.0012, volume_24h=low_volume_24h)  # 50% spike
    if alert2:
        print(f"❌ Low volume alert triggered (should be filtered): {alert2.description}")
    else:
        print("✅ Low volume alert correctly filtered out")
    
    # Test 3: No volume data (should trigger alert - no filtering)
    print("\n📊 Test 3: No volume data (should trigger)")
    detector.add_price_data("ETHUSDT", 2900.0, volume_24h=None)  # Base price
    detector.add_price_data("ETHUSDT", 2950.0, volume_24h=None)  # Small change
    alert3 = detector.add_price_data("ETHUSDT", 3100.0, volume_24h=None)  # 6.9% spike
    if alert3:
        print(f"✅ No volume data alert triggered: {alert3.description}")
    else:
        print("❌ No volume data alert not triggered")
    
    print(f"\n📈 Total alerts generated: {len(detector.alerts)}")
    for i, alert in enumerate(detector.alerts):
        print(f"{i+1}. {alert.symbol} - {alert.alert_type} - {alert.description}")

if __name__ == "__main__":
    asyncio.run(test_volume_filtering())
