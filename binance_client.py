"""
Binance API client for fetching market data and managing WebSocket connections
"""
import asyncio
import json
import time
import websocket
import threading
from typing import Dict, List, Callable, Optional
import requests
from datetime import datetime, timedelta
import logging

from config import (
    BINANCE_BASE_URL, BINANCE_WS_URL,
    BINANCE_COIN_BASE_URL, BINANCE_WS_URL_COIN,
    MAX_REQUESTS_PER_MINUTE,
    REQUEST_DELAY, WS_RECONNECT_DELAY, WS_MAX_RECONNECT_ATTEMPTS,
    WS_PING_INTERVAL, WS_PING_TIMEOUT
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceClient:
    """Binance API client with rate limiting and WebSocket management"""
    
    def __init__(self):
        self.session = requests.Session()
        self.rate_limiter = RateLimiter(MAX_REQUESTS_PER_MINUTE)
        self.ws_connections = {}
        self.ws_callbacks = {}
        self.reconnect_attempts = {}
        
    def get_usdt_futures_symbols(self) -> List[str]:
        """Get all USDT perpetual futures symbols with retries and safe fallback."""
        # Expanded fallback list to include many more pairs for comprehensive monitoring
        fallback_symbols = [
            # Major USDⓈ-M pairs
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", 
            "LINKUSDT", "TONUSDT", "MATICUSDT", "DOTUSDT", "LTCUSDT", "UNIUSDT", "ATOMUSDT", "FILUSDT",
            "TRXUSDT", "ETCUSDT", "XLMUSDT", "XMRUSDT", "DASHUSDT", "ZECUSDT", "XTZUSDT", "IOTAUSDT",
            "BATUSDT", "VETUSDT", "THETAUSDT", "ALGOUSDT", "ZILUSDT", "KSMUSDT", "AAVEUSDT", "SUSHIUSDT",
            "COMPUSDT", "YFIUSDT", "SNXUSDT", "MKRUSDT", "CRVUSDT", "1INCHUSDT", "GRTUSDT", "ENJUSDT",
            "CHZUSDT", "HOTUSDT", "MANAUSDT", "SANDUSDT", "AXSUSDT", "GALAUSDT", "FLOWUSDT", "ICPUSDT",
            "NEARUSDT", "FTMUSDT", "ROSEUSDT", "HBARUSDT", "EGLDUSDT", "ONEUSDT", "HARMONYUSDT", "ZENUSDT",
            "KAVAUSDT", "WAVESUSDT", "OMGUSDT", "NEOUSDT", "QTUMUSDT", "ONTUSDT", "ZRXUSDT", "REPUSDT",
            "STORJUSDT", "DGBUSDT", "SCUSDT", "ZENUSDT", "RVNUSDT", "DCRUSDT", "LSKUSDT", "NANOUSDT",
            "ICXUSDT", "WANUSDT", "AIONUSDT", "REQUSDT", "LRCUSDT", "KNCUSDT", "BNTUSDT", "LENDUSDT",
            "RENUSDT", "KMDUSDT", "ARKUSDT", "LSKUSDT", "FUNUSDT", "GNTUSDT", "REPUSDT", "STORJUSDT",
            # Additional popular pairs
            "COAIUSDT", "ZECUSDT", "DASHUSDT", "XMRUSDT", "DGBUSDT", "SCUSDT", "RVNUSDT", "DCRUSDT",
            "LSKUSDT", "NANOUSDT", "ICXUSDT", "WANUSDT", "AIONUSDT", "REQUSDT", "LRCUSDT", "KNCUSDT",
            "BNTUSDT", "LENDUSDT", "RENUSDT", "KMDUSDT", "ARKUSDT", "FUNUSDT", "GNTUSDT", "REPUSDT",
            # COIN-M pairs
            "BTCUSD_PERP", "ETHUSD_PERP", "BNBUSD_PERP", "ADAUSD_PERP", "XRPUSD_PERP", "SOLUSD_PERP",
            "DOGEUSD_PERP", "AVAXUSD_PERP", "LINKUSD_PERP", "TONUSD_PERP", "MATICUSD_PERP", "DOTUSD_PERP",
            "LTCUSD_PERP", "UNIUSD_PERP", "ATOMUSD_PERP", "FILUSD_PERP", "TRXUSD_PERP", "ETCUSD_PERP"
        ]

        # Try multiple times with different strategies to get all symbols
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                self.rate_limiter.wait()
                
                # Add headers to avoid some blocking
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
                
                response = self.session.get(
                    f"{BINANCE_BASE_URL}/fapi/v1/exchangeInfo",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 451:
                    logger.warning(f"Binance API blocked (451) - likely geographic restriction")
                    break
                    
                response.raise_for_status()

                data = response.json()
                symbols = []
                for symbol_info in data.get('symbols', []):
                    if (
                        symbol_info.get('status') == 'TRADING' and
                        symbol_info.get('quoteAsset') == 'USDT' and
                        symbol_info.get('contractType') == 'PERPETUAL'
                    ):
                        symbols.append(symbol_info['symbol'])

                if symbols:
                    logger.info(f"Found {len(symbols)} USDT perpetual futures symbols")
                    return symbols
                else:
                    logger.warning("ExchangeInfo returned no symbols; retrying...")
            except Exception as e:
                logger.warning(f"Attempt {attempt}/{max_retries} to fetch symbols failed: {e}")
                if "451" in str(e) or "blocked" in str(e).lower():
                    logger.error("Binance API is blocked - using fallback symbols only")
                    break
                time.sleep(2 * attempt)

        logger.error("Falling back to a small default symbol list due to repeated failures")
        return fallback_symbols

    def get_coinm_futures_symbols(self) -> List[str]:
        """Get all COIN-M perpetual futures symbols (e.g., BTCUSD_PERP)."""
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                self.rate_limiter.wait()
                
                # Add headers to avoid some blocking
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
                
                response = self.session.get(
                    f"{BINANCE_COIN_BASE_URL}/dapi/v1/exchangeInfo",
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 451:
                    logger.warning(f"Binance COIN-M API blocked (451) - likely geographic restriction")
                    break
                    
                response.raise_for_status()
                data = response.json()
                symbols: List[str] = []
                for s in data.get('symbols', []):
                    if s.get('status') == 'TRADING' and s.get('contractType') == 'PERPETUAL':
                        symbols.append(s['symbol'])  # e.g., BTCUSD_PERP
                if symbols:
                    logger.info(f"Found {len(symbols)} COIN-M perpetual futures symbols")
                    return symbols
            except Exception as e:
                logger.warning(f"Attempt {attempt}/{max_retries} to fetch COIN-M symbols failed: {e}")
                if "451" in str(e) or "blocked" in str(e).lower():
                    logger.error("Binance COIN-M API is blocked - skipping COIN-M symbols")
                    break
                time.sleep(2 * attempt)
        return []
    
    def get_24h_ticker(self, symbol: str) -> Optional[Dict]:
        """Get 24h ticker statistics for a symbol"""
        try:
            self.rate_limiter.wait()
            response = self.session.get(f"{BINANCE_BASE_URL}/fapi/v1/ticker/24hr", 
                                      params={'symbol': symbol})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching 24h ticker for {symbol}: {e}")
            return None
    
    def get_market_cap_estimate(self, symbol: str) -> Optional[float]:
        """Get estimated market cap for a symbol (in USDT)"""
        try:
            # For futures, we can't get exact market cap, but we can estimate from volume
            # This is a simplified approach - in production you'd want more sophisticated filtering
            ticker_data = self.get_24h_ticker(symbol)
            if not ticker_data:
                return None
            
            # Use 24h volume as a proxy for market cap estimation
            # This is not perfect but gives us a reasonable filter
            volume_24h = float(ticker_data.get('volume', 0))
            price = float(ticker_data.get('lastPrice', 0))
            
            # Estimate market cap as volume * price (very rough estimate)
            estimated_market_cap = volume_24h * price
            
            return estimated_market_cap
            
        except Exception as e:
            logger.error(f"Error estimating market cap for {symbol}: {e}")
            return None

    def diagnostics(self) -> Dict:
        """Return quick diagnostics useful for serverless debugging."""
        diags = {}
        try:
            resp = self.session.get(f"{BINANCE_BASE_URL}/fapi/v1/ping", timeout=5)
            diags['fapi_ping_status'] = resp.status_code
        except Exception as e:
            diags['fapi_ping_status'] = str(e)
        try:
            resp = self.session.get(f"{BINANCE_COIN_BASE_URL}/dapi/v1/ping", timeout=5)
            diags['dapi_ping_status'] = resp.status_code
        except Exception as e:
            diags['dapi_ping_status'] = str(e)
        return diags
    
    def start_websocket(self, symbol: str, callback: Callable):
        """Start WebSocket connection for a symbol (handles both markets)."""
        if symbol in self.ws_connections:
            logger.warning(f"WebSocket already exists for {symbol}")
            return
        
        # USDⓈ-M vs COIN-M stream base
        if symbol.endswith('USDT') or symbol.endswith('USDC'):
            ws_base = BINANCE_WS_URL
        else:
            ws_base = BINANCE_WS_URL_COIN
        stream_name = f"{symbol.lower()}@ticker"
        ws_url = f"{ws_base}{stream_name}"
        
        self.ws_callbacks[symbol] = callback
        self.reconnect_attempts[symbol] = 0
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                callback(symbol, data)
            except Exception as e:
                logger.error(f"Error processing WebSocket message for {symbol}: {e}")
        
        def on_error(ws, error):
            logger.error(f"WebSocket error for {symbol}: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logger.warning(f"WebSocket closed for {symbol}: {close_status_code} - {close_msg}")
            self._reconnect_websocket(symbol, callback)
        
        def on_open(ws):
            logger.info(f"WebSocket connected for {symbol}")
            self.reconnect_attempts[symbol] = 0
        
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )
        
        self.ws_connections[symbol] = ws
        
        # Start WebSocket in a separate thread
        def run_ws():
            ws.run_forever(
                ping_interval=WS_PING_INTERVAL,
                ping_timeout=WS_PING_TIMEOUT
            )
        
        thread = threading.Thread(target=run_ws, daemon=True)
        thread.start()
    
    def _reconnect_websocket(self, symbol: str, callback: Callable):
        """Reconnect WebSocket with exponential backoff"""
        if symbol not in self.reconnect_attempts:
            return
        
        attempts = self.reconnect_attempts[symbol]
        if attempts >= WS_MAX_RECONNECT_ATTEMPTS:
            logger.error(f"Max reconnection attempts reached for {symbol}")
            return
        
        self.reconnect_attempts[symbol] += 1
        delay = WS_RECONNECT_DELAY * (2 ** attempts)
        
        logger.info(f"Reconnecting {symbol} in {delay} seconds (attempt {attempts + 1})")
        
        def delayed_reconnect():
            time.sleep(delay)
            if symbol in self.ws_connections:
                del self.ws_connections[symbol]
            self.start_websocket(symbol, callback)
        
        thread = threading.Thread(target=delayed_reconnect, daemon=True)
        thread.start()
    
    def stop_websocket(self, symbol: str):
        """Stop WebSocket connection for a symbol"""
        if symbol in self.ws_connections:
            self.ws_connections[symbol].close()
            del self.ws_connections[symbol]
            del self.ws_callbacks[symbol]
            if symbol in self.reconnect_attempts:
                del self.reconnect_attempts[symbol]
    
    def stop_all_websockets(self):
        """Stop all WebSocket connections"""
        for symbol in list(self.ws_connections.keys()):
            self.stop_websocket(symbol)


class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, max_requests_per_minute: int):
        self.max_requests = max_requests_per_minute
        self.requests = []
        self.lock = threading.Lock()
    
    def wait(self):
        """Wait if necessary to respect rate limits"""
        with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            self.requests = [req_time for req_time in self.requests if now - req_time < 60]
            
            if len(self.requests) >= self.max_requests:
                sleep_time = 60 - (now - self.requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Clean up old requests after sleeping
                    now = time.time()
                    self.requests = [req_time for req_time in self.requests if now - req_time < 60]
            
            self.requests.append(now)
            time.sleep(REQUEST_DELAY)