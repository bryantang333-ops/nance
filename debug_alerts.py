#!/usr/bin/env python3
"""
Debug why alerts are not being received
"""
import asyncio
import os
from telegram_notifier import TelegramNotifier
from anomaly_detector import AnomalyAlert
from datetime import datetime

async def debug_alerts():
    """Debug alert system"""
    print("🔍 DEBUGGING ALERT SYSTEM")
    print("=" * 50)
    
    # Test 1: Check if bot can send to group
    print("\n📱 1. TESTING TELEGRAM BOT")
    print("-" * 30)
    
    os.environ['TELEGRAM_BOT_TOKEN'] = '8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY'
    os.environ['TELEGRAM_CHAT_ID'] = '-1002327706087'  # Your group chat
    
    notifier = TelegramNotifier()
    
    if notifier.is_configured():
        print("✅ Bot configured")
        
        # Send test message
        print("📤 Sending test message...")
        success = await notifier.send_test_message()
        if success:
            print("✅ Test message sent successfully!")
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
            print("✅ Fake alert sent successfully!")
        else:
            print("❌ Fake alert failed")
    else:
        print("❌ Bot not configured")
    
    # Test 2: Check anomaly detection
    print("\n🚨 2. TESTING ANOMALY DETECTION")
    print("-" * 30)
    
    from anomaly_detector import AnomalyDetector
    detector = AnomalyDetector()
    
    # Test price spike detection
    print("📊 Testing price spike detection...")
    detector.add_price_data("BTCUSDT", 44000.0, volume_24h=500_000_000)  # Base price
    detector.add_price_data("BTCUSDT", 44100.0, volume_24h=500_000_000)  # Small change
    alert = detector.add_price_data("BTCUSDT", 46500.0, volume_24h=500_000_000)  # 5.7% spike
    
    if alert:
        print(f"✅ Price spike detected: {alert.description}")
    else:
        print("❌ Price spike not detected")
    
    # Test volume filtering
    print("📊 Testing volume filtering...")
    detector.add_price_data("SMALLCOIN", 0.001, volume_24h=50_000_000)  # Low volume
    detector.add_price_data("SMALLCOIN", 0.002, volume_24h=50_000_000)  # 100% spike
    alert2 = detector.add_price_data("SMALLCOIN", 0.003, volume_24h=50_000_000)
    
    if alert2:
        print("❌ Volume filtering not working (low volume alert sent)")
    else:
        print("✅ Volume filtering working (low volume filtered)")
    
    # Test 3: Check Streamlit Cloud status
    print("\n🌐 3. STREAMLIT CLOUD STATUS")
    print("-" * 30)
    
    import requests
    try:
        # Check if your Streamlit app is running
        streamlit_url = "https://share.streamlit.io/bryantang333-ops/nance/main/dashboard.py"
        response = requests.get(streamlit_url, timeout=10)
        if response.status_code == 200:
            print("✅ Streamlit app is running")
        else:
            print(f"❌ Streamlit app issue: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach Streamlit app: {e}")
        print("   💡 App might be sleeping or down")
    
    # Test 4: Check Binance API
    print("\n📊 4. BINANCE API STATUS")
    print("-" * 30)
    
    try:
        response = requests.get("https://fapi.binance.com/fapi/v1/ping", timeout=5)
        if response.status_code == 200:
            print("✅ Binance API connected")
        else:
            print(f"❌ Binance API issue: {response.status_code}")
    except Exception as e:
        print(f"❌ Binance API error: {e}")
    
    # Test 5: Check if monitoring is started
    print("\n🔄 5. MONITORING STATUS")
    print("-" * 30)
    print("💡 To check if monitoring is started:")
    print("   1. Go to your Streamlit app")
    print("   2. Look for 'Start Monitoring' button")
    print("   3. Click it if not already started")
    print("   4. Check if you see live data updating")
    
    # Test 6: Check alert thresholds
    print("\n📈 6. ALERT THRESHOLDS")
    print("-" * 30)
    print("Current thresholds:")
    print("   • Price spike: >3% in 5 minutes")
    print("   • Volume spike: 2x above 1-hour average")
    print("   • 24h volume filter: >100M USDT")
    print("   • Only high-volume pairs trigger alerts")
    
    print("\n🎯 POSSIBLE REASONS FOR NO ALERTS:")
    print("-" * 30)
    print("1. ❌ Streamlit app not running or sleeping")
    print("2. ❌ Monitoring not started in dashboard")
    print("3. ❌ No real market movements >3%")
    print("4. ❌ All movements in low-volume pairs (<100M USDT)")
    print("5. ❌ Wrong chat ID in Streamlit secrets")
    print("6. ❌ Bot not properly configured in cloud")
    
    print("\n🔧 SOLUTIONS:")
    print("-" * 30)
    print("1. ✅ Check Streamlit app is running")
    print("2. ✅ Click 'Start Monitoring' in dashboard")
    print("3. ✅ Update Streamlit secrets with correct chat ID")
    print("4. ✅ Wait for real market movements")
    print("5. ✅ Check if bot has admin permissions in group")

if __name__ == "__main__":
    asyncio.run(debug_alerts())
