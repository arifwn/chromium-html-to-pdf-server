#!/bin/bash

# Chromium HTML to PDF Server - Development Startup Script

set -e

echo "Starting Chromium HTML to PDF Server..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "   No .env file found. Copy .env.example to .env and configure your API key."
    echo "   Using default API key for development..."
    export API_KEY="your-secret-api-key-here"
fi

# Set default port if not specified
export PORT=${PORT:-8822}

echo "Setup complete!"
echo "API Key: $API_KEY"
echo "Server will start on port: $PORT"
echo ""
echo "Starting server..."

# Start the server
python main.py
