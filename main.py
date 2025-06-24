"""
Main entry point for the Graph Web Crawler Research Bot
Run this file to start the Streamlit application
"""

import streamlit as st
import subprocess
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Main function to run the Streamlit app"""
    
    # Ensure we're in the right directory
    current_dir = Path(__file__).parent
    os.chdir(current_dir)
    
    # Load environment variables
    load_dotenv()
    
    # Add the current directory to Python path
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    print("🔍 Starting AI Research Crawler...")
    print("📡 Graph algorithms: BFS (Search) & DFS+BFS (Deep Research)")
    print("🚀 Launching Streamlit interface...")
    
    # Run the Streamlit app
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "localhost"
    ])

if __name__ == "__main__":
    main()
