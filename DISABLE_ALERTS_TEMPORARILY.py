#!/usr/bin/env python3
"""
TEMPORARY ALERT DISABLE
This will completely disable all alerts temporarily
"""
import os

# Temporarily disable all alerts
os.environ['TELEGRAM_ENABLED'] = 'False'

print("🚨 ALERTS TEMPORARILY DISABLED")
print("=" * 40)
print("All Telegram alerts are now DISABLED")
print("This will stop the spam immediately")
print("You can re-enable later with proper settings")
