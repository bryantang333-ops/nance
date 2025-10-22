"""
Configuration settings for the Binance Anomaly Detector
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Binance API Configuration
BINANCE_BASE_URL = "https://fapi.binance.com"  # USDⓈ-M (USDT/USDC) futures
BINANCE_WS_URL = "wss://fstream.binance.com/ws/"

# COIN-Margined futures
BINANCE_COIN_BASE_URL = "https://dapi.binance.com"
BINANCE_WS_URL_COIN = "wss://dstream.binance.com/ws/"

# Application Configuration
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", 8501))
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 5))

# EMERGENCY FIX: Ultra-restrictive settings to stop spam
PRICE_SPIKE_THRESHOLD = 0.15  # 15% price spike in 5 minutes (ULTRA HIGH)
VOLUME_SPIKE_THRESHOLD = 10.0  # 10x volume above 1-hour average (ULTRA HIGH)
OI_CHANGE_THRESHOLD = 0.30    # 30% OI change in 10 minutes (ULTRA HIGH)
MIN_24H_VOLUME_USDT = 500_000_000  # Minimum 24h volume in USDT (500M - ULTRA HIGH)
MIN_MARKET_CAP_USDT = 100_000_000  # 100M market cap minimum (ULTRA HIGH)

# Time Windows (in minutes)
PRICE_WINDOW = 5
VOLUME_WINDOW = 60
OI_WINDOW = 10

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = 1200
REQUEST_DELAY = 0.05  # 50ms delay between requests

# WebSocket Configuration
WS_RECONNECT_DELAY = 5  # seconds
WS_MAX_RECONNECT_ATTEMPTS = 10
WS_PING_INTERVAL = 20  # seconds
WS_PING_TIMEOUT = 10   # seconds

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# EMERGENCY FIX: Ultra-restrictive Telegram settings
TELEGRAM_SEND_EXTREME = True
TELEGRAM_SEND_HIGH = False   # BLOCK high severity alerts
TELEGRAM_SEND_MEDIUM = False # BLOCK medium severity alerts  
TELEGRAM_SEND_LOW = False    # BLOCK low severity alerts
TELEGRAM_BATCH_SIZE = 1  # Send one alert at a time
TELEGRAM_RATE_LIMIT = 300.0  # 5 MINUTES between messages (ULTRA CONSERVATIVE)
ALERT_COOLDOWN_HOURS = 24  # 24-hour cooldown for same ticker
