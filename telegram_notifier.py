"""
Telegram notification service for sending anomaly alerts
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional, List
from telegram import Bot
from telegram.error import TelegramError
import os
from dotenv import load_dotenv

from anomaly_detector import AnomalyAlert

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Telegram bot for sending anomaly alerts"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = None
        self.is_enabled = bool(self.bot_token and self.chat_id)
        
        if self.is_enabled:
            try:
                self.bot = Bot(token=self.bot_token)
                logger.info("Telegram notifier initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
                self.is_enabled = False
        else:
            logger.warning("Telegram notifier disabled - missing bot token or chat ID")
    
    def is_configured(self) -> bool:
        """Check if Telegram is properly configured"""
        return self.is_enabled and self.bot is not None
    
    async def send_alert(self, alert: AnomalyAlert) -> bool:
        """Send a single alert to Telegram"""
        if not self.is_configured():
            logger.warning("Telegram not configured, skipping alert")
            return False
        
        try:
            message = self._format_alert_message(alert)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            logger.info(f"Sent Telegram alert for {alert.symbol}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram alert: {e}")
            return False
    
    async def send_batch_alerts(self, alerts: List[AnomalyAlert]) -> int:
        """Send multiple alerts to Telegram with proper rate limiting"""
        if not self.is_configured():
            logger.warning("Telegram not configured, skipping batch alerts")
            return 0
        
        if not alerts:
            return 0
        
        # Group alerts by severity for better organization
        alerts_by_severity = {}
        for alert in alerts:
            if alert.severity not in alerts_by_severity:
                alerts_by_severity[alert.severity] = []
            alerts_by_severity[alert.severity].append(alert)
        
        sent_count = 0
        
        try:
            # Send summary message first
            summary_message = self._format_summary_message(alerts_by_severity)
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=summary_message,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            sent_count += 1
            
            # Rate limiting: wait between messages
            await asyncio.sleep(5.0)
            
            # Send individual alerts for extreme, high, and medium severity
            for alert in alerts:
                if alert.severity in ['extreme', 'high', 'medium']:  # Send medium and above
                    message = self._format_alert_message(alert)
                    await self.bot.send_message(
                        chat_id=self.chat_id,
                        text=message,
                        parse_mode='HTML',
                        disable_web_page_preview=True
                    )
                    sent_count += 1
                    # Very conservative rate limiting
                    await asyncio.sleep(10.0)  # 10 seconds between messages
            
            logger.info(f"Sent {sent_count} Telegram messages for {len(alerts)} alerts")
            return sent_count
            
        except TelegramError as e:
            if "Flood control exceeded" in str(e):
                logger.warning(f"Telegram flood control hit, will retry later: {e}")
                # Don't treat this as a complete failure
                return sent_count
            else:
                logger.error(f"Failed to send batch Telegram alerts: {e}")
                return sent_count
        except Exception as e:
            logger.error(f"Unexpected error sending batch Telegram alerts: {e}")
            return sent_count
    
    def _format_alert_message(self, alert: AnomalyAlert) -> str:
        """Format a single alert for Telegram"""
        # Emojis for different alert types and severities
        type_emojis = {
            'price_spike': '📈',
            'volume_spike': '📊',
            'oi_change': '🔗'
        }
        
        severity_emojis = {
            'extreme': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        type_emoji = type_emojis.get(alert.alert_type, '📋')
        severity_emoji = severity_emojis.get(alert.severity, '⚪')
        
        # Format the message
        message = f"""
{severity_emoji} <b>ANOMALY ALERT</b> {type_emoji}

<b>Symbol:</b> {alert.symbol}
<b>Type:</b> {alert.alert_type.replace('_', ' ').title()}
<b>Severity:</b> {alert.severity.upper()}
<b>Description:</b> {alert.description}
<b>Value:</b> {alert.value:,.4f}
<b>Change:</b> {alert.percentage_change:+.2f}%
<b>Time:</b> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        return message
    
    def _format_summary_message(self, alerts_by_severity: dict) -> str:
        """Format a summary message for multiple alerts"""
        total_alerts = sum(len(alerts) for alerts in alerts_by_severity.values())
        
        message = f"🚨 <b>ANOMALY DETECTION SUMMARY</b>\n\n"
        message += f"<b>Total Alerts:</b> {total_alerts}\n"
        message += f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for severity, alerts in alerts_by_severity.items():
            if alerts:
                severity_emoji = {
                    'extreme': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(severity, '⚪')
                
                message += f"{severity_emoji} <b>{severity.upper()}:</b> {len(alerts)} alerts\n"
                
                # List symbols for extreme and high severity
                if severity in ['extreme', 'high']:
                    symbols = [alert.symbol for alert in alerts]
                    message += f"   Symbols: {', '.join(symbols[:10])}"
                    if len(symbols) > 10:
                        message += f" (+{len(symbols) - 10} more)"
                    message += "\n"
        
        return message
    
    async def send_test_message(self) -> bool:
        """Send a test message to verify configuration"""
        if not self.is_configured():
            return False
        
        try:
            test_message = """
🤖 <b>Binance Anomaly Detector</b>

✅ Telegram notifications are working!

This is a test message to verify your bot configuration.

<b>Status:</b> Connected
<b>Time:</b> {time}
            """.format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=test_message,
                parse_mode='HTML'
            )
            logger.info("Test message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send test message: {e}")
            return False
    
    async def send_startup_message(self) -> bool:
        """Send a startup notification"""
        if not self.is_configured():
            return False
        
        try:
            startup_message = """
🚀 <b>Binance Anomaly Detector Started</b>

📊 Monitoring all USDT perpetual futures pairs
🔍 Detecting price spikes, volume anomalies, and OI changes
📱 You will receive alerts for significant market movements

<b>Status:</b> Active
<b>Time:</b> {time}
            """.format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=startup_message,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send startup message: {e}")
            return False
    
    async def send_shutdown_message(self) -> bool:
        """Send a shutdown notification"""
        if not self.is_configured():
            return False
        
        try:
            shutdown_message = """
⏹️ <b>Binance Anomaly Detector Stopped</b>

Monitoring has been stopped.

<b>Status:</b> Inactive
<b>Time:</b> {time}
            """.format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=shutdown_message,
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send shutdown message: {e}")
            return False

# Global notifier instance
telegram_notifier = TelegramNotifier()
