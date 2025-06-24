#!/usr/bin/env python3
"""
Deployment Fix Script for Streamlit Web Scraping Issues
This script diagnoses and fixes common deployment issues
"""

import os
import sys
import subprocess
import logging
import platform
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_system_info():
    """Check system information"""
    print("🔍 System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Python: {sys.version}")
    print(f"   Architecture: {platform.machine()}")
    print()

def check_chrome_installation():
    """Check Chrome/Chromium installation"""
    print("🔍 Checking Chrome Installation:")
    
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/opt/google/chrome/chrome',
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"   ✅ Found Chrome at: {path}")
            chrome_found = True
            break
    
    if not chrome_found:
        # Try which command
        try:
            for cmd in ['google-chrome', 'chromium', 'chrome']:
                result = subprocess.run(['which', cmd], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"   ✅ Found {cmd} at: {result.stdout.strip()}")
                    chrome_found = True
                    break
        except Exception:
            pass
    
    if not chrome_found:
        print("   ❌ Chrome/Chromium not found")
        print("   💡 Install Chrome with:")
        if platform.system() == "Linux":
            print("      Ubuntu/Debian: sudo apt-get install google-chrome-stable")
            print("      Or: sudo apt-get install chromium-browser")
        elif platform.system() == "Darwin":
            print("      macOS: brew install --cask google-chrome")
        
        return False
    
    return True

def install_chrome_linux():
    """Install Chrome on Linux systems"""
    try:
        print("🔧 Installing Chrome on Linux...")
        
        # Update package list
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        
        # Install wget if not present
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'wget'], check=True)
        
        # Download and install Chrome
        subprocess.run(['wget', '-q', '-O', '-', 'https://dl.google.com/linux/linux_signing_key.pub'], check=True)
        subprocess.run(['sudo', 'apt-key', 'add', '-'], check=True)
        subprocess.run(['sudo', 'sh', '-c', 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'], check=True)
        subprocess.run(['sudo', 'apt-get', 'update'], check=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'google-chrome-stable'], check=True)
        
        print("✅ Chrome installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Chrome: {e}")
        return False

def setup_display_environment():
    """Setup display environment for headless systems"""
    print("🔧 Setting up display environment...")
    
    if not os.getenv('DISPLAY'):
        try:
            # Install xvfb for virtual display
            if platform.system() == "Linux":
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'xvfb'], check=True)
                
                # Set DISPLAY environment variable
                os.environ['DISPLAY'] = ':99'
                
                # Start Xvfb
                subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1024x768x24'], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print("✅ Virtual display setup complete")
                return True
        except Exception as e:
            print(f"❌ Failed to setup display: {e}")
            return False
    else:
        print("✅ Display environment already configured")
        return True

def create_deployment_env():
    """Create deployment-specific environment file"""
    print("🔧 Creating deployment environment configuration...")
    
    deployment_env = """
# Deployment-specific environment variables
DEPLOYMENT_MODE=true
CHROME_HEADLESS=true
SELENIUM_TIMEOUT=30
CRAWL_DELAY=2.0
MAX_PAGES_PER_CRAWL=20

# Chrome/Selenium specific
CHROME_NO_SANDBOX=true
DISABLE_DEV_SHM_USAGE=true
CHROME_DISABLE_GPU=true

# Logging
LOG_LEVEL=INFO
STREAMLIT_SERVER_HEADLESS=true
"""
    
    try:
        with open('.env.deployment', 'w') as f:
            f.write(deployment_env)
        print("✅ Deployment environment file created")
        return True
    except Exception as e:
        print(f"❌ Failed to create deployment env: {e}")
        return False

def test_selenium_setup():
    """Test Selenium setup with deployment fixes"""
    print("🧪 Testing Selenium setup...")
    
    try:
        # Add current directory to path
        sys.path.append('.')
        
        from selenium_deployment import test_deployment_driver
        
        success = test_deployment_driver()
        if success:
            print("✅ Selenium test passed")
            return True
        else:
            print("❌ Selenium test failed")
            return False
            
    except Exception as e:
        print(f"❌ Selenium test error: {e}")
        return False

def create_dockerfile():
    """Create Dockerfile for containerized deployment"""
    dockerfile_content = """
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    unzip \\
    curl \\
    xvfb \\
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \\
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \\
    && apt-get update \\
    && apt-get install -y google-chrome-stable \\
    && rm -rf /var/lib/apt/lists/*

# Set display port to avoid crash
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create entrypoint script
RUN echo '#!/bin/bash\\n\\
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\\n\\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# Expose Streamlit port
EXPOSE 8501

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
    
    try:
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        print("✅ Dockerfile created for containerized deployment")
        return True
    except Exception as e:
        print(f"❌ Failed to create Dockerfile: {e}")
        return False

def create_docker_compose():
    """Create docker-compose.yml for easy deployment"""
    docker_compose_content = """
version: '3.8'

services:
  web-crawler:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DISPLAY=:99
      - STREAMLIT_SERVER_HEADLESS=true
      - CHROME_HEADLESS=true
    volumes:
      - ./.env:/app/.env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
    
    try:
        with open('docker-compose.yml', 'w') as f:
            f.write(docker_compose_content)
        print("✅ docker-compose.yml created")
        return True
    except Exception as e:
        print(f"❌ Failed to create docker-compose.yml: {e}")
        return False

def main():
    """Main deployment fix function"""
    print("🚀 Web Scraping Deployment Fix Tool")
    print("=" * 50)
    
    check_system_info()
    
    fixes_applied = []
    
    # Check and fix Chrome installation
    if not check_chrome_installation():
        if platform.system() == "Linux":
            if input("Install Chrome automatically? (y/N): ").lower() == 'y':
                if install_chrome_linux():
                    fixes_applied.append("Chrome installation")
    
    # Setup display environment
    if setup_display_environment():
        fixes_applied.append("Display environment")
    
    # Create deployment configuration
    if create_deployment_env():
        fixes_applied.append("Deployment environment")
    
    # Test Selenium
    if test_selenium_setup():
        fixes_applied.append("Selenium configuration")
    
    # Create Docker files
    if input("Create Docker files for containerized deployment? (y/N): ").lower() == 'y':
        if create_dockerfile():
            fixes_applied.append("Dockerfile")
        if create_docker_compose():
            fixes_applied.append("Docker Compose")
    
    # Summary
    print("\\n" + "=" * 50)
    print("📋 DEPLOYMENT FIX SUMMARY")
    print("=" * 50)
    
    if fixes_applied:
        print("✅ Applied fixes:")
        for fix in fixes_applied:
            print(f"   - {fix}")
    else:
        print("❌ No fixes were applied")
    
    print("\\n🛠️  DEPLOYMENT RECOMMENDATIONS:")
    print("1. Use headless mode: Set CHROME_HEADLESS=true")
    print("2. For cloud deployment, use Docker")
    print("3. Ensure Chrome is installed in deployment environment")
    print("4. Set appropriate timeouts and delays")
    print("5. Monitor memory usage and adjust limits")
    
    print("\\n🐳 DOCKER DEPLOYMENT:")
    print("   Build: docker build -t web-crawler .")
    print("   Run: docker-compose up -d")
    
    print("\\n🚀 STREAMLIT DEPLOYMENT:")
    print("   Local: streamlit run app.py")
    print("   With fixes: CHROME_HEADLESS=true streamlit run app.py")

if __name__ == "__main__":
    main()
