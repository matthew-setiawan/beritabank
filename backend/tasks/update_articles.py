#!/usr/bin/env python3
"""
Article update functionality - direct function calls without Celery
"""

import datetime
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_articles(scraper_name, scraper_function_name):
    """
    Generic function to scrape articles from any scraper and save them to database
    
    Args:
        scraper_name (str): Name of the scraper (e.g., 'infobank', 'bisnis')
        scraper_function_name (str): Function name to call (e.g., 'get_infobank_news', 'get_bisnis_news')
    
    Returns:
        dict: Result summary with success status, counts, and details
    """
    try:
        now = datetime.datetime.utcnow().isoformat()
        print(f"[{now}] Starting {scraper_name} scraping...")
        
        # Import the required modules
        from models.pagesummarizer import save_article_to_database
        
        # Dynamically import the scraper function
        scraper_module = __import__(f'scrapers.{scraper_name}_scraper', fromlist=[scraper_function_name])
        scraper_function = getattr(scraper_module, scraper_function_name)
        
        # Step 1: Get headlines and links from the scraper
        print(f"[{now}] Scraping {scraper_name} headlines...")
        scraper_data = scraper_function()
        
        if not scraper_data.get('success'):
            error_msg = f"Failed to scrape {scraper_name}: {scraper_data.get('error', 'Unknown error')}"
            print(f"[{now}] {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'scraper': scraper_name,
                'processed': 0,
                'skipped': 0,
                'failed': 0
            }
        
        headlines = scraper_data.get('headlines', [])
        print(f"[{now}] Found {len(headlines)} headlines from {scraper_name}")
        
        # Step 2: Process each article link
        processed_count = 0
        skipped_count = 0
        failed_count = 0
        results = []
        
        for i, headline in enumerate(headlines):
            link = headline.get('link')
            title = headline.get('title', 'Unknown Title')
            
            if not link:
                print(f"[{now}] Skipping headline {i+1}: No link found")
                failed_count += 1
                continue
            
            print(f"[{now}] Processing article {i+1}/{len(headlines)}: {title[:50]}...")
            
            try:
                # Save article to database (includes duplicate check)
                result = save_article_to_database(link)
                
                if result.get('success'):
                    if result.get('existing'):
                        print(f"[{now}] Article {i+1} already exists in database")
                        skipped_count += 1
                    else:
                        print(f"[{now}] Article {i+1} successfully saved to database")
                        processed_count += 1
                else:
                    print(f"[{now}] Failed to process article {i+1}: {result.get('error', 'Unknown error')}")
                    failed_count += 1
                
                results.append({
                    'title': title,
                    'link': link,
                    'result': result
                })
                
            except Exception as e:
                error_msg = f"Exception processing article {i+1}: {str(e)}"
                print(f"[{now}] {error_msg}")
                failed_count += 1
                results.append({
                    'title': title,
                    'link': link,
                    'error': error_msg
                })
        
        # Summary
        summary = {
            'success': True,
            'message': f'{scraper_name.title()} scraping completed. Processed: {processed_count}, Skipped: {skipped_count}, Failed: {failed_count}',
            'scraper': scraper_name,
            'total_headlines': len(headlines),
            'processed': processed_count,
            'skipped': skipped_count,
            'failed': failed_count,
            'results': results,
            'timestamp': now
        }
        
        print(f"[{now}] Task completed: {summary['message']}")
        return summary
        
    except Exception as e:
        error_msg = f"Task failed with exception: {str(e)}"
        print(f"[{now}] {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'scraper': scraper_name,
            'processed': 0,
            'skipped': 0,
            'failed': 0,
            'timestamp': now
        }


def update_all_articles():
    """
    Update articles from all available scrapers
    
    Returns:
        dict: Combined results from all scrapers
    """
    # Define all scrapers to process
    scrapers = [
        ("infobank", "get_infobank_news", "InfoBank"),
        ("bisnis", "get_bisnis_news", "Bisnis.com"),
        ("detik", "get_detik_news", "DetikFinance"),
        ("kontan", "get_kontan_news", "Kontan")
    ]
    
    all_results = {}
    total_processed = 0
    total_skipped = 0
    total_failed = 0
    
    print("🚀 Starting article updates for all scrapers")
    print("=" * 60)
    
    for module_name, scraper_function, display_name in scrapers:
        print(f"\n--- Processing {display_name} ---")
        result = update_articles(module_name, scraper_function)
        all_results[display_name] = result
        
        if result and result.get('success'):
            total_processed += result.get('processed', 0)
            total_skipped += result.get('skipped', 0)
            total_failed += result.get('failed', 0)
            print(f"✅ {display_name}: {result.get('processed', 0)} processed, {result.get('skipped', 0)} skipped, {result.get('failed', 0)} failed")
        else:
            print(f"❌ {display_name}: Failed")
        print(f"--- {display_name} completed ---\n")
    
    # Overall summary
    overall_summary = {
        'success': True,
        'message': f'All scrapers completed. Total - Processed: {total_processed}, Skipped: {total_skipped}, Failed: {total_failed}',
        'total_processed': total_processed,
        'total_skipped': total_skipped,
        'total_failed': total_failed,
        'scraper_results': all_results,
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    
    print("=" * 60)
    print("📊 OVERALL SUMMARY")
    print("=" * 60)
    print(f"Total Processed: {total_processed}")
    print(f"Total Skipped: {total_skipped}")
    print(f"Total Failed: {total_failed}")
    print("🎉 All article updates completed!")
    
    return overall_summary


if __name__ == "__main__":
    print("🧪 Testing Article Update Functions")
    print("=" * 50)
    
    # Test individual scraper
    print("\n1️⃣ Testing individual scraper (InfoBank)...")
    result = update_articles("infobank", "get_infobank_news")
    
    if result:
        print(f"✅ Individual test completed!")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Processed: {result.get('processed', 0)}")
        print(f"Skipped: {result.get('skipped', 0)}")
        print(f"Failed: {result.get('failed', 0)}")
    else:
        print("❌ Individual test failed!")
    
    print("\n" + "=" * 50)
    
    # Test all scrapers
    print("\n2️⃣ Testing all scrapers...")
    all_results = update_all_articles()
    
    if all_results:
        print(f"✅ All scrapers test completed!")
        print(f"Total Processed: {all_results.get('total_processed', 0)}")
        print(f"Total Skipped: {all_results.get('total_skipped', 0)}")
        print(f"Total Failed: {all_results.get('total_failed', 0)}")
    else:
        print("❌ All scrapers test failed!")
    
    print("\n🎉 Testing completed!")
