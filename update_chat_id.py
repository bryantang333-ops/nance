#!/usr/bin/env python3
"""
Update chat ID to group chat
"""
import os
import asyncio
from telegram_notifier import TelegramNotifier
from anomaly_detector import AnomalyAlert
from datetime import datetime

async def test_group_chat():
    """Test with group chat ID"""
    print("🔧 Testing group chat setup...")
    
    # Update to group chat ID
    os.environ['TELEGRAM_BOT_TOKEN'] = '8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY'
    os.environ['TELEGRAM_CHAT_ID'] = '-1002327706087'  # Group chat ID
    
    notifier = TelegramNotifier()
    
    if notifier.is_configured():
        print("✅ Bot configured with group chat ID")
        
        # Send test message
        success = await notifier.send_test_message()
        if success:
            print("✅ Group chat test message sent!")
        else:
            print("❌ Group chat test failed")
        
        # Send fake alert
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
        
        success = await notifier.send_alert(fake_alert)
        if success:
            print("✅ Group chat alert sent!")
        else:
            print("❌ Group chat alert failed")
    else:
        print("❌ Bot not configured")

if __name__ == "__main__":
    asyncio.run(test_group_chat())
