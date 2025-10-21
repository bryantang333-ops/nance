#!/usr/bin/env python3
"""
Main application entry point for the Binance Futures Anomaly Detector
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import streamlit
        import pandas
        import numpy
        import plotly
        import requests
        import websocket
        from binance import Client
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_dashboard(port=8501, host="localhost"):
    """Run the Streamlit dashboard"""
    print(f"🚀 Starting Binance Futures Anomaly Detector on {host}:{port}")
    print("📊 Dashboard will open in your browser automatically")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 60)
    
    try:
        # Run streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", str(port),
            "--server.address", host,
            "--browser.gatherUsageStats", "false"
        ]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Binance Futures Anomaly Detector")
    parser.add_argument("--port", type=int, default=8501, help="Port to run the dashboard on")
    parser.add_argument("--host", default="localhost", help="Host to run the dashboard on")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies and exit")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies and exit")
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🔍 Binance Futures Anomaly Detector")
    print("=" * 50)
    
    if args.install_deps:
        if install_dependencies():
            print("✅ Setup complete! Run 'python app.py' to start the application")
        else:
            sys.exit(1)
        return
    
    if args.check_deps:
        if check_dependencies():
            print("✅ All dependencies are available")
        else:
            print("❌ Some dependencies are missing")
            sys.exit(1)
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n🔧 Installing missing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies. Please install manually:")
            print("   pip install -r requirements.txt")
            sys.exit(1)
    
    # Run the dashboard
    run_dashboard(port=args.port, host=args.host)

if __name__ == "__main__":
    main()
