#!/usr/bin/env python3
"""
Test bot in new channel
"""
import asyncio
import os
from telegram_notifier import TelegramNotifier

async def test_new_channel():
    """Test bot in new channel"""
    print("🔧 Testing bot in new channel...")
    
    # Your bot token
    bot_token = "8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY"
    
    print("📋 INSTRUCTIONS:")
    print("1. Add your bot to the new channel")
    print("2. Make the bot an admin")
    print("3. Send a message in the channel")
    print("4. Then run this script again")
    print()
    
    # Try to find the channel ID
    import requests
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            print("📋 Recent messages:")
            for update in data['result'][-5:]:
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
                    
                    # If it's a channel, test it
                    if chat_type == 'channel':
                        print(f"🎯 FOUND CHANNEL: {chat_title}")
                        print(f"   Channel ID: {chat_id}")
                        print()
                        
                        # Test sending to this channel
                        os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
                        os.environ['TELEGRAM_CHAT_ID'] = str(chat_id)
                        
                        notifier = TelegramNotifier()
                        if notifier.is_configured():
                            print("✅ Bot configured for channel")
                            success = await notifier.send_test_message()
                            if success:
                                print("✅ Test message sent to channel!")
                            else:
                                print("❌ Failed to send to channel")
                        else:
                            print("❌ Bot not configured")
                        break
            else:
                print("❌ No channels found")
                print("💡 Make sure you:")
                print("   1. Added the bot to your channel")
                print("   2. Made the bot an admin")
                print("   3. Sent a message in the channel")
        else:
            print("❌ No recent messages found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_new_channel())
