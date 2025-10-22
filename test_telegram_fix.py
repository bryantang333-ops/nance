#!/usr/bin/env python3
"""
Test the Telegram alert fix for WebSocket threads
"""
import asyncio
import threading
import os
from datetime import datetime
from anomaly_detector import AnomalyDetector, AnomalyAlert

def test_telegram_in_thread():
    """Test Telegram sending from a background thread (simulating WebSocket thread)"""
    print("🧪 Testing Telegram alerts from background thread...")
    
    # Set up environment
    os.environ['TELEGRAM_BOT_TOKEN'] = '8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY'
    os.environ['TELEGRAM_CHAT_ID'] = '-1002327706087'
    
    # Create detector
    detector = AnomalyDetector()
    
    # Simulate WebSocket thread
    def websocket_thread():
        print("📡 Simulating WebSocket thread...")
        
        # Create fake alert
        fake_alert = AnomalyAlert(
            symbol="BTCUSDT",
            alert_type="price_spike",
            severity="high",
            value=45000.0,
            threshold=3.0,
            percentage_change=5.2,
            timestamp=datetime.now(),
            description="Price up 5.20% in 5 minutes (24h vol: $500.0M)"
        )
        
        # Try to send alert from thread (this should work now)
        print("📤 Sending alert from WebSocket thread...")
        detector._send_telegram_alert(fake_alert)
        print("✅ Alert sent successfully from thread!")
    
    # Run in background thread
    thread = threading.Thread(target=websocket_thread)
    thread.start()
    thread.join()
    
    print("🎉 Test completed!")

if __name__ == "__main__":
    test_telegram_in_thread()
