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

# Anomaly Detection Thresholds
PRICE_SPIKE_THRESHOLD = 0.03  # 3% price spike in 5 minutes
VOLUME_SPIKE_THRESHOLD = 2.0  # 2x volume above 1-hour average
OI_CHANGE_THRESHOLD = 0.10    # 10% OI change in 10 minutes

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

# Telegram Alert Settings
TELEGRAM_SEND_EXTREME = True
TELEGRAM_SEND_HIGH = True
TELEGRAM_SEND_MEDIUM = False
TELEGRAM_SEND_LOW = False
TELEGRAM_BATCH_SIZE = 10  # Send alerts in batches
TELEGRAM_RATE_LIMIT = 1.0  # seconds between messages
