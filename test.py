#!/usr/bin/env python3

"""
Test script for AI Website Chatbot
This script tests the basic functionality without running the full Flask app
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests imported successfully")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        import bs4
        print("✅ BeautifulSoup imported successfully")
    except ImportError as e:
        print(f"❌ BeautifulSoup import failed: {e}")
        return False
    
    try:
        import google.generativeai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        return False
    
    try:
        import html2text
        print("✅ html2text imported successfully")
    except ImportError as e:
        print(f"❌ html2text import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\n🔧 Testing environment configuration...")
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    elif api_key == 'your_gemini_api_key_here':
        print("❌ GEMINI_API_KEY is still set to placeholder value")
        return False
    else:
        print("✅ GEMINI_API_KEY is configured")
        return True

def test_website_scraper():
    """Test website scraping functionality"""
    print("\n🌐 Testing website scraper...")
    
    try:
        from app import WebsiteScraper
        scraper = WebsiteScraper()
        
        # Test with a simple website
        test_url = "https://httpbin.org/html"
        result = scraper.scrape_website(test_url)
        
        if 'error' in result:
            print(f"❌ Website scraping failed: {result['error']}")
            return False
        else:
            print("✅ Website scraping test passed")
            print(f"   Title: {result['title']}")
            print(f"   Content length: {len(result['content'])} characters")
            return True
            
    except Exception as e:
        print(f"❌ Website scraper test failed: {e}")
        return False

def test_gemini_integration():
    """Test Gemini API integration"""
    print("\n🤖 Testing Gemini API integration...")
    
    try:
        from app import GeminiChatbot
        chatbot = GeminiChatbot()
        
        # Set some test data
        test_data = {
            'url': 'https://example.com',
            'title': 'Example Domain',
            'content': 'This domain is for use in illustrative examples in documents.',
            'links': [],
            'scraped_at': 1234567890
        }
        
        chatbot.set_website_data(test_data)
        response = chatbot.generate_response("What is this website about?")
        
        if 'error' in response:
            print(f"❌ Gemini API test failed: {response['error']}")
            return False
        else:
            print("✅ Gemini API test passed")
            print(f"   Response: {response['response'][:100]}...")
            return True
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Website Chatbot - Test Suite")
    print("==================================")
    
    tests = [
        test_imports,
        test_environment,
        test_website_scraper,
        test_gemini_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is ready to run.")
        print("   Run: ./run.sh")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("   Make sure to run: ./setup.sh")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)