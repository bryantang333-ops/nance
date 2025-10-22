#!/usr/bin/env python3
"""
Final test script to verify Telegram rate limiting and filtering
"""
import asyncio
import time
from datetime import datetime
from anomaly_detector import AnomalyDetector, AnomalyAlert
from config import TELEGRAM_ENABLED, MIN_24H_VOLUME_USDT, PRICE_SPIKE_THRESHOLD, VOLUME_SPIKE_THRESHOLD

def test_telegram_final():
    """Test the final Telegram configuration"""
    print("🧪 Testing Final Telegram Configuration")
    print("=" * 50)
    
    print(f"📊 Volume Filter: {MIN_24H_VOLUME_USDT:,} USDT (200M)")
    print(f"📈 Price Threshold: {PRICE_SPIKE_THRESHOLD*100:.1f}%")
    print(f"📊 Volume Threshold: {VOLUME_SPIKE_THRESHOLD:.1f}x")
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram not enabled - set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        return
    
    # Create anomaly detector
    detector = AnomalyDetector()
    
    if not detector.telegram_notifier or not detector.telegram_notifier.is_configured():
        print("❌ Telegram notifier not configured")
        return
    
    print("✅ Telegram notifier configured")
    
    # Test with high-volume pairs only
    high_volume_pairs = [
        ("BTCUSDT", 500_000_000),  # 500M volume
        ("ETHUSDT", 300_000_000),  # 300M volume
        ("BNBUSDT", 250_000_000),  # 250M volume
    ]
    
    # Test with low-volume pairs (should be filtered out)
    low_volume_pairs = [
        ("SMALLUSDT", 50_000_000),   # 50M volume (below threshold)
        ("TINYUSDT", 10_000_000),    # 10M volume (below threshold)
    ]
    
    print(f"\n🔄 Testing with high-volume pairs (should trigger alerts)...")
    for symbol, volume_24h in high_volume_pairs:
        # Simulate price spike
        alert = detector.add_price_data(symbol, 100.0, volume_24h=volume_24h)
        if alert:
            print(f"   ✅ Alert triggered for {symbol} (vol: ${volume_24h/1_000_000:.0f}M)")
        else:
            print(f"   ⚠️  No alert for {symbol} (vol: ${volume_24h/1_000_000:.0f}M)")
    
    print(f"\n🔄 Testing with low-volume pairs (should be filtered out)...")
    for symbol, volume_24h in low_volume_pairs:
        # Simulate price spike
        alert = detector.add_price_data(symbol, 100.0, volume_24h=volume_24h)
        if alert:
            print(f"   ❌ Unexpected alert for {symbol} (vol: ${volume_24h/1_000_000:.0f}M)")
        else:
            print(f"   ✅ Correctly filtered {symbol} (vol: ${volume_24h/1_000_000:.0f}M)")
    
    # Test queue processing
    print(f"\n📤 Processing telegram queue...")
    start_time = time.time()
    detector.process_pending_telegram_alerts()
    processing_time = time.time() - start_time
    
    print(f"⏱️  Processing took {processing_time:.2f} seconds")
    print(f"📋 Queue size: {len(detector.telegram_queue)}")
    
    print("\n✅ Final test completed!")
    print("📱 Check your Telegram for messages (should be very few, high-quality alerts)")
    print("🔍 Only high-volume pairs with significant moves should trigger alerts")

if __name__ == "__main__":
    test_telegram_final()
