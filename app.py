import os
import requests
from bs4 import BeautifulSoup
import html2text
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import re
from urllib.parse import urljoin, urlparse
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

class WebsiteScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.h = html2text.HTML2Text()
        self.h.ignore_links = False
        self.h.ignore_images = True
        
    def scrape_website(self, url):
        """Scrape website content and return structured data"""
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract main content
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No title found"
            
            # Try to find main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|body'))
            
            if not main_content:
                main_content = soup.find('body')
            
            # Convert to text
            text_content = self.h.handle(str(main_content)) if main_content else ""
            
            # Clean up text
            text_content = re.sub(r'\n+', '\n', text_content)
            text_content = re.sub(r' +', ' ', text_content)
            
            # Extract links for reference
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/'):
                    href = urljoin(url, href)
                if href.startswith('http'):
                    links.append({
                        'text': link.get_text().strip(),
                        'url': href
                    })
            
            return {
                'url': url,
                'title': title_text,
                'content': text_content[:5000],  # Limit content length
                'links': links[:10],  # Limit number of links
                'scraped_at': time.time()
            }
            
        except Exception as e:
            return {'error': f"Failed to scrape website: {str(e)}"}

class GeminiChatbot:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.website_data = None
        
    def set_website_data(self, data):
        """Set the scraped website data for the chatbot"""
        self.website_data = data
        
    def generate_response(self, question):
        """Generate response based on website data"""
        if not self.website_data:
            return {
                'response': "No website data available. Please scrape a website first.",
                'is_relevant': False
            }
        
        # Create context for Gemini
        context = f"""
        Website Information:
        Title: {self.website_data['title']}
        URL: {self.website_data['url']}
        Content: {self.website_data['content']}
        
        User Question: {question}
        
        Instructions:
        1. Answer the question ONLY based on the provided website information
        2. If the question is not relevant to the website content, respond with: "Sorry, I can only answer questions about the content from {self.website_data['url']}. For more information, please visit: {self.website_data['url']}"
        3. If the question is relevant, provide a helpful answer based on the website content
        4. Keep responses concise and informative
        """
        
        try:
            response = self.model.generate_content(context)
            response_text = response.text
            
            # Check if response indicates irrelevance
            is_relevant = not ("sorry" in response_text.lower() and "can only answer questions" in response_text.lower())
            
            return {
                'response': response_text,
                'is_relevant': is_relevant,
                'source_url': self.website_data['url']
            }
            
        except Exception as e:
            return {
                'response': f"Error generating response: {str(e)}",
                'is_relevant': False
            }

# Initialize components
scraper = WebsiteScraper()
chatbot = GeminiChatbot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape_website():
    """Endpoint to scrape a website"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    scraped_data = scraper.scrape_website(url)
    
    if 'error' in scraped_data:
        return jsonify(scraped_data), 400
    
    # Set the scraped data for the chatbot
    chatbot.set_website_data(scraped_data)
    
    return jsonify({
        'success': True,
        'data': scraped_data
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint to chat with the AI"""
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    response = chatbot.generate_response(question)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)