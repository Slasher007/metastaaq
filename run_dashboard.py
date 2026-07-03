#!/usr/bin/env python3
"""
Launch script for the MetaSTAAQ Dashboard
Run this script to start the Streamlit dashboard
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit dashboard"""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dashboard_path = os.path.join(script_dir, "dashboard.py")
    
    print("🚀 Starting MetaSTAAQ Dashboard...")
    print(f"📁 Dashboard location: {dashboard_path}")
    print("🌐 The dashboard will open in your default web browser")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", dashboard_path,
            "--server.address", "localhost",
            "--server.port", "8010",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting dashboard: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")
    except FileNotFoundError:
        print("❌ Python not found. Make sure Python is installed and in your PATH.")

if __name__ == "__main__":
    main()
