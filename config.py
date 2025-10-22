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

# Production Settings - User Specified Conditions
PRICE_SPIKE_THRESHOLD = 0.10  # 10% price spike in 5 minutes (extreme moves only)
VOLUME_SPIKE_THRESHOLD = 5.0  # 5x volume above 1-hour average (massive spikes)
OI_CHANGE_THRESHOLD = 0.20    # 20% OI change in 10 minutes
MIN_24H_VOLUME_USDT = 250_000_000  # Minimum 24h volume in USDT (250M)
MIN_MARKET_CAP_USDT = 100_000_000  # 100M market cap minimum (established tokens only)

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
# Re-enabled with proper restrictive settings
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# Production Telegram Settings - User Specified
TELEGRAM_SEND_EXTREME = True
TELEGRAM_SEND_HIGH = True    # Send high severity alerts
TELEGRAM_SEND_MEDIUM = True  # Send medium severity alerts  
TELEGRAM_SEND_LOW = False    # Block low severity alerts
TELEGRAM_BATCH_SIZE = 1  # Send one alert at a time
TELEGRAM_RATE_LIMIT = 300.0  # 5 MINUTES between messages (very conservative)
ALERT_COOLDOWN_HOURS = 24  # 24-hour cooldown for same ticker
