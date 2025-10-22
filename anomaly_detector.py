"""
Anomaly detection algorithms for price, volume, and open interest
Fixed import issues for Streamlit Cloud deployment
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import asyncio

from config import (
    PRICE_SPIKE_THRESHOLD, VOLUME_SPIKE_THRESHOLD, OI_CHANGE_THRESHOLD,
    PRICE_WINDOW, VOLUME_WINDOW, OI_WINDOW, TELEGRAM_ENABLED,
    MIN_24H_VOLUME_USDT
)

logger = logging.getLogger(__name__)

@dataclass
class AnomalyAlert:
    """Data class for anomaly alerts"""
    symbol: str
    alert_type: str  # 'price_spike', 'volume_spike', 'oi_change'
    severity: str    # 'low', 'medium', 'high', 'extreme'
    value: float
    threshold: float
    percentage_change: float
    timestamp: datetime
    description: str

class AnomalyDetector:
    """Detects anomalies in price, volume, and open interest data"""
    
    def __init__(self):
        self.price_history = {}  # symbol -> list of (timestamp, price)
        self.volume_history = {}  # symbol -> list of (timestamp, volume)
        self.oi_history = {}     # symbol -> list of (timestamp, oi)
        self.alerts = []         # list of AnomalyAlert objects
        
        # Import telegram notifier only if enabled
        if TELEGRAM_ENABLED:
            try:
                from telegram_notifier import telegram_notifier
                self.telegram_notifier = telegram_notifier
            except ImportError:
                logger.warning("Telegram notifier not available")
                self.telegram_notifier = None
        else:
            self.telegram_notifier = None
        
    def add_price_data(self, symbol: str, price: float, timestamp: datetime = None, volume_24h: float = None):
        """Add price data and check for anomalies"""
        if timestamp is None:
            timestamp = datetime.now()
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append((timestamp, price))
        
        # Keep only recent data (last 2 hours)
        cutoff_time = timestamp - timedelta(hours=2)
        self.price_history[symbol] = [
            (ts, p) for ts, p in self.price_history[symbol] 
            if ts > cutoff_time
        ]
        
        # Check for price spike (only if 24h volume meets threshold)
        alert = self._detect_price_spike(symbol, price, timestamp, volume_24h)
        if alert:
            self.alerts.append(alert)
            self._send_telegram_alert(alert)
            return alert
        
        return None
    
    def add_volume_data(self, symbol: str, volume: float, timestamp: datetime = None, volume_24h: float = None):
        """Add volume data and check for anomalies"""
        if timestamp is None:
            timestamp = datetime.now()
        
        if symbol not in self.volume_history:
            self.volume_history[symbol] = []
        
        self.volume_history[symbol].append((timestamp, volume))
        
        # Keep only recent data (last 2 hours)
        cutoff_time = timestamp - timedelta(hours=2)
        self.volume_history[symbol] = [
            (ts, v) for ts, v in self.volume_history[symbol] 
            if ts > cutoff_time
        ]
        
        # Check for volume spike (only if 24h volume meets threshold)
        alert = self._detect_volume_spike(symbol, volume, timestamp, volume_24h)
        if alert:
            self.alerts.append(alert)
            self._send_telegram_alert(alert)
            return alert
        
        return None
    
    def add_oi_data(self, symbol: str, oi: float, timestamp: datetime = None):
        """Add open interest data and check for anomalies"""
        if timestamp is None:
            timestamp = datetime.now()
        
        if symbol not in self.oi_history:
            self.oi_history[symbol] = []
        
        self.oi_history[symbol].append((timestamp, oi))
        
        # Keep only recent data (last 2 hours)
        cutoff_time = timestamp - timedelta(hours=2)
        self.oi_history[symbol] = [
            (ts, o) for ts, o in self.oi_history[symbol] 
            if ts > cutoff_time
        ]
        
        # Check for OI change
        alert = self._detect_oi_change(symbol, oi, timestamp)
        if alert:
            self.alerts.append(alert)
            self._send_telegram_alert(alert)
            return alert
        
        return None
    
    def _detect_price_spike(self, symbol: str, current_price: float, timestamp: datetime, volume_24h: float = None) -> Optional[AnomalyAlert]:
        """Detect price spikes in the last 5 minutes (only for high-volume pairs)"""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 2:
            return None
        
        # Check 24h volume threshold first
        if volume_24h is not None and volume_24h < MIN_24H_VOLUME_USDT:
            return None
        
        # Get prices from the last 5 minutes
        cutoff_time = timestamp - timedelta(minutes=PRICE_WINDOW)
        recent_prices = [
            price for ts, price in self.price_history[symbol]
            if ts >= cutoff_time and ts < timestamp
        ]
        
        if not recent_prices:
            return None
        
        # Calculate percentage change from the earliest price in the window
        earliest_price = recent_prices[0]
        price_change = (current_price - earliest_price) / earliest_price
        
        if abs(price_change) >= PRICE_SPIKE_THRESHOLD:
            severity = self._get_severity(abs(price_change), PRICE_SPIKE_THRESHOLD)
            direction = "up" if price_change > 0 else "down"
            
            volume_info = f" (24h vol: ${volume_24h/1_000_000:.1f}M)" if volume_24h else ""
            
            return AnomalyAlert(
                symbol=symbol,
                alert_type="price_spike",
                severity=severity,
                value=current_price,
                threshold=PRICE_SPIKE_THRESHOLD,
                percentage_change=price_change * 100,
                timestamp=timestamp,
                description=f"Price {direction} {abs(price_change)*100:.2f}% in {PRICE_WINDOW} minutes{volume_info}"
            )
        
        return None
    
    def _detect_volume_spike(self, symbol: str, current_volume: float, timestamp: datetime, volume_24h: float = None) -> Optional[AnomalyAlert]:
        """Detect volume spikes compared to 1-hour average (only for high-volume pairs)"""
        if symbol not in self.volume_history or len(self.volume_history[symbol]) < 10:
            return None
        
        # Check 24h volume threshold first
        if volume_24h is not None and volume_24h < MIN_24H_VOLUME_USDT:
            return None
        
        # Get volumes from the last hour
        cutoff_time = timestamp - timedelta(minutes=VOLUME_WINDOW)
        recent_volumes = [
            volume for ts, volume in self.volume_history[symbol]
            if ts >= cutoff_time and ts < timestamp
        ]
        
        if len(recent_volumes) < 5:  # Need at least 5 data points
            return None
        
        # Calculate average volume
        avg_volume = np.mean(recent_volumes)
        
        if avg_volume == 0:
            return None
        
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio >= VOLUME_SPIKE_THRESHOLD:
            severity = self._get_severity(volume_ratio, VOLUME_SPIKE_THRESHOLD)
            
            volume_info = f" (24h vol: ${volume_24h/1_000_000:.1f}M)" if volume_24h else ""
            
            return AnomalyAlert(
                symbol=symbol,
                alert_type="volume_spike",
                severity=severity,
                value=current_volume,
                threshold=VOLUME_SPIKE_THRESHOLD,
                percentage_change=(volume_ratio - 1) * 100,
                timestamp=timestamp,
                description=f"Volume {volume_ratio:.1f}x above 1-hour average{volume_info}"
            )
        
        return None
    
    def _detect_oi_change(self, symbol: str, current_oi: float, timestamp: datetime) -> Optional[AnomalyAlert]:
        """Detect significant open interest changes in the last 10 minutes"""
        if symbol not in self.oi_history or len(self.oi_history[symbol]) < 2:
            return None
        
        # Get OI from the last 10 minutes
        cutoff_time = timestamp - timedelta(minutes=OI_WINDOW)
        recent_oi = [
            oi for ts, oi in self.oi_history[symbol]
            if ts >= cutoff_time and ts < timestamp
        ]
        
        if not recent_oi:
            return None
        
        # Calculate percentage change from the earliest OI in the window
        earliest_oi = recent_oi[0]
        if earliest_oi == 0:
            return None
        
        oi_change = (current_oi - earliest_oi) / earliest_oi
        
        if abs(oi_change) >= OI_CHANGE_THRESHOLD:
            severity = self._get_severity(abs(oi_change), OI_CHANGE_THRESHOLD)
            direction = "up" if oi_change > 0 else "down"
            
            return AnomalyAlert(
                symbol=symbol,
                alert_type="oi_change",
                severity=severity,
                value=current_oi,
                threshold=OI_CHANGE_THRESHOLD,
                percentage_change=oi_change * 100,
                timestamp=timestamp,
                description=f"Open Interest {direction} {abs(oi_change)*100:.2f}% in {OI_WINDOW} minutes"
            )
        
        return None
    
    def _get_severity(self, change: float, threshold: float) -> str:
        """Determine severity based on how much the change exceeds the threshold"""
        ratio = change / threshold
        
        if ratio >= 5.0:
            return "extreme"
        elif ratio >= 3.0:
            return "high"
        elif ratio >= 2.0:
            return "medium"
        else:
            return "low"
    
    def get_recent_alerts(self, minutes: int = 60) -> List[AnomalyAlert]:
        """Get alerts from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            alert for alert in self.alerts
            if alert.timestamp >= cutoff_time
        ]
    
    def get_alerts_by_severity(self, severity: str) -> List[AnomalyAlert]:
        """Get alerts by severity level"""
        return [alert for alert in self.alerts if alert.severity == severity]
    
    def clear_old_alerts(self, hours: int = 24):
        """Clear alerts older than N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        self.alerts = [
            alert for alert in self.alerts
            if alert.timestamp >= cutoff_time
        ]
    
    def get_market_summary(self) -> Dict:
        """Get summary statistics for all monitored symbols"""
        summary = {
            'total_symbols': len(set(
                list(self.price_history.keys()) + 
                list(self.volume_history.keys()) + 
                list(self.oi_history.keys())
            )),
            'price_data_points': sum(len(data) for data in self.price_history.values()),
            'volume_data_points': sum(len(data) for data in self.volume_history.values()),
            'oi_data_points': sum(len(data) for data in self.oi_history.values()),
            'total_alerts': len(self.alerts),
            'recent_alerts': len(self.get_recent_alerts(60)),
            'extreme_alerts': len(self.get_alerts_by_severity('extreme')),
            'high_alerts': len(self.get_alerts_by_severity('high'))
        }
        return summary
    
    def _send_telegram_alert(self, alert: AnomalyAlert):
        """Send alert to Telegram if configured"""
        if self.telegram_notifier and self.telegram_notifier.is_configured():
            try:
                # Handle different thread contexts
                try:
                    # Try to get existing event loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is already running, schedule the coroutine
                        asyncio.create_task(self.telegram_notifier.send_alert(alert))
                    else:
                        # If no loop is running, run it
                        loop.run_until_complete(self.telegram_notifier.send_alert(alert))
                except RuntimeError:
                    # No event loop in this thread, create a new one
                    asyncio.run(self.telegram_notifier.send_alert(alert))
            except Exception as e:
                logger.error(f"Failed to send Telegram alert: {e}")
    
    async def send_startup_notification(self):
        """Send startup notification to Telegram"""
        if self.telegram_notifier and self.telegram_notifier.is_configured():
            try:
                await self.telegram_notifier.send_startup_message()
            except Exception as e:
                logger.error(f"Failed to send startup notification: {e}")
    
    async def send_shutdown_notification(self):
        """Send shutdown notification to Telegram"""
        if self.telegram_notifier and self.telegram_notifier.is_configured():
            try:
                await self.telegram_notifier.send_shutdown_message()
            except Exception as e:
                logger.error(f"Failed to send shutdown notification: {e}")
    
    async def send_test_notification(self):
        """Send test notification to Telegram"""
        if self.telegram_notifier and self.telegram_notifier.is_configured():
            try:
                return await self.telegram_notifier.send_test_message()
            except Exception as e:
                logger.error(f"Failed to send test notification: {e}")
                return False
        return False