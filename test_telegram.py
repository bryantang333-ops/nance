#!/usr/bin/env python3
"""
Test script to send a fake alert to your Telegram bot
"""
import asyncio
import os
from datetime import datetime
from telegram_notifier import TelegramNotifier
from anomaly_detector import AnomalyAlert

async def test_telegram():
    """Send test alerts to Telegram"""
    print("🧪 Testing Telegram bot...")
    
    # Set your credentials
    os.environ['TELEGRAM_BOT_TOKEN'] = '8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY'
    os.environ['TELEGRAM_CHAT_ID'] = '751872795'
    
    notifier = TelegramNotifier()
    
    if not notifier.is_configured():
        print("❌ Telegram not configured properly")
        return
    
    print("✅ Telegram bot configured")
    
    # Send test message
    print("📤 Sending test message...")
    success = await notifier.send_test_message()
    if success:
        print("✅ Test message sent! Check your Telegram.")
    else:
        print("❌ Failed to send test message")
    
    # Send fake price spike alert
    print("📤 Sending fake price spike alert...")
    fake_alert = AnomalyAlert(
        symbol="BTCUSDT",
        alert_type="price_spike",
        severity="high",
        value=45000.0,
        threshold=3.0,
        percentage_change=5.2,
        timestamp=datetime.now(),
        description="Price up 5.20% in 5 minutes"
    )
    
    success = await notifier.send_alert(fake_alert)
    if success:
        print("✅ Fake alert sent! Check your Telegram.")
    else:
        print("❌ Failed to send fake alert")
    
    # Send fake volume spike alert
    print("📤 Sending fake volume spike alert...")
    fake_volume_alert = AnomalyAlert(
        symbol="ETHUSDT",
        alert_type="volume_spike",
        severity="extreme",
        value=1500000.0,
        threshold=2.0,
        percentage_change=350.0,
        timestamp=datetime.now(),
        description="Volume 3.5x above 1-hour average"
    )
    
    success = await notifier.send_alert(fake_volume_alert)
    if success:
        print("✅ Fake volume alert sent! Check your Telegram.")
    else:
        print("❌ Failed to send fake volume alert")

if __name__ == "__main__":
    asyncio.run(test_telegram())
