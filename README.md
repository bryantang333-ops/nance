# Binance Futures Anomaly Detector 📊

A real-time anomaly detection system for Binance USDT perpetual futures pairs, built with Python, Streamlit, and WebSocket connections.

## Features 🚀

- **Real-time Monitoring**: WebSocket connections to all USDT perpetual futures pairs
- **Anomaly Detection**: Automatic detection of price spikes, volume anomalies, and open interest changes
- **Live Dashboard**: Beautiful Streamlit interface with live updating tables
- **Alert System**: Color-coded alerts with severity levels and timestamps
- **Auto-reconnection**: Robust WebSocket reconnection logic
- **Rate Limiting**: Built-in API rate limiting to respect Binance limits
- **No API Keys Required**: Uses only public market data

## Anomaly Detection Rules 🎯

The system monitors and flags the following anomalies:

1. **Price Spikes**: >3% price change in 5 minutes
2. **Volume Spikes**: 2x volume above 1-hour average
3. **Open Interest Changes**: >10% OI change in 10 minutes

## Installation 🛠️

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd binance-anomaly-detector
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser** to `http://localhost:8501`

### Alternative Installation

If you encounter issues, you can install dependencies manually:

```bash
pip install streamlit python-binance websocket-client pandas numpy plotly requests python-dotenv
```

## Usage 📖

### Starting the Application

```bash
# Basic usage
python app.py

# Custom port
python app.py --port 8502

# Custom host
python app.py --host 0.0.0.0

# Check dependencies
python app.py --check-deps

# Install dependencies
python app.py --install-deps
```

### Dashboard Features

1. **Market Overview Tab**
   - Live table of all monitored pairs
   - Real-time price, volume, and open interest data
   - 24-hour statistics

2. **Alerts Tab**
   - Filter alerts by severity (Extreme, High, Medium, Low)
   - Filter by alert type (Price Spike, Volume Spike, OI Change)
   - Time-based filtering
   - Color-coded alert cards

3. **Individual Pairs Tab**
   - Detailed analysis of specific trading pairs
   - Historical data visualization
   - Custom thresholds

4. **Settings Tab**
   - Adjustable detection thresholds
   - Display preferences
   - Refresh intervals

## Configuration ⚙️

### Environment Variables

Create a `.env` file (optional):

```env
# Application Configuration
STREAMLIT_PORT=8501
REFRESH_INTERVAL=5

# Detection Thresholds (can be adjusted in the dashboard)
PRICE_SPIKE_THRESHOLD=0.03  # 3%
VOLUME_SPIKE_THRESHOLD=2.0  # 2x
OI_CHANGE_THRESHOLD=0.10     # 10%
```

### Customizing Detection Rules

You can modify the detection thresholds in `config.py`:

```python
# Anomaly Detection Thresholds
PRICE_SPIKE_THRESHOLD = 0.03  # 3% price spike in 5 minutes
VOLUME_SPIKE_THRESHOLD = 2.0  # 2x volume above 1-hour average
OI_CHANGE_THRESHOLD = 0.10    # 10% OI change in 10 minutes
```

## Architecture 🏗️

### Project Structure

```
binance-anomaly-detector/
├── app.py                 # Main application entry point
├── dashboard.py           # Streamlit dashboard
├── binance_client.py      # Binance API client and WebSocket manager
├── anomaly_detector.py    # Anomaly detection algorithms
├── config.py             # Configuration settings
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Key Components

1. **BinanceClient**: Handles API requests and WebSocket connections
2. **AnomalyDetector**: Implements detection algorithms for price, volume, and OI
3. **Dashboard**: Streamlit interface with real-time updates
4. **RateLimiter**: Ensures API rate limits are respected

## Technical Details 🔧

### WebSocket Connections

- Connects to Binance futures WebSocket streams
- Automatic reconnection with exponential backoff
- Handles connection drops gracefully
- Monitors all USDT perpetual futures pairs

### Rate Limiting

- Built-in rate limiter (1200 requests/minute)
- 50ms delay between requests
- Respects Binance API limits

### Data Processing

- Real-time price and volume data from WebSocket
- Open interest data via REST API calls
- Historical data storage for anomaly detection
- Efficient data structures for fast lookups

## Troubleshooting 🐛

### Common Issues

1. **WebSocket Connection Errors**
   - Check internet connection
   - Verify Binance API is accessible
   - Restart the application

2. **Missing Dependencies**
   ```bash
   python app.py --install-deps
   ```

3. **Port Already in Use**
   ```bash
   python app.py --port 8502
   ```

4. **Slow Performance**
   - Reduce the number of monitored symbols
   - Increase refresh interval
   - Check system resources

### Logs and Debugging

The application includes comprehensive logging. Check the console output for:
- WebSocket connection status
- API rate limiting information
- Anomaly detection events
- Error messages

## Performance Considerations ⚡

- **Memory Usage**: Monitors ~200+ symbols with historical data
- **CPU Usage**: Real-time processing of WebSocket data
- **Network**: Continuous WebSocket connections + API calls
- **Storage**: In-memory data storage (no database required)

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License 📄

This project is open source and available under the MIT License.

## Disclaimer ⚠️

This tool is for educational and research purposes only. It does not provide financial advice. Always do your own research before making trading decisions. The authors are not responsible for any financial losses.

## Support 💬

If you encounter issues or have questions:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all dependencies are installed
4. Verify your internet connection

---

**Happy Trading! 📈**
