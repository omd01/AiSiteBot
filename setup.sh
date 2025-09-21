#!/bin/bash

# AI Website Chatbot Setup Script

echo "🤖 AI Website Chatbot Setup"
echo "============================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ Python 3 and pip3 are installed"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your Gemini API key"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
    echo "🔑 To get your Gemini API key:"
    echo "   1. Go to https://makersuite.google.com/app/apikey"
    echo "   2. Sign in with your Google account"
    echo "   3. Click 'Create API Key'"
    echo "   4. Copy the generated key"
    echo "   5. Paste it in the .env file"
    echo ""
    echo "After adding your API key, run: ./run.sh"
else
    echo "✅ .env file found"
fi

echo ""
echo "🚀 Setup complete! To run the application:"
echo "   ./run.sh"
echo ""
echo "📖 For more information, see README.md"