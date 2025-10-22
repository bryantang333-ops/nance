#!/usr/bin/env python3
"""
Test script to check what symbols are being loaded
"""
import os
from binance_client import BinanceClient

def test_symbol_loading():
    """Test what symbols are being loaded"""
    print("🔍 Testing symbol loading...")
    
    client = BinanceClient()
    
    # Get USDT symbols
    print("\n📊 Loading USDT perpetual futures symbols...")
    usdt_symbols = client.get_usdt_futures_symbols()
    print(f"Found {len(usdt_symbols)} USDT symbols")
    
    # Check for specific symbols
    test_symbols = ["COAIUSDT", "ZECUSDT", "BTCUSDT", "ETHUSDT"]
    print(f"\n🎯 Checking for specific symbols:")
    for symbol in test_symbols:
        if symbol in usdt_symbols:
            print(f"✅ {symbol} - FOUND")
        else:
            print(f"❌ {symbol} - NOT FOUND")
    
    # Show first 20 symbols
    print(f"\n📋 First 20 symbols loaded:")
    for i, symbol in enumerate(usdt_symbols[:20]):
        print(f"{i+1:2d}. {symbol}")
    
    if len(usdt_symbols) > 20:
        print(f"... and {len(usdt_symbols) - 20} more symbols")
    
    # Get COIN-M symbols
    print(f"\n🪙 Loading COIN-M perpetual futures symbols...")
    coinm_symbols = client.get_coinm_futures_symbols()
    print(f"Found {len(coinm_symbols)} COIN-M symbols")
    
    if coinm_symbols:
        print(f"First 10 COIN-M symbols:")
        for i, symbol in enumerate(coinm_symbols[:10]):
            print(f"{i+1:2d}. {symbol}")
    
    # Total symbols
    all_symbols = list(set(usdt_symbols + coinm_symbols))
    print(f"\n📈 Total unique symbols: {len(all_symbols)}")
    
    return usdt_symbols, coinm_symbols

if __name__ == "__main__":
    test_symbol_loading()
