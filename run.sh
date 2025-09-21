#!/bin/bash

# AI Website Chatbot Run Script

echo "🤖 Starting AI Website Chatbot..."
echo "================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./setup.sh first"
    exit 1
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=" .env || grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
    echo "❌ GEMINI_API_KEY not configured in .env file"
    echo "   Please edit .env file and add your Gemini API key"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import flask, requests, bs4, google.generativeai" 2>/dev/null; then
    echo "❌ Dependencies not installed. Please run ./setup.sh first"
    exit 1
fi

echo "✅ All checks passed"
echo ""
echo "🌐 Starting Flask application..."
echo "📱 Open your browser and go to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Run the Flask application
python3 app.py