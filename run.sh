#!/bin/bash

# SQL Agent Run Script
echo "Setting up SQL Agent environment..."

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
pip install -U flask langchain langchain-core langchain-google-genai langgraph pydantic python-dotenv werkzeug langchain-community

# Create required directories if they don't exist
echo "Setting up project structure..."
mkdir -p templates uploads agents database

# Check if .env file exists, create if not
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "API_KEY=your_google_api_key_here" > .env
    echo "Please update the .env file with your actual Google API key."
fi

# Run the application
echo "Starting SQL Agent application..."
python run.py

# Deactivate virtual environment on exit
deactivate