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
    BINANCE_BASE_URL, BINANCE_WS_URL, MAX_REQUESTS_PER_MINUTE, 
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
        """Get all USDT perpetual futures symbols"""
        try:
            self.rate_limiter.wait()
            response = self.session.get(f"{BINANCE_BASE_URL}/fapi/v1/exchangeInfo")
            response.raise_for_status()
            
            data = response.json()
            symbols = []
            for symbol_info in data['symbols']:
                if (symbol_info['status'] == 'TRADING' and 
                    symbol_info['quoteAsset'] == 'USDT' and 
                    symbol_info['contractType'] == 'PERPETUAL'):
                    symbols.append(symbol_info['symbol'])
            
            logger.info(f"Found {len(symbols)} USDT perpetual futures symbols")
            return symbols
            
        except Exception as e:
            logger.error(f"Error fetching symbols: {e}")
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
    
    def get_open_interest(self, symbol: str) -> Optional[Dict]:
        """Get open interest for a symbol"""
        try:
            self.rate_limiter.wait()
            response = self.session.get(f"{BINANCE_BASE_URL}/fapi/v1/openInterest", 
                                      params={'symbol': symbol})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching open interest for {symbol}: {e}")
            return None
    
    def start_websocket(self, symbol: str, callback: Callable):
        """Start WebSocket connection for a symbol"""
        if symbol in self.ws_connections:
            logger.warning(f"WebSocket already exists for {symbol}")
            return
        
        stream_name = f"{symbol.lower()}@ticker"
        ws_url = f"{BINANCE_WS_URL}{stream_name}"
        
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
