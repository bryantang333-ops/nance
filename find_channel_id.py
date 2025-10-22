#!/usr/bin/env python3
"""
Find the new channel ID from recent messages
"""
import requests
import json

def find_channel_id():
    """Find the channel ID from recent messages"""
    print("🔍 Finding your new channel ID...")
    
    bot_token = "8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY"
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('ok') and data.get('result'):
            print("📋 Recent messages:")
            print("-" * 50)
            
            # Get the most recent messages
            recent_updates = data['result'][-10:]  # Last 10 messages
            
            for i, update in enumerate(recent_updates):
                if 'message' in update:
                    msg = update['message']
                    chat = msg.get('chat', {})
                    chat_id = chat.get('id')
                    chat_type = chat.get('type')
                    chat_title = chat.get('title', 'Private Chat')
                    text = msg.get('text', 'No text')
                    date = msg.get('date', 0)
                    
                    # Convert timestamp to readable date
                    from datetime import datetime
                    readable_date = datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M:%S')
                    
                    print(f"{i+1:2d}. Chat ID: {chat_id}")
                    print(f"    Type: {chat_type}")
                    print(f"    Title: {chat_title}")
                    print(f"    Text: {text[:50]}...")
                    print(f"    Time: {readable_date}")
                    print()
            
            # Find channel messages (type = 'channel')
            channels = []
            for update in data['result']:
                if 'message' in update:
                    msg = update['message']
                    chat = msg.get('chat', {})
                    if chat.get('type') == 'channel':
                        channels.append({
                            'id': chat.get('id'),
                            'title': chat.get('title'),
                            'text': msg.get('text', ''),
                            'date': msg.get('date', 0)
                        })
            
            if channels:
                print("🎯 CHANNELS FOUND:")
                print("-" * 30)
                for i, channel in enumerate(channels):
                    readable_date = datetime.fromtimestamp(channel['date']).strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{i+1}. Channel ID: {channel['id']}")
                    print(f"   Title: {channel['title']}")
                    print(f"   Last message: {channel['text'][:50]}...")
                    print(f"   Time: {readable_date}")
                    print()
                
                # Get the most recent channel
                latest_channel = max(channels, key=lambda x: x['date'])
                print(f"✅ LATEST CHANNEL:")
                print(f"   Channel ID: {latest_channel['id']}")
                print(f"   Title: {latest_channel['title']}")
                print()
                print("🔧 TO UPDATE YOUR BOT:")
                print(f"   Update TELEGRAM_CHAT_ID to: {latest_channel['id']}")
                
            else:
                print("❌ No channels found in recent messages")
                print("💡 Make sure you:")
                print("   1. Added the bot to your channel")
                print("   2. Made the bot an admin")
                print("   3. Sent a message in the channel")
                print("   4. Then run this script again")
                
        else:
            print("❌ No recent messages found")
            print("💡 Send a message to your bot in the channel, then run this script again")
            
    except Exception as e:
        print(f"❌ Error getting updates: {e}")

if __name__ == "__main__":
    find_channel_id()
