#!/usr/bin/env python3
"""
Test script to verify all pairs monitoring
"""
import os
from binance_client import BinanceClient

def test_all_pairs():
    """Test that we're monitoring many more pairs"""
    print("🔍 Testing All Pairs Monitoring")
    print("=" * 50)
    
    client = BinanceClient()
    
    # Get symbols
    print("📊 Loading symbols...")
    symbols = client.get_usdt_futures_symbols()
    print(f"Found {len(symbols)} symbols")
    
    # Check for specific pairs
    test_pairs = [
        "BTCUSDT", "ETHUSDT", "COAIUSDT", "ZECUSDT", "DOGEUSDT", "ADAUSDT",
        "SOLUSDT", "AVAXUSDT", "LINKUSDT", "TONUSDT", "MATICUSDT", "DOTUSDT",
        "LTCUSDT", "UNIUSDT", "ATOMUSDT", "FILUSDT", "TRXUSDT", "ETCUSDT",
        "XLMUSDT", "XMRUSDT", "DASHUSDT", "XTZUSDT", "IOTAUSDT", "BATUSDT",
        "VETUSDT", "THETAUSDT", "ALGOUSDT", "ZILUSDT", "KSMUSDT", "AAVEUSDT",
        "SUSHIUSDT", "COMPUSDT", "YFIUSDT", "SNXUSDT", "MKRUSDT", "CRVUSDT",
        "1INCHUSDT", "GRTUSDT", "ENJUSDT", "CHZUSDT", "HOTUSDT", "MANAUSDT",
        "SANDUSDT", "AXSUSDT", "GALAUSDT", "FLOWUSDT", "ICPUSDT", "NEARUSDT",
        "FTMUSDT", "ROSEUSDT", "HBARUSDT", "EGLDUSDT", "ONEUSDT", "HARMONYUSDT"
    ]
    
    print(f"\n🎯 Checking for {len(test_pairs)} test pairs:")
    found_pairs = []
    missing_pairs = []
    
    for pair in test_pairs:
        if pair in symbols:
            found_pairs.append(pair)
            print(f"✅ {pair}")
        else:
            missing_pairs.append(pair)
            print(f"❌ {pair}")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Found: {len(found_pairs)} pairs")
    print(f"❌ Missing: {len(missing_pairs)} pairs")
    print(f"📈 Total symbols: {len(symbols)}")
    
    if len(found_pairs) > 50:
        print("🎉 EXCELLENT! Bot is monitoring many pairs!")
    elif len(found_pairs) > 20:
        print("✅ GOOD! Bot is monitoring a good number of pairs")
    else:
        print("⚠️ LIMITED! Bot is only monitoring a few pairs")
    
    # Show first 30 symbols
    print(f"\n📋 First 30 symbols:")
    for i, symbol in enumerate(symbols[:30]):
        print(f"{i+1:2d}. {symbol}")
    
    if len(symbols) > 30:
        print(f"... and {len(symbols) - 30} more symbols")
    
    print(f"\n🎯 ALERT CRITERIA:")
    print("• Price spikes >3% in 5 minutes")
    print("• Volume spikes 2x above 1-hour average")
    print("• 24h volume filter: >100M USDT")
    print("• ANY pair meeting criteria will trigger alerts")
    
    return symbols

if __name__ == "__main__":
    test_all_pairs()
