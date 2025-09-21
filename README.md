# AI Website Chatbot

A Flask-based AI chatbot that scrapes website content and uses Google's Gemini API to answer questions about the scraped data.

## Features

- 🌐 **Website Scraping**: Automatically scrapes any website URL you provide
- 🤖 **AI-Powered Chat**: Uses Google Gemini API for intelligent responses
- 🎯 **Content-Focused**: Only answers questions relevant to the scraped website
- 🚫 **Relevance Filtering**: Provides helpful messages when questions aren't relevant
- 💻 **Modern UI**: Beautiful, responsive web interface
- ⚡ **Real-time Chat**: Interactive chat experience

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Gemini API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the API key

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   Open your browser and go to `http://localhost:5000`

## Usage

1. **Scrape a Website**: Enter any website URL and click "Scrape Website"
2. **Chat with AI**: Ask questions about the scraped content
3. **Get Relevant Answers**: The AI will only answer questions related to the website content
4. **Fallback Messages**: If your question isn't relevant, you'll get a helpful message with the original website link

## API Endpoints

- `POST /scrape`: Scrape a website URL
- `POST /chat`: Send a question to the AI chatbot
- `GET /`: Serve the main web interface

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

## Dependencies

- Flask: Web framework
- requests: HTTP requests
- beautifulsoup4: HTML parsing
- google-generativeai: Gemini API integration
- python-dotenv: Environment variable management
- html2text: HTML to text conversion
- lxml: XML/HTML parser

## Example Usage

1. Enter a website URL like `https://example.com`
2. Wait for the scraping to complete
3. Ask questions like:
   - "What is this website about?"
   - "What are the main features mentioned?"
   - "Tell me about the pricing information"
   - "What contact information is available?"

The AI will provide relevant answers based on the scraped content, or politely redirect you to the original website if your question isn't relevant.