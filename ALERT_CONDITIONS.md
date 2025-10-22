# 🚨 Alert Trigger Conditions

## Current Production Settings

### 📊 **Volume Filter**
- **Minimum 24h Volume**: 250,000,000 USDT (250M)
- **Market Cap**: No restriction - includes all altcoins
- **Result**: Any pair with 250M+ volume can trigger alerts (major pairs + smaller altcoins)

### 📈 **Price Spike Detection**
- **Threshold**: 8% price change in 5 minutes
- **Severity Levels**:
  - **Medium**: 8-16% price change
  - **High**: 16-24% price change  
  - **Extreme**: 24%+ price change
- **Example**: BTC drops from $43,000 to $39,560 (8% drop) in 5 minutes

### 📊 **Volume Spike Detection**
- **Threshold**: 5x volume above 1-hour average
- **Severity Levels**:
  - **Medium**: 5-10x volume spike
  - **High**: 10-15x volume spike
  - **Extreme**: 15x+ volume spike
- **Example**: Normal volume is 1M, suddenly spikes to 5M+ in 1 hour

### 🚨 **Alert Severity Filtering**
- **✅ SENT**: Medium, High, Extreme severity alerts
- **❌ BLOCKED**: Low severity alerts
- **Result**: Only significant market movements trigger alerts

### ⏰ **24-Hour Cooldown Per Symbol**
- **Rule**: Once COAIUSDT (or any symbol) gets an alert, no more alerts for 24 hours
- **Result**: No spam alerts for the same pair

### 🐌 **Rate Limiting**
- **Delay**: 30 seconds between messages
- **Batch Size**: 1 alert at a time
- **Result**: Very conservative alert frequency

## 🎯 **Real-World Examples**

### ✅ **WILL TRIGGER ALERT:**
- BTCUSDT drops 10% in 5 minutes (High severity)
- ETHUSDT volume spikes 6x above normal (Medium severity)
- Any pair with 250M+ volume has 8%+ price move (Medium+ severity)
- Small altcoin with 300M+ volume has 8%+ price move (Medium+ severity)

### ❌ **WILL NOT TRIGGER ALERT:**
- Any pair with less than 250M volume (below volume threshold)
- Less than 8% price move (below price threshold)
- Low severity alert (blocked by severity filter)
- Same symbol alert within 24 hours (cooldown)

## 📊 **Expected Alert Frequency**

### **Before (Spam Mode):**
- 142 alerts per minute
- All severity levels
- No cooldown
- Low volume pairs included

### **After (Production Mode):**
- 1-5 alerts per day
- Only medium+ severity
- 24-hour cooldown per symbol
- Any pair with 250M+ volume (major pairs + smaller altcoins)

## 🔧 **Configuration Summary**

```python
# Volume Filter
MIN_24H_VOLUME_USDT = 250_000_000  # 250M USDT
MIN_MARKET_CAP_USDT = 0            # No market cap restriction

# Price & Volume Thresholds
PRICE_SPIKE_THRESHOLD = 0.08       # 8% in 5 minutes
VOLUME_SPIKE_THRESHOLD = 5.0       # 5x above 1-hour average

# Severity Filtering
TELEGRAM_SEND_EXTREME = True       # Send extreme alerts
TELEGRAM_SEND_HIGH = True          # Send high alerts
TELEGRAM_SEND_MEDIUM = True        # Send medium alerts
TELEGRAM_SEND_LOW = False          # Block low alerts

# Rate Limiting
TELEGRAM_RATE_LIMIT = 30.0         # 30 seconds between messages
ALERT_COOLDOWN_HOURS = 24          # 24-hour cooldown per symbol
```

## 🎯 **Bottom Line**

You'll now only get alerts for:
1. **Any pair with 250M+ volume** (major pairs + smaller altcoins)
2. **Significant moves** (8%+ price or 5x+ volume)
3. **Medium+ severity** (no low severity spam)
4. **Once per symbol per 24 hours** (no duplicates)
5. **Very conservative rate** (30s between messages)

This should reduce your alerts from 142/minute to 1-5 per day! 🎯
