#!/usr/bin/env python3
"""
Fix Telegram bot for group chats and channels
"""
import os
import asyncio
from telegram_notifier import TelegramNotifier
from anomaly_detector import AnomalyAlert
from datetime import datetime

async def test_telegram_setup():
    """Test Telegram bot in different scenarios"""
    print("🔧 Fixing Telegram bot setup...")
    
    # Your current credentials
    bot_token = "8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY"
    chat_id = "751872795"  # This might be wrong for group chats
    
    print(f"🤖 Bot Token: {bot_token[:10]}...")
    print(f"💬 Current Chat ID: {chat_id}")
    
    # Test 1: Private chat
    print("\n📱 Test 1: Private Chat")
    os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
    os.environ['TELEGRAM_CHAT_ID'] = chat_id
    
    notifier = TelegramNotifier()
    
    if notifier.is_configured():
        print("✅ Bot configured")
        success = await notifier.send_test_message()
        if success:
            print("✅ Private chat test message sent!")
        else:
            print("❌ Private chat test failed")
    else:
        print("❌ Bot not configured")
    
    # Test 2: Get updates to find correct chat IDs
    print("\n🔍 Test 2: Finding Chat IDs")
    try:
        import requests
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            print("📋 Recent messages:")
            for update in data['result'][-5:]:  # Last 5 messages
                if 'message' in update:
                    msg = update['message']
                    chat = msg.get('chat', {})
                    print(f"  Chat ID: {chat.get('id')} | Type: {chat.get('type')} | Title: {chat.get('title', 'Private')}")
        else:
            print("❌ No recent messages found")
            print("💡 Send a message to your bot first, then run this script again")
    except Exception as e:
        print(f"❌ Error getting updates: {e}")
    
    print("\n" + "="*50)
    print("🔧 SOLUTIONS:")
    print("="*50)
    
    print("\n1️⃣ PRIVATE CHAT (Recommended):")
    print("   • Message your bot directly: @YourBotName")
    print("   • Use the chat ID from getUpdates")
    print("   • Most reliable method")
    
    print("\n2️⃣ GROUP CHAT:")
    print("   • Add bot to group")
    print("   • Make bot admin (optional but recommended)")
    print("   • Send /start in the group")
    print("   • Use group chat ID (usually negative number)")
    
    print("\n3️⃣ CHANNEL:")
    print("   • Create a channel")
    print("   • Add bot as admin")
    print("   • Post a message in channel")
    print("   • Use channel chat ID")
    
    print("\n4️⃣ FIND CORRECT CHAT ID:")
    print("   • Send message to bot/group/channel")
    print("   • Run: python3 fix_telegram.py")
    print("   • Look for the chat ID in the output")
    print("   • Update your .env file with correct chat ID")

if __name__ == "__main__":
    asyncio.run(test_telegram_setup())
