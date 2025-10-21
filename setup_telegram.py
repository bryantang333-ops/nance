#!/usr/bin/env python3
"""
Telegram bot setup helper script
"""
import os
import asyncio
from telegram_notifier import TelegramNotifier

def main():
    print("🤖 Binance Anomaly Detector - Telegram Setup")
    print("=" * 50)
    
    print("\n📋 Step 1: Create a Telegram Bot")
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot")
    print("3. Choose a name for your bot")
    print("4. Choose a username (must end with 'bot')")
    print("5. Copy the bot token you receive")
    
    print("\n💬 Step 2: Get Your Chat ID")
    print("1. Start a chat with your new bot")
    print("2. Send any message to the bot")
    print("3. Visit: https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates")
    print("4. Find your chat ID in the response")
    
    print("\n⚙️ Step 3: Configure the Application")
    
    bot_token = input("\nEnter your bot token: ").strip()
    chat_id = input("Enter your chat ID: ").strip()
    
    if not bot_token or not chat_id:
        print("❌ Both bot token and chat ID are required!")
        return
    
    # Set environment variables
    os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
    os.environ['TELEGRAM_CHAT_ID'] = chat_id
    
    print("\n🧪 Testing Telegram connection...")
    
    async def test_connection():
        notifier = TelegramNotifier()
        if notifier.is_configured():
            print("✅ Telegram bot configured successfully!")
            
            # Send test message
            success = await notifier.send_test_message()
            if success:
                print("✅ Test message sent! Check your Telegram.")
            else:
                print("❌ Failed to send test message")
        else:
            print("❌ Telegram configuration failed")
    
    try:
        asyncio.run(test_connection())
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n💾 To make this permanent, create a .env file with:")
    print(f"TELEGRAM_BOT_TOKEN={bot_token}")
    print(f"TELEGRAM_CHAT_ID={chat_id}")
    
    print("\n🚀 You're all set! Start the application with:")
    print("python3 -m streamlit run dashboard.py")

if __name__ == "__main__":
    main()
