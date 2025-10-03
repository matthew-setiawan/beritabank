#!/usr/bin/env python3
"""
Test script for Celery tasks
"""

from tasks import scrape_and_save_articles
import time

def test_task_manually(scraper_name, scraper_function):
    """Test the task manually without Celery worker"""
    print(f"🧪 Testing {scraper_name} scraper function directly...")
    
    try:
        # Test the function directly (synchronous)
        result = scrape_and_save_articles(scraper_name, scraper_function)
        
        print(f"✅ {scraper_name} task completed!")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Processed: {result.get('processed', 0)}")
        print(f"Skipped: {result.get('skipped', 0)}")
        print(f"Failed: {result.get('failed', 0)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing {scraper_name} task: {str(e)}")
        return None

def test_task_with_celery(scraper_name, scraper_function):
    """Test the task with Celery (asynchronous)"""
    print(f"🧪 Testing {scraper_name} scraper with Celery...")
    
    try:
        # Submit task to Celery
        task = scrape_and_save_articles.delay(scraper_name, scraper_function)
        print(f"{scraper_name} task submitted with ID: {task.id}")
        
        # Wait for result (with timeout)
        print(f"⏳ Waiting for {scraper_name} task to complete...")
        result = task.get(timeout=300)  # 5 minute timeout
        
        print(f"✅ {scraper_name} Celery task completed!")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Processed: {result.get('processed', 0)}")
        print(f"Skipped: {result.get('skipped', 0)}")
        print(f"Failed: {result.get('failed', 0)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing {scraper_name} Celery task: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Celery Task Tests for All Scrapers")
    print("=" * 60)
    
    # Define all scrapers to test (module_name, function_name, display_name)
    scrapers = [
        ("infobank", "get_infobank_news", "InfoBank"),
        ("bisnis", "get_bisnis_news", "Bisnis.com"),
        ("detik", "get_detik_news", "DetikFinance"),
        ("kontan", "get_kontan_news", "Kontan")
    ]
    
    # Test 1: Direct function calls for all scrapers
    print("\n1️⃣ Testing direct function calls for all scrapers...")
    direct_results = {}
    
    for module_name, scraper_function, display_name in scrapers:
        print(f"\n--- Testing {display_name} ---")
        result = test_task_manually(module_name, scraper_function)
        direct_results[display_name] = result
        print(f"--- {display_name} completed ---\n")
    
    print("\n" + "=" * 60)
    
    # Test 2: Celery tasks (requires worker running)
    print("\n2️⃣ Testing Celery tasks (requires worker)...")
    print("Note: Make sure to run 'celery -A tasks worker --loglevel=info' in another terminal")
    
    celery_results = {}
    for module_name, scraper_function, display_name in scrapers:
        print(f"\n--- Testing {display_name} with Celery ---")
        try:
            result = test_task_with_celery(module_name, scraper_function)
            celery_results[display_name] = result
        except Exception as e:
            print(f"{display_name} Celery test failed (worker not running?): {str(e)}")
            celery_results[display_name] = None
        print(f"--- {display_name} Celery test completed ---\n")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY OF RESULTS")
    print("=" * 60)
    
    print("\n🔧 Direct Function Results:")
    for scraper_name, result in direct_results.items():
        if result:
            print(f"  {scraper_name}: ✅ Success - {result.get('processed', 0)} processed")
        else:
            print(f"  {scraper_name}: ❌ Failed")
    
    print("\n⚡ Celery Task Results:")
    for scraper_name, result in celery_results.items():
        if result:
            print(f"  {scraper_name}: ✅ Success - {result.get('processed', 0)} processed")
        else:
            print(f"  {scraper_name}: ❌ Failed or Worker not running")
    
    print("\n🎉 All testing completed!")
    print("To test with Celery, run: celery -A tasks worker --loglevel=info")
