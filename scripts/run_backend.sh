#!/bin/bash

echo "🚀 Starting Review Summarizer Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=backend/app.py
export FLASK_ENV=development

# Create database tables
echo "🗄️ Setting up database..."
python database_setup.py

# Start the Flask application
echo "🌐 Starting Flask server..."
python backend/app.py
