#!/usr/bin/env python3

"""
Demo script for AI Website Chatbot
This script demonstrates how to use the chatbot programmatically
"""

import os
import time
from dotenv import load_dotenv
from app import WebsiteScraper, GeminiChatbot

def demo():
    """Run a demonstration of the chatbot"""
    print("🤖 AI Website Chatbot - Demo")
    print("============================")
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ Please configure your GEMINI_API_KEY in .env file")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Initialize components
    print("🔧 Initializing components...")
    scraper = WebsiteScraper()
    chatbot = GeminiChatbot()
    
    # Demo website URL
    demo_url = "https://httpbin.org/html"  # Simple test website
    print(f"🌐 Scraping demo website: {demo_url}")
    
    # Scrape website
    scraped_data = scraper.scrape_website(demo_url)
    
    if 'error' in scraped_data:
        print(f"❌ Failed to scrape website: {scraped_data['error']}")
        return
    
    print("✅ Website scraped successfully!")
    print(f"   Title: {scraped_data['title']}")
    print(f"   Content: {scraped_data['content'][:200]}...")
    
    # Set data for chatbot
    chatbot.set_website_data(scraped_data)
    
    # Demo questions
    questions = [
        "What is this website about?",
        "What are the main features mentioned?",
        "Tell me about the weather today",  # Irrelevant question
        "What information is available on this page?"
    ]
    
    print("\n💬 Chat Demo:")
    print("=============")
    
    for i, question in enumerate(questions, 1):
        print(f"\n{i}. Question: {question}")
        print("   " + "-" * 50)
        
        response = chatbot.generate_response(question)
        
        if response['is_relevant']:
            print(f"   ✅ Relevant response:")
        else:
            print(f"   ⚠️  Not relevant to website content:")
        
        print(f"   {response['response']}")
        
        # Small delay between questions
        time.sleep(1)
    
    print("\n🎉 Demo completed!")
    print("   To run the full web application: ./run.sh")

if __name__ == "__main__":
    demo()