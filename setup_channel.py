#!/usr/bin/env python3
"""
Setup bot for the new Binance anomaly alerts channel
"""
import asyncio
import os
import requests
from telegram_notifier import TelegramNotifier
from anomaly_detector import AnomalyAlert
from datetime import datetime

async def setup_channel():
    """Setup bot for the new channel"""
    print("🔧 Setting up bot for Binance anomaly alerts channel...")
    print("Channel: https://t.me/+IHdt-As3CFpmNTk9")
    print()
    
    bot_token = "8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY"
    
    print("📋 STEP-BY-STEP SETUP:")
    print("1. Go to your channel: https://t.me/+IHdt-As3CFpmNTk9")
    print("2. Click 'Manage Channel' (or channel settings)")
    print("3. Click 'Administrators'")
    print("4. Click 'Add Admin'")
    print("5. Search for your bot and add it")
    print("6. Give it 'Post Messages' permission")
    print("7. Send a test message in the channel")
    print("8. Then run this script again")
    print()
    
    # Check for recent messages
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            print("📋 Recent messages:")
            channels_found = []
            
            for update in data['result'][-10:]:
                if 'message' in update:
                    msg = update['message']
                    chat = msg.get('chat', {})
                    chat_id = chat.get('id')
                    chat_type = chat.get('type')
                    chat_title = chat.get('title', 'Private')
                    text = msg.get('text', 'No text')
                    
                    print(f"   Chat ID: {chat_id}")
                    print(f"   Type: {chat_type}")
                    print(f"   Title: {chat_title}")
                    print(f"   Text: {text[:50]}...")
                    print()
                    
                    if chat_type == 'channel':
                        channels_found.append({
                            'id': chat_id,
                            'title': chat_title,
                            'text': text
                        })
            
            if channels_found:
                print("🎯 CHANNELS FOUND:")
                for i, channel in enumerate(channels_found):
                    print(f"{i+1}. {channel['title']}")
                    print(f"   Channel ID: {channel['id']}")
                    print(f"   Last message: {channel['text'][:50]}...")
                    print()
                
                # Test the most recent channel
                latest_channel = channels_found[0]
                print(f"✅ TESTING CHANNEL: {latest_channel['title']}")
                print(f"   Channel ID: {latest_channel['id']}")
                
                # Set up bot for this channel
                os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
                os.environ['TELEGRAM_CHAT_ID'] = str(latest_channel['id'])
                
                notifier = TelegramNotifier()
                if notifier.is_configured():
                    print("✅ Bot configured for channel")
                    
                    # Send test message
                    print("📤 Sending test message...")
                    success = await notifier.send_test_message()
                    if success:
                        print("✅ Test message sent to channel!")
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
                        print("✅ Fake alert sent to channel!")
                        print()
                        print("🎯 TO UPDATE STREAMLIT CLOUD:")
                        print(f"1. Go to your Streamlit app")
                        print(f"2. Click 'Manage app' → 'Settings' → 'Secrets'")
                        print(f"3. Update TELEGRAM_CHAT_ID to: {latest_channel['id']}")
                        print(f"4. Save and restart the app")
                    else:
                        print("❌ Fake alert failed")
                else:
                    print("❌ Bot not configured")
            else:
                print("❌ No channels found")
                print("💡 Make sure you:")
                print("   1. Added the bot to your channel")
                print("   2. Made the bot an admin")
                print("   3. Sent a message in the channel")
                print("   4. Then run this script again")
        else:
            print("❌ No recent messages found")
            print("💡 Send a message to your bot in the channel, then run this script again")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(setup_channel())
