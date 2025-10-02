from celery import Celery
from celery.schedules import crontab
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default bank names to process (can be reused in beat schedule args)
DEFAULT_BANK_NAMES = [
    "Bank Akasia Mas",
    "Bank Mayapada",
    "Bank Central Asia",
    "Bank Mandiri",
    "Bank BNI",
    "Neo Bank Commerce",
]

# Configure Celery with Redis
celery = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery.task
def scrape_and_save_articles(scraper_name, scraper_function_name):
    """
    Generic Celery task to scrape articles from any scraper and save them to database
    
    Args:
        scraper_name (str): Name of the scraper (e.g., 'infobank', 'bbc')
        scraper_function_name (str): Function name to call (e.g., 'get_infobank_news', 'get_bbc_news')
    """
    try:
        now = datetime.datetime.utcnow().isoformat()
        print(f"[{now}] Starting {scraper_name} scraping task...")
        
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

# New: Update bank information task
@celery.task
def update_bank_info(bank_names=None, country="Indonesia"):
    """
    Update (upsert) bank information for a list of bank names.

    Args:
        bank_names (list[str]): List of bank names to process. If None, uses a default list.
        country (str): Country context passed to the summarizer.
    """
    now = datetime.datetime.utcnow().isoformat()
    try:
        if bank_names is None:
            bank_names = DEFAULT_BANK_NAMES

        from models.banksummarizer import save_bankinfo_to_database

        results = []
        updated = 0
        inserted = 0
        failed = 0

        print(f"[{now}] Starting bank info update for {len(bank_names)} banks...")

        for idx, name in enumerate(bank_names, start=1):
            try:
                print(f"[{now}] ({idx}/{len(bank_names)}) Processing: {name}")
                res = save_bankinfo_to_database(name, country=country)
                if res.get('success'):
                    op = res.get('operation')
                    if op == 'updated':
                        updated += 1
                    elif op == 'inserted':
                        inserted += 1
                else:
                    failed += 1
                results.append({"bank": name, "result": res})
            except Exception as e:
                failed += 1
                results.append({"bank": name, "error": str(e)})

        summary = {
            'success': True,
            'message': f'Bank info update completed. Updated: {updated}, Inserted: {inserted}, Failed: {failed}',
            'updated': updated,
            'inserted': inserted,
            'failed': failed,
            'total': len(bank_names),
            'results': results,
            'timestamp': now,
        }
        print(f"[{now}] {summary['message']}")
        return summary

    except Exception as e:
        error_msg = f"Bank info task failed with exception: {str(e)}"
        print(f"[{now}] {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'updated': 0,
            'inserted': 0,
            'failed': 0,
            'total': 0,
            'results': [],
            'timestamp': now,
        }

# Schedule the tasks
celery.conf.beat_schedule = {
    "scrape-infobank-daily": {
        "task": "tasks.scrape_and_save_articles",
        "schedule": crontab(hour=0, minute=0),  # every day at midnight UTC
        "args": ("infobank", "get_infobank_news"),  # scraper_name, function_name
    },
    "update-bank-info-daily": {
        "task": "tasks.update_bank_info",
        "schedule": crontab(hour=1, minute=0),  # daily at 01:00 UTC
        "args": (DEFAULT_BANK_NAMES, "Indonesia"),
    },
}
celery.conf.timezone = "UTC"