#!/usr/bin/env python3
"""
Use the current working group chat
"""
import asyncio
import os
from telegram_notifier import TelegramNotifier
from anomaly_detector import AnomalyAlert
from datetime import datetime

async def use_current_group():
    """Use the current working group chat"""
    print("🔧 Using current working group chat...")
    
    # Use the current working group chat ID
    os.environ['TELEGRAM_BOT_TOKEN'] = '8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY'
    os.environ['TELEGRAM_CHAT_ID'] = '-1002327706087'  # Your current working group
    
    notifier = TelegramNotifier()
    
    if notifier.is_configured():
        print("✅ Bot configured with current group chat")
        
        # Send test message
        print("📤 Sending test message...")
        success = await notifier.send_test_message()
        if success:
            print("✅ Test message sent to group!")
        else:
            print("❌ Test message failed")
        
        # Send fake alert
        print("📤 Sending fake alert...")
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
            print("✅ Fake alert sent to group!")
        else:
            print("❌ Fake alert failed")
        
        print("\n🎯 TO UPDATE STREAMLIT CLOUD:")
        print("1. Go to your Streamlit app")
        print("2. Click 'Manage app' → 'Settings' → 'Secrets'")
        print("3. Update TELEGRAM_CHAT_ID to: -1002327706087")
        print("4. Save and restart the app")
        
    else:
        print("❌ Bot not configured")

if __name__ == "__main__":
    asyncio.run(use_current_group())
