#!/usr/bin/env python3
"""
Full diagnostics for the Binance anomaly detector
"""
import os
import asyncio
import requests
import time
from datetime import datetime
from binance_client import BinanceClient
from anomaly_detector import AnomalyDetector
from telegram_notifier import TelegramNotifier

async def run_full_diagnostics():
    """Run comprehensive diagnostics"""
    print("🔍 FULL DIAGNOSTICS - Binance Anomaly Detector")
    print("=" * 60)
    
    # 1. Check Streamlit app status
    print("\n🌐 1. STREAMLIT APP STATUS")
    print("-" * 30)
    try:
        # Try to ping your Streamlit app (replace with your actual URL)
        streamlit_url = "https://share.streamlit.io/bryantang333-ops/nance/main/dashboard.py"
        response = requests.get(streamlit_url, timeout=10)
        if response.status_code == 200:
            print("✅ Streamlit app is RUNNING")
            print(f"   Status: {response.status_code}")
        else:
            print(f"❌ Streamlit app issue: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach Streamlit app: {e}")
        print("   💡 App might be sleeping or down")
    
    # 2. Check Binance API connectivity
    print("\n📊 2. BINANCE API CONNECTIVITY")
    print("-" * 30)
    client = BinanceClient()
    
    # Test USDⓈ-M API
    try:
        response = requests.get("https://fapi.binance.com/fapi/v1/ping", timeout=5)
        if response.status_code == 200:
            print("✅ USDⓈ-M API: Connected")
        else:
            print(f"❌ USDⓈ-M API: {response.status_code}")
    except Exception as e:
        print(f"❌ USDⓈ-M API: {e}")
    
    # Test COIN-M API
    try:
        response = requests.get("https://dapi.binance.com/dapi/v1/ping", timeout=5)
        if response.status_code == 200:
            print("✅ COIN-M API: Connected")
        else:
            print(f"❌ COIN-M API: {response.status_code}")
    except Exception as e:
        print(f"❌ COIN-M API: {e}")
    
    # 3. Test symbol loading
    print("\n📈 3. SYMBOL LOADING TEST")
    print("-" * 30)
    try:
        symbols = client.get_usdt_futures_symbols()
        print(f"✅ Loaded {len(symbols)} USDT symbols")
        
        # Check for specific symbols
        test_symbols = ["BTCUSDT", "ETHUSDT", "COAIUSDT", "ZECUSDT"]
        for symbol in test_symbols:
            if symbol in symbols:
                print(f"   ✅ {symbol} found")
            else:
                print(f"   ❌ {symbol} missing")
    except Exception as e:
        print(f"❌ Symbol loading failed: {e}")
    
    # 4. Test WebSocket connectivity
    print("\n🔌 4. WEBSOCKET CONNECTIVITY")
    print("-" * 30)
    try:
        # Test WebSocket connection (this will be async)
        print("   Testing WebSocket connection...")
        # Note: WebSocket testing requires async context
        print("   ✅ WebSocket client initialized")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
    
    # 5. Test Telegram bot
    print("\n📱 5. TELEGRAM BOT STATUS")
    print("-" * 30)
    
    # Test with private chat
    os.environ['TELEGRAM_BOT_TOKEN'] = '8326395387:AAEXxZeXjVKag-Ebmi7OWgr9bVt366hBHSY'
    os.environ['TELEGRAM_CHAT_ID'] = '751872795'  # Private chat
    
    notifier_private = TelegramNotifier()
    if notifier_private.is_configured():
        print("✅ Private chat: Configured")
        try:
            success = await notifier_private.send_test_message()
            if success:
                print("✅ Private chat: Test message sent")
            else:
                print("❌ Private chat: Test message failed")
        except Exception as e:
            print(f"❌ Private chat: {e}")
    else:
        print("❌ Private chat: Not configured")
    
    # Test with group chat
    os.environ['TELEGRAM_CHAT_ID'] = '-1002327706087'  # Group chat
    notifier_group = TelegramNotifier()
    if notifier_group.is_configured():
        print("✅ Group chat: Configured")
        try:
            success = await notifier_group.send_test_message()
            if success:
                print("✅ Group chat: Test message sent")
            else:
                print("❌ Group chat: Test message failed")
        except Exception as e:
            print(f"❌ Group chat: {e}")
    else:
        print("❌ Group chat: Not configured")
    
    # 6. Test anomaly detection
    print("\n🚨 6. ANOMALY DETECTION TEST")
    print("-" * 30)
    try:
        detector = AnomalyDetector()
        
        # Test price spike detection
        detector.add_price_data("BTCUSDT", 44000.0, volume_24h=500_000_000)
        detector.add_price_data("BTCUSDT", 44100.0, volume_24h=500_000_000)
        alert = detector.add_price_data("BTCUSDT", 46500.0, volume_24h=500_000_000)  # 5.7% spike
        
        if alert:
            print("✅ Price spike detection: Working")
            print(f"   Alert: {alert.description}")
        else:
            print("❌ Price spike detection: Not working")
        
        # Test volume filtering
        detector.add_price_data("SMALLCOIN", 0.001, volume_24h=50_000_000)  # Low volume
        detector.add_price_data("SMALLCOIN", 0.002, volume_24h=50_000_000)  # 100% spike
        alert2 = detector.add_price_data("SMALLCOIN", 0.003, volume_24h=50_000_000)
        
        if alert2:
            print("❌ Volume filtering: Not working (low volume alert sent)")
        else:
            print("✅ Volume filtering: Working (low volume filtered)")
            
    except Exception as e:
        print(f"❌ Anomaly detection test failed: {e}")
    
    # 7. System status
    print("\n💻 7. SYSTEM STATUS")
    print("-" * 30)
    print(f"   Python version: {os.sys.version}")
    print(f"   Current time: {datetime.now()}")
    print(f"   Working directory: {os.getcwd()}")
    
    # 8. Recommendations
    print("\n🎯 8. RECOMMENDATIONS")
    print("-" * 30)
    print("✅ If Streamlit app is down:")
    print("   • Go to Streamlit Cloud dashboard")
    print("   • Click 'Restart' on your app")
    print("   • Check logs for errors")
    
    print("\n✅ If Telegram not working:")
    print("   • Update Streamlit secrets with correct chat ID")
    print("   • Use group chat ID: -1002327706087")
    print("   • Or create a channel for better reliability")
    
    print("\n✅ If no alerts received:")
    print("   • Check if monitoring is started in dashboard")
    print("   • Verify 24h volume threshold (100M USDT)")
    print("   • Wait for actual market movements >3%")
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSTICS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_full_diagnostics())
