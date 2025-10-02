"""
Page Summarizer Module - Simplified
Takes a news article URL and returns a reworded article with better title and content in English
"""

import requests
from bs4 import BeautifulSoup
import openai
import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

def read_website_content(url):
    """Read and extract content from a website URL"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = ""
        for selector in ['h1', '.entry-title', '.post-title', '.article-title', 'title']:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                break
        
        # Extract content - be more comprehensive and include more elements
        content = ""
        
        # Try to find main content area first
        for selector in ['.entry-content', '.post-content', '.article-content', '.content', 'article', 'main', '.main-content']:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove only essential unwanted elements, keep more content
                for unwanted in content_elem.select('script, style, .advertisement, .ads, .social-share, .comments'):
                    unwanted.decompose()
                content = content_elem.get_text(strip=True)
                break
        
        # If no main content found, get broader content including headers, paragraphs, and metadata
        if not content:
            # Include more elements that might contain important info like dates
            content_elements = soup.select('h1, h2, h3, h4, h5, h6, p, .date, .published, .meta, .author, .byline, .timestamp, time, .article-meta, .post-meta')
            content = ' '.join([elem.get_text(strip=True) for elem in content_elements if elem.get_text(strip=True)])
        
        # Final fallback - get all text but remove scripts and styles
        if not content:
            # Remove scripts and styles but keep everything else
            for script in soup(["script", "style"]):
                script.decompose()
            content = soup.get_text()
        
        return {'title': title, 'content': content}
        
    except Exception as e:
        return {'error': f'Failed to read website: {str(e)}'}

def summarize_with_gpt(title, content):
    """Send content to GPT for summarization and translation, returns JSON directly"""
    prompt = f"""You are a content analyzer and translator. Analyze this content and follow instructions.
            Title: {title}
            Content: {content}

            IMPORTANT INSTRUCTIONS:
            
            DEFAULT ACTION: Process and analyze ALL content and rewrite into a story or article.
            
            Return your response as a JSON object with the following structure:
            {{
                "title": "English title",
                "title_id": "Indonesian translation of the title",
                "date": "Try as best as possible to identify/predict date of publication based on the content or use today's date",
                "importance": "Score from 1-5 based on relevance and impact",
                "content": "You are a content writer, rewrite the article in english with your own analysis but style should be as a news article not a summary. Format the content with proper paragraphs separated by double newlines (\\n\\n) for better readability. Each paragraph should be well-structured and flow naturally. Make sure to rewrite and analyze the content, not just copy it.",
                "content_id": "Indonesian translation of the English content you wrote above. Translate your rewritten English article to Indonesian, maintaining the same structure and analysis."
            }}
            
            IMPORTANCE SCORING GUIDE:
            5 – Headline-Worthy: Breaking or major news with urgent, wide public impact (front-page material).
            4 – Strongly Relevant: Important developments of broad interest but less urgent than breaking news.
            3 – Moderately Relevant: General-interest or niche stories that are notable but not front-page.
            2 – Low Relevance: Local, promotional, or lightly reported stories with limited appeal.
            1 – Minimal Relevance: Advertisements, press releases, or filler content with no real news value.
            
            IMPORTANT: Return ONLY valid JSON. Do not include any other text or formatting."""
    try:
        # Use the centralized OpenAI utility with proper import handling
        import sys
        import os
        import json
        
        # Add parent directory to path to find utils
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
        
        from utils.openai_utils import call_openai
        gpt_result = call_openai(prompt, model="gpt-5-nano", max_tokens=2000, temperature=0.3)
        
        # Parse JSON response directly
        try:
            parsed_data = json.loads(gpt_result)
            
            # Validate required fields
            required_fields = ['title', 'title_id', 'content', 'content_id', 'date', 'importance']
            for field in required_fields:
                if field not in parsed_data:
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}',
                        'raw_result': gpt_result
                    }
            
            # Validate importance is between 1-5
            try:
                importance = int(parsed_data['importance'])
                if importance < 1 or importance > 5:
                    parsed_data['importance'] = 3  # Default to moderate relevance
            except (ValueError, TypeError):
                parsed_data['importance'] = 3
            
            # Parse date if it's a string
            if isinstance(parsed_data['date'], str):
                parsed_data['date'] = parse_date_string(parsed_data['date'])
            
            return {
                'success': True,
                **parsed_data,
                'raw_result': gpt_result
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Invalid JSON response: {str(e)}',
                'raw_result': gpt_result
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Error: {str(e)}"
        }

def parse_date_string(date_str):
    """Parse date string and return datetime object"""
    try:
        from datetime import datetime
        today = datetime.now()
        
        # Try to parse common date formats
        date_formats = [
            "%B %d, %Y",  # September 9, 2025
            "%B %d %Y",   # September 9 2025
            "%Y-%m-%d",   # 2025-09-09
            "%d/%m/%Y",   # 09/09/2025
            "%m/%d/%Y",   # 09/09/2025
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                # Check if date is in the future (news can't come from future)
                if parsed_date > today:
                    return today
                else:
                    return parsed_date
            except ValueError:
                continue
        
        # If parsing fails, use current date
        return today
        
    except Exception:
        # If all parsing fails, use current date
        return datetime.now()

def summarize_article_from_url(url):
    """Main function to summarize an article from URL"""
    # Read website content
    website_data = read_website_content(url)
    
    if 'error' in website_data:
        return website_data
    
    # Summarize with GPT
    gpt_result = summarize_with_gpt(website_data['title'], website_data['content'])
    
    # Check if GPT processing failed
    if not gpt_result.get('success'):
        return {
            'success': False,
            'error': gpt_result.get('error', 'Unknown error'),
            'url': url,
            'original_title': website_data['title'],
            'original_content': website_data['content'][:200] + '...' if len(website_data['content']) > 200 else website_data['content']
        }
    
    return {
        'success': True,
        'url': url,
        'original_title': website_data['title'],
        'original_content': website_data['content'],
        'parsed_data': gpt_result
    }

def save_article_to_database(url):
    """
    Complete workflow: summarize article, get image, and save to MongoDB
    
    Args:
        url (str): Article URL to process
    
    Returns:
        dict: Result of the operation with success status and details
    """
    try:
        # Step 0: Check if article already exists in database
        print(f"🔍 Checking if article already exists: {url}")
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        if not connection_string:
            return {
                'success': False,
                'error': 'MONGODB_CONNECTION_STRING not found in environment variables',
                'url': url
            }
        
        client = MongoClient(connection_string)
        db = client['beritabank']
        collection = db['news_articles']
        
        # Check if link already exists
        existing_article = collection.find_one({'link': url})
        if existing_article:
            return {
                'success': True,
                'message': 'Article already exists in database',
                'url': url,
                'database_id': str(existing_article['_id']),
                'existing': True
            }
        
        # Step 1: Summarize article from URL
        print(f"📰 Processing article: {url}")
        website_data = read_website_content(url)
        article_data = summarize_article_from_url(url)
        
        if not article_data.get('success'):
            return {
                'success': False,
                'error': f"Failed to summarize article: {article_data.get('error', 'Unknown error')}",
                'url': url
            }
        
        # Step 2: Extract parsed data from GPT result
        parsed_data = article_data['parsed_data']
        title = parsed_data['title']
        title_id = parsed_data['title_id']
        content = parsed_data['content']
        content_id = parsed_data['content_id']
        date = parsed_data['date']
        importance = parsed_data['importance']
        
        # Step 3: Get image URL using the article title
        print(f"🖼️  Searching for image with title: {website_data['title']}")
        try:
            from .imageretriever import get_first_image_url
        except ImportError:
            try:
                from models.imageretriever import get_first_image_url
            except ImportError:
                import sys
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                from imageretriever import get_first_image_url
        
        image_url = get_first_image_url(website_data['title'])
        
        if not image_url:
            print("⚠️  No image found for this article")
            image_url = "No image available"
        
        # Step 4: Save to database (connection already established)
        print(f"💾 Saving to database...")
        
        # Create document to insert
        article_document = {
            'link': url,
            'title': title,
            'title_id': title_id,
            'content': content,
            'content_id': content_id,
            'date': date,  # This is now a datetime object for proper sorting
            'date_string': date_str if 'date_str' in locals() else str(date),  # Original string for display
            'importance': importance,
            'image_url': image_url,
            'created_at': datetime.now().isoformat(),
            'original_title': article_data['original_title'],
            'original_content': article_data['original_content']
        }
        
        # Insert into database
        result = collection.insert_one(article_document)
        
        return {
            'success': True,
            'message': 'Article successfully saved to database',
            'url': url,
            'title': title,
            'date': date,
            'importance': importance,
            'image_url': image_url,
            'database_id': str(result.inserted_id)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Database operation failed: {str(e)}',
            'url': url
        }

if __name__ == "__main__":
    import json
    
    # Test with the provided InfoBank URL
    test_url = "https://infobanknews.com/realisasi-kur-tembus-rp190-triliun-penyaluran-ke-sektor-produksi-lebihi-target/"
    
    print("Testing Page Summarizer with InfoBank URL...")
    print("=" * 60)
    
    result = summarize_article_from_url(test_url)
    
    if result.get('success'):
        print("✅ SUCCESS!")
        print(f"📰 Original Title: {result['original_title']}")
        print(f"🔗 URL: {result['url']}")
        
        # Save parsed data to JSON file
        parsed_data = result['parsed_data']
        output_data = {
            'url': result['url'],
            'original_title': result['original_title'],
            'parsed_data': parsed_data
        }
        
        with open('page_summarizer_result.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        
        print("💾 Results saved to page_summarizer_result.json")
            
    else:
        print("❌ ERROR:")
        print(result.get('error', 'Unknown error occurred'))
