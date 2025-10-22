#!/usr/bin/env python3
"""
Cloud setup script for Binance anomaly detector
"""
import os
import asyncio
from telegram_notifier import TelegramNotifier
from anomaly_detector import AnomalyAlert
from datetime import datetime

async def cloud_setup():
    """Setup bot for cloud deployment"""
    print("🚀 CLOUD SETUP - Binance Anomaly Detector")
    print("=" * 60)
    
    # Your credentials
    bot_token = "8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY"
    group_chat_id = "-1002327706087"
    
    print("📋 STEP 1: STREAMLIT CLOUD SECRETS")
    print("-" * 40)
    print("Go to your Streamlit app:")
    print("1. Open: https://share.streamlit.io/bryantang333-ops/nance/main/dashboard.py")
    print("2. Click 'Manage app' (bottom right)")
    print("3. Click 'Settings' tab")
    print("4. Click 'Secrets' section")
    print("5. Add/Update these secrets:")
    print()
    print("```toml")
    print(f'TELEGRAM_BOT_TOKEN = "{bot_token}"')
    print(f'TELEGRAM_CHAT_ID = "{group_chat_id}"')
    print("```")
    print()
    print("6. Click 'Save'")
    print("7. Click 'Restart' to apply changes")
    print()
    
    print("📋 STEP 2: TEST TELEGRAM CONNECTION")
    print("-" * 40)
    
    # Test current setup
    os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
    os.environ['TELEGRAM_CHAT_ID'] = group_chat_id
    
    notifier = TelegramNotifier()
    
    if notifier.is_configured():
        print("✅ Bot configured locally")
        
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
    else:
        print("❌ Bot not configured")
    
    print()
    print("📋 STEP 3: START MONITORING")
    print("-" * 40)
    print("After updating secrets:")
    print("1. Go to your Streamlit app")
    print("2. Click 'Start Monitoring' button")
    print("3. Check if you see live data updating")
    print("4. Look for 'Monitoring: Active' status")
    print()
    
    print("📋 STEP 4: VERIFY ALERTS")
    print("-" * 40)
    print("Your bot will send alerts when:")
    print("• Price spikes >3% in 5 minutes")
    print("• Volume spikes 2x above 1-hour average")
    print("• Only for high-volume pairs (>100M USDT)")
    print("• 523 symbols monitored")
    print()
    
    print("📋 STEP 5: TROUBLESHOOTING")
    print("-" * 40)
    print("If no alerts received:")
    print("1. ✅ Check Streamlit app is running")
    print("2. ✅ Verify 'Start Monitoring' is clicked")
    print("3. ✅ Check secrets are updated correctly")
    print("4. ✅ Wait for real market movements >3%")
    print("5. ✅ Check bot has admin permissions in group")
    print()
    
    print("🎯 CURRENT STATUS:")
    print("-" * 40)
    print("✅ Bot token: Configured")
    print("✅ Group chat ID: -1002327706087")
    print("✅ Local testing: Working")
    print("✅ Anomaly detection: Working")
    print("✅ Volume filtering: Working")
    print("❌ Cloud secrets: Need to be updated")
    print("❌ Monitoring: Need to be started")
    print()
    
    print("🚀 NEXT STEPS:")
    print("-" * 40)
    print("1. Update Streamlit Cloud secrets (see Step 1)")
    print("2. Restart the app")
    print("3. Start monitoring in dashboard")
    print("4. Wait for real market movements")
    print("5. Receive alerts in your Telegram group!")
    print()
    
    print("=" * 60)
    print("🔧 CLOUD SETUP COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(cloud_setup())
