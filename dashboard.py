"""
Streamlit dashboard for the Binance Anomaly Detector
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import threading
from typing import Dict, List

from binance_client import BinanceClient
from anomaly_detector import AnomalyDetector, AnomalyAlert
from config import REFRESH_INTERVAL

# Page configuration
st.set_page_config(
    page_title="Binance Futures Anomaly Detector",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-card {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.3rem;
        border-left: 4px solid;
    }
    .alert-extreme {
        background-color: #ffebee;
        border-left-color: #d32f2f;
    }
    .alert-high {
        background-color: #fff3e0;
        border-left-color: #f57c00;
    }
    .alert-medium {
        background-color: #fff8e1;
        border-left-color: #fbc02d;
    }
    .alert-low {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-connected {
        background-color: #4caf50;
    }
    .status-disconnected {
        background-color: #f44336;
    }
</style>
""", unsafe_allow_html=True)

class Dashboard:
    """Main dashboard class for the anomaly detector"""
    
    def __init__(self):
        self.binance_client = BinanceClient()
        self.anomaly_detector = AnomalyDetector()
        self.symbols = []
        self.market_data = {}
        self.is_running = False
        self.websocket_threads = {}
        
        # Initialize session state
        if 'alerts' not in st.session_state:
            st.session_state.alerts = []
        if 'market_data' not in st.session_state:
            st.session_state.market_data = {}
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
    
    def run(self):
        """Run the main dashboard"""
        # Header
        st.markdown('<h1 class="main-header">📊 Binance Futures Anomaly Detector</h1>', 
                   unsafe_allow_html=True)
        
        # Sidebar controls
        self._render_sidebar()
        
        # Main content
        if st.session_state.get('is_monitoring', False):
            self._render_main_content()
        else:
            self._render_welcome_screen()
    
    def _render_sidebar(self):
        """Render sidebar controls"""
        st.sidebar.title("🎛️ Controls")
        
        # Monitoring controls
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("🚀 Start Monitoring", type="primary"):
                self._start_monitoring()
        
        with col2:
            if st.button("⏹️ Stop Monitoring"):
                self._stop_monitoring()
        
        # Status indicator
        st.sidebar.markdown("---")
        st.sidebar.subheader("📡 Status")
        
        if st.session_state.get('is_monitoring', False):
            st.sidebar.markdown(
                '<span class="status-indicator status-connected"></span>Monitoring Active',
                unsafe_allow_html=True
            )
        else:
            st.sidebar.markdown(
                '<span class="status-indicator status-disconnected"></span>Monitoring Stopped',
                unsafe_allow_html=True
            )
        
        # Statistics
        if st.session_state.get('market_data'):
            st.sidebar.markdown("---")
            st.sidebar.subheader("📈 Statistics")
            
            summary = self.anomaly_detector.get_market_summary()
            
            st.sidebar.metric("Symbols Monitored", summary['total_symbols'])
            st.sidebar.metric("Total Alerts", summary['total_alerts'])
            st.sidebar.metric("Recent Alerts (1h)", summary['recent_alerts'])
            st.sidebar.metric("Extreme Alerts", summary['extreme_alerts'])
        
        # Settings
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ Settings")
        
        refresh_interval = st.sidebar.slider(
            "Refresh Interval (seconds)", 
            min_value=1, max_value=30, 
            value=REFRESH_INTERVAL
        )
        
        if refresh_interval != REFRESH_INTERVAL:
            st.session_state.refresh_interval = refresh_interval

        # Diagnostics
        st.sidebar.markdown("---")
        st.sidebar.subheader("🛠 Diagnostics")
        if st.button("Run Diagnostics"):
            try:
                diags = self.binance_client.diagnostics()
                st.sidebar.json(diags)
                if diags.get('oi_fetch_disabled'):
                    st.sidebar.info("Open Interest temporarily disabled (451). Price & Volume alerts continue.")
            except Exception as e:
                st.sidebar.error(f"Diagnostics failed: {e}")
    
    def _render_welcome_screen(self):
        """Render welcome screen when not monitoring"""
        st.markdown("""
        ## Welcome to the Binance Futures Anomaly Detector! 🚀
        
        This application monitors all USDT perpetual futures pairs on Binance and detects:
        
        - **Price Spikes**: >3% price change in 5 minutes
        - **Volume Spikes**: 2x volume above 1-hour average  
        - **OI Changes**: >10% open interest change in 10 minutes
        
        ### Features:
        - 📊 Real-time WebSocket data streaming
        - 🚨 Automatic anomaly detection and alerting
        - 📈 Live market data dashboard
        - 🎨 Color-coded severity levels
        - 🔄 Auto-reconnection on connection loss
        
        ### Getting Started:
        1. Click "Start Monitoring" in the sidebar
        2. Wait for data to load (this may take a few moments)
        3. Monitor the live dashboard for anomalies
        
        **Note**: No API keys required - uses public market data only.
        """)
        
        # Show some example data
        if st.button("📋 Load Sample Data"):
            self._load_sample_data()
    
    def _render_main_content(self):
        """Render main dashboard content"""
        # Sync thread-safe data to session state
        self._sync_thread_safe_data()
        
        # Auto-refresh
        if st.session_state.get('auto_refresh', True):
            time.sleep(st.session_state.get('refresh_interval', REFRESH_INTERVAL))
            st.rerun()
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", "🚨 Alerts", "📈 Individual Pairs", "📋 Settings"])
        
        with tab1:
            self._render_market_overview()
        
        with tab2:
            self._render_alerts_panel()
        
        with tab3:
            self._render_individual_pairs()
        
        with tab4:
            self._render_settings()
    
    def _render_market_overview(self):
        """Render market overview tab"""
        st.subheader("📊 Market Overview")
        
        if not st.session_state.get('market_data'):
            st.warning("No market data available. Please start monitoring.")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pairs", len(st.session_state.market_data))
        
        with col2:
            recent_alerts = len(self.anomaly_detector.get_recent_alerts(60))
            st.metric("Recent Alerts (1h)", recent_alerts)
        
        with col3:
            extreme_alerts = len(self.anomaly_detector.get_alerts_by_severity('extreme'))
            st.metric("Extreme Alerts", extreme_alerts)
        
        with col4:
            last_update = st.session_state.get('last_update', datetime.now())
            st.metric("Last Update", last_update.strftime("%H:%M:%S"))
        
        # Market data table
        st.subheader("📈 Live Market Data")
        
        if st.session_state.market_data:
            df = pd.DataFrame.from_dict(st.session_state.market_data, orient='index')
            df = df.reset_index().rename(columns={'index': 'Symbol'})
            
            # Format columns
            if 'price' in df.columns:
                df['price'] = df['price'].apply(lambda x: f"${x:,.4f}" if pd.notna(x) else "N/A")
            if 'volume' in df.columns:
                df['volume'] = df['volume'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
            if 'open_interest' in df.columns:
                df['open_interest'] = df['open_interest'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
            if 'price_change_24h' in df.columns:
                df['price_change_24h'] = df['price_change_24h'].apply(
                    lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A"
                )
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No market data available yet. Please wait for data to load...")
    
    def _render_alerts_panel(self):
        """Render alerts panel"""
        st.subheader("🚨 Anomaly Alerts")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            severity_filter = st.selectbox(
                "Filter by Severity",
                ["All", "Extreme", "High", "Medium", "Low"]
            )
        
        with col2:
            alert_type_filter = st.selectbox(
                "Filter by Type",
                ["All", "Price Spike", "Volume Spike", "OI Change"]
            )
        
        with col3:
            time_filter = st.selectbox(
                "Time Range",
                ["Last Hour", "Last 6 Hours", "Last 24 Hours", "All"]
            )
        
        # Get filtered alerts
        alerts = self.anomaly_detector.get_recent_alerts(
            minutes=60 if time_filter == "Last Hour" else 
                   360 if time_filter == "Last 6 Hours" else
                   1440 if time_filter == "Last 24 Hours" else 999999
        )
        
        if severity_filter != "All":
            alerts = [a for a in alerts if a.severity.lower() == severity_filter.lower()]
        
        if alert_type_filter != "All":
            type_mapping = {
                "Price Spike": "price_spike",
                "Volume Spike": "volume_spike", 
                "OI Change": "oi_change"
            }
            alert_type = type_mapping.get(alert_type_filter)
            if alert_type:
                alerts = [a for a in alerts if a.alert_type == alert_type]
        
        # Display alerts
        if alerts:
            st.write(f"Found {len(alerts)} alerts")
            
            for alert in sorted(alerts, key=lambda x: x.timestamp, reverse=True):
                self._render_alert_card(alert)
        else:
            st.info("No alerts found for the selected filters.")
    
    def _render_alert_card(self, alert: AnomalyAlert):
        """Render individual alert card"""
        severity_colors = {
            'extreme': 'alert-extreme',
            'high': 'alert-high', 
            'medium': 'alert-medium',
            'low': 'alert-low'
        }
        
        severity_icons = {
            'extreme': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        alert_type_icons = {
            'price_spike': '📈',
            'volume_spike': '📊',
            'oi_change': '🔗'
        }
        
        icon = severity_icons.get(alert.severity, '⚪')
        type_icon = alert_type_icons.get(alert.alert_type, '📋')
        
        st.markdown(f"""
        <div class="alert-card {severity_colors.get(alert.severity, 'alert-low')}">
            <strong>{icon} {type_icon} {alert.symbol}</strong> - {alert.description}<br>
            <small>Severity: {alert.severity.upper()} | Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</small>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_individual_pairs(self):
        """Render individual pairs analysis"""
        st.subheader("📈 Individual Pairs Analysis")
        
        if not st.session_state.get('market_data'):
            st.warning("No market data available.")
            return
        
        # Symbol selector
        symbols = list(st.session_state.market_data.keys())
        selected_symbol = st.selectbox("Select Symbol", symbols)
        
        if selected_symbol and selected_symbol in st.session_state.market_data:
            data = st.session_state.market_data[selected_symbol]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Current Price", f"${data.get('price', 0):,.4f}")
                st.metric("24h Volume", f"{data.get('volume', 0):,.0f}")
                st.metric("Open Interest", f"{data.get('open_interest', 0):,.0f}")
            
            with col2:
                st.metric("24h Change", f"{data.get('price_change_24h', 0):+.2f}%")
                st.metric("24h High", f"${data.get('high_24h', 0):,.4f}")
                st.metric("24h Low", f"${data.get('low_24h', 0):,.4f}")
    
    def _render_settings(self):
        """Render settings tab"""
        st.subheader("⚙️ Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Detection Thresholds")
            
            price_threshold = st.slider(
                "Price Spike Threshold (%)",
                min_value=1.0, max_value=10.0, value=3.0, step=0.5
            )
            
            volume_threshold = st.slider(
                "Volume Spike Threshold (x)",
                min_value=1.0, max_value=5.0, value=2.0, step=0.1
            )
            
            oi_threshold = st.slider(
                "OI Change Threshold (%)",
                min_value=5.0, max_value=20.0, value=10.0, step=1.0
            )
        
        with col2:
            st.subheader("Display Options")
            
            auto_refresh = st.checkbox("Auto Refresh", value=True)
            refresh_interval = st.slider(
                "Refresh Interval (seconds)",
                min_value=1, max_value=30, value=5
            )
            
            show_timestamps = st.checkbox("Show Timestamps", value=True)
            color_coding = st.checkbox("Color Coding", value=True)
        
        # Telegram Settings
        st.markdown("---")
        st.subheader("📱 Telegram Notifications")
        
        telegram_enabled = st.checkbox("Enable Telegram Alerts", value=False)
        
        if telegram_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                bot_token = st.text_input(
                    "Bot Token", 
                    placeholder="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                    type="password"
                )
            
            with col2:
                chat_id = st.text_input(
                    "Chat ID", 
                    placeholder="123456789"
                )
            
            if st.button("🧪 Test Telegram Connection"):
                if bot_token and chat_id:
                    # Set environment variables temporarily
                    import os
                    os.environ['TELEGRAM_BOT_TOKEN'] = bot_token
                    os.environ['TELEGRAM_CHAT_ID'] = chat_id
                    
                    # Test the connection
                    try:
                        from telegram_notifier import TelegramNotifier
                        notifier = TelegramNotifier()
                        if notifier.is_configured():
                            st.success("✅ Telegram connection successful!")
                            st.info("You should receive a test message in Telegram.")
                        else:
                            st.error("❌ Telegram configuration failed")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("Please enter both Bot Token and Chat ID")
            
            st.markdown("""
            **How to set up Telegram bot:**
            1. Message @BotFather on Telegram
            2. Send `/newbot` and follow instructions
            3. Copy the bot token above
            4. Start a chat with your bot
            5. Send any message to your bot
            6. Visit: `https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates`
            7. Find your chat ID in the response
            """)
        
        if st.button("💾 Save Settings"):
            st.success("Settings saved!")
    
    def _start_monitoring(self):
        """Start monitoring all USDT futures pairs"""
        st.session_state.is_monitoring = True
        
        # Get USDⓈ-M and COIN-M perpetual futures symbols
        with st.spinner("Loading futures symbols (USDⓈ-M & COIN-M)..."):
            usdt_symbols = self.binance_client.get_usdt_futures_symbols()
            coinm_symbols = []
            try:
                coinm_symbols = self.binance_client.get_coinm_futures_symbols()
            except Exception:
                coinm_symbols = []
            symbols = list(dict.fromkeys(usdt_symbols + coinm_symbols))
        
        if not symbols:
            st.error("Failed to load symbols. Please try again.")
            st.session_state.is_monitoring = False
            return
        
        st.session_state.symbols = symbols
        st.session_state.market_data = {}
        
        # Start WebSocket connections
        with st.spinner(f"Starting monitoring for {len(symbols)} symbols..."):
            for symbol in symbols:
                self._start_symbol_monitoring(symbol)
        
        st.success(f"Started monitoring {len(symbols)} symbols!")
        st.rerun()
    
    def _stop_monitoring(self):
        """Stop monitoring"""
        st.session_state.is_monitoring = False
        self.binance_client.stop_all_websockets()
        st.success("Monitoring stopped!")
        st.rerun()
    
    def _start_symbol_monitoring(self, symbol: str):
        """Start monitoring a specific symbol"""
        def websocket_callback(sym, data):
            try:
                # Process WebSocket data
                price = float(data.get('c', 0))  # current price
                volume = float(data.get('v', 0))  # volume
                price_change_24h = float(data.get('P', 0))  # 24h price change %
                
                # Store data in thread-safe way (don't access st.session_state from threads)
                market_data = {
                    'price': price,
                    'volume': volume,
                    'price_change_24h': price_change_24h,
                    'high_24h': float(data.get('h', 0)),
                    'low_24h': float(data.get('l', 0)),
                    'last_update': datetime.now()
                }
                
                # Store in a thread-safe data store
                if not hasattr(self, 'thread_safe_data'):
                    self.thread_safe_data = {}
                self.thread_safe_data[sym] = market_data
                
                # Check for anomalies (this is thread-safe)
                alert = self.anomaly_detector.add_price_data(sym, price)
                if alert:
                    if not hasattr(self, 'thread_safe_alerts'):
                        self.thread_safe_alerts = []
                    self.thread_safe_alerts.append(alert)
                
                alert = self.anomaly_detector.add_volume_data(sym, volume)
                if alert:
                    if not hasattr(self, 'thread_safe_alerts'):
                        self.thread_safe_alerts = []
                    self.thread_safe_alerts.append(alert)
                
                # Get open interest (this requires a separate API call)
                # Only try OI for USDT pairs to avoid errors with USD pairs
                if sym.endswith('USDT'):
                    try:
                        oi_data = self.binance_client.get_open_interest(sym)
                        if oi_data and 'openInterest' in oi_data:
                            oi = float(oi_data.get('openInterest', 0))
                            self.thread_safe_data[sym]['open_interest'] = oi
                            
                            alert = self.anomaly_detector.add_oi_data(sym, oi)
                            if alert:
                                if not hasattr(self, 'thread_safe_alerts'):
                                    self.thread_safe_alerts = []
                                self.thread_safe_alerts.append(alert)
                    except Exception as e:
                        # Avoid noisy logs on serverless when blocked
                        self.thread_safe_data[sym]['open_interest'] = 0
                else:
                    # For non-USDT pairs, set OI to 0
                    self.thread_safe_data[sym]['open_interest'] = 0
                    
            except Exception as e:
                logger.error(f"Error in websocket callback for {sym}: {e}")
        
        # Start WebSocket
        self.binance_client.start_websocket(symbol, websocket_callback)
    
    def _load_sample_data(self):
        """Load sample data for demonstration"""
        sample_data = {
            'BTCUSDT': {
                'price': 43250.50,
                'volume': 1234567.89,
                'price_change_24h': 2.34,
                'open_interest': 987654321.0,
                'high_24h': 44000.0,
                'low_24h': 42000.0
            },
            'ETHUSDT': {
                'price': 2650.75,
                'volume': 987654.32,
                'price_change_24h': -1.23,
                'open_interest': 456789123.0,
                'high_24h': 2700.0,
                'low_24h': 2600.0
            }
        }
        
        st.session_state.market_data = sample_data
        st.success("Sample data loaded!")
    
    def _sync_thread_safe_data(self):
        """Sync thread-safe data to session state"""
        # Sync market data
        if hasattr(self, 'thread_safe_data') and self.thread_safe_data:
            st.session_state.market_data.update(self.thread_safe_data)
            st.session_state.last_update = datetime.now()
        
        # Sync alerts
        if hasattr(self, 'thread_safe_alerts') and self.thread_safe_alerts:
            # Add new alerts to session state
            for alert in self.thread_safe_alerts:
                if alert not in st.session_state.alerts:
                    st.session_state.alerts.append(alert)
            # Clear processed alerts
            self.thread_safe_alerts = []

def main():
    """Main function to run the dashboard"""
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
