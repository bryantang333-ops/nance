#!/usr/bin/env python3
"""
Test script to verify Telegram rate limiting fix
"""
import asyncio
import time
from datetime import datetime
from anomaly_detector import AnomalyDetector, AnomalyAlert
from config import TELEGRAM_ENABLED

def test_telegram_rate_limiting():
    """Test the new rate limiting system"""
    print("🧪 Testing Telegram Rate Limiting Fix")
    print("=" * 50)
    
    if not TELEGRAM_ENABLED:
        print("❌ Telegram not enabled - set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        return
    
    # Create anomaly detector
    detector = AnomalyDetector()
    
    if not detector.telegram_notifier or not detector.telegram_notifier.is_configured():
        print("❌ Telegram notifier not configured")
        return
    
    print("✅ Telegram notifier configured")
    
    # Create test alerts
    test_alerts = []
    for i in range(10):
        alert = AnomalyAlert(
            symbol=f"TEST{i}USDT",
            alert_type="price_spike",
            severity="high" if i % 2 == 0 else "extreme",
            value=100.0 + i,
            threshold=3.0,
            percentage_change=5.0 + i,
            timestamp=datetime.now(),
            description=f"Test alert {i+1}"
        )
        test_alerts.append(alert)
    
    print(f"📊 Created {len(test_alerts)} test alerts")
    
    # Test queueing system
    print("\n🔄 Testing alert queueing...")
    start_time = time.time()
    
    for alert in test_alerts:
        detector._queue_telegram_alert(alert)
        print(f"   Queued alert for {alert.symbol}")
        time.sleep(0.1)  # Small delay between queueing
    
    print(f"⏱️  Queueing took {time.time() - start_time:.2f} seconds")
    print(f"📋 Queue size: {len(detector.telegram_queue)}")
    
    # Test processing
    print("\n📤 Processing queue...")
    start_time = time.time()
    
    detector.process_pending_telegram_alerts()
    
    print(f"⏱️  Processing took {time.time() - start_time:.2f} seconds")
    print(f"📋 Remaining queue size: {len(detector.telegram_queue)}")
    
    print("\n✅ Rate limiting test completed!")
    print("📱 Check your Telegram for messages (should be batched and rate-limited)")

if __name__ == "__main__":
    test_telegram_rate_limiting()
