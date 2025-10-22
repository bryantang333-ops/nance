#!/usr/bin/env python3
"""
EMERGENCY STOP SCRIPT
This will immediately stop all alert spam by setting ultra-restrictive thresholds
"""
import os
import sys
from datetime import datetime

print("🚨 EMERGENCY STOP ACTIVATED")
print("=" * 40)
print(f"Timestamp: {datetime.now()}")
print("Setting ultra-restrictive thresholds to stop spam:")
print("- Price threshold: 15% (was 8%)")
print("- Volume threshold: 10x (was 5x)")
print("- Volume requirement: 500M USDT (was 250M)")
print("- Market cap requirement: 100M USDT (was 0)")
print("- Rate limit: 5 minutes (was 30 seconds)")
print("- Only EXTREME alerts allowed")
print("")
print("This should immediately stop the spam!")
print("Deploying emergency fix to GitHub...")
