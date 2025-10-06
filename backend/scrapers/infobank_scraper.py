import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def get_infobank_news(directory=None):
    """
    Scrape headlines from InfoBank website
    Args:
        directory (str, optional): Directory path to append to base URL (e.g., "/category/berita-ekonomi-dan-bisnis-terbaru/")
    Returns a list of dictionaries containing headline information
    """
    # Get URL from environment variable
    base_url = os.getenv('infobank_url')
    
    if not base_url:
        return {
            'error': 'infobank_url not found in environment variables',
            'headlines': []
        }
    
    # Construct the full URL
    if directory:
        # Ensure directory starts with / if it doesn't already
        if not directory.startswith('/'):
            directory = '/' + directory
        # Ensure directory ends with / if it doesn't already
        if not directory.endswith('/'):
            directory = directory + '/'
        url = base_url.rstrip('/') + directory
    else:
        url = base_url
        
    try:
        # Send GET request with headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)

        # Check if request succeeded
        if response.status_code == 200:
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            headlines = []
            
            # Look for common headline selectors
            # Try different selectors that might contain headlines
            headline_selectors = [
                'h1', 'h2', 'h3',  # Common heading tags
                '.title', '.headline', '.news-title',  # Common class names
                'a[href*="news"]',  # Links that might contain news
                '.post-title', '.article-title',  # Article title classes
                '.entry-title', '.content-title'  # Content title classes
            ]
            
            for selector in headline_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if text and len(text) > 10:  # Filter out very short text
                        # Get link if available
                        link = None
                        if element.name == 'a':
                            link = element.get('href')
                        elif element.find('a'):
                            link = element.find('a').get('href')
                        
                        # Make link absolute if it's relative
                        if link and not link.startswith('http'):
                            link = url + link if link.startswith('/') else url + '/' + link
                        
                        headline_data = {
                            'title': text,
                            'link': link,
                            'source': 'InfoBank'
                        }
                        
                        # Avoid duplicates
                        if headline_data not in headlines:
                            headlines.append(headline_data)
            
            # Limit to first 50 headlines to avoid too much data
            headlines = headlines[:20]
            
            return {
                'success': True,
                'headlines': headlines,
                'count': len(headlines),
                'source': 'InfoBank',
                'url_scraped': url,
                'directory_used': directory,
                'scraped_at': datetime.now().isoformat()
            }
        else:
            return {
                'error': f'Failed to fetch. Status code: {response.status_code}',
                'headlines': []
            }

    except requests.exceptions.RequestException as e:
        return {
            'error': f'Request error: {str(e)}',
            'headlines': []
        }
    except Exception as e:
        return {
            'error': f'Parsing error: {str(e)}',
            'headlines': []
        }

if __name__ == "__main__":
    import json
    from datetime import datetime
    
    print("🔍 Scraping InfoBank news...")
    print("=" * 50)
    
    # Test with specific category directory
    directory = "/category/berita-ekonomi-dan-bisnis-terbaru/"  # Scrape economics and business news
    
    # Get the news data
    result = get_infobank_news(directory=directory)
    
    # Add timestamp and metadata
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'scraper': 'InfoBank Scraper',
        'status': 'success' if result.get('success') else 'error',
        'data': result
    }
    
    # Save to JSON file
    output_file = 'infobank_scraper_result.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
    
    # Print summary
    if result.get('success'):
        print("✅ SUCCESS!")
        print(f"📰 Found {result.get('count', 0)} headlines")
        print(f"🔗 Source: {result.get('source', 'Unknown')}")
        if result.get('directory_used'):
            print(f"📁 Directory: {result.get('directory_used')}")
        print(f"🌐 URL: {result.get('url_scraped', 'Unknown')}")
        print(f"💾 Results saved to {output_file}")
    else:
        print("❌ ERROR:")
        print(f"Error: {result.get('error', 'Unknown error occurred')}")
        print(f"💾 Error details saved to {output_file}")