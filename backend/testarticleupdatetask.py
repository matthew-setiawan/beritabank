#!/usr/bin/env python3
"""
Test script for Celery tasks
"""

from tasks import scrape_and_save_articles
import time

def test_task_manually():
    """Test the task manually without Celery worker"""
    print("🧪 Testing scrape_and_save_articles function directly...")
    
    try:
        # Test the function directly (synchronous)
        result = scrape_and_save_articles("infobank", "get_infobank_news")
        
        print("✅ Task completed!")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Processed: {result.get('processed', 0)}")
        print(f"Skipped: {result.get('skipped', 0)}")
        print(f"Failed: {result.get('failed', 0)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing task: {str(e)}")
        return None

def test_task_with_celery():
    """Test the task with Celery (asynchronous)"""
    print("🧪 Testing scrape_and_save_articles with Celery...")
    
    try:
        # Submit task to Celery
        task = scrape_and_save_articles.delay("infobank", "get_infobank_news")
        print(f"Task submitted with ID: {task.id}")
        
        # Wait for result (with timeout)
        print("⏳ Waiting for task to complete...")
        result = task.get(timeout=300)  # 5 minute timeout
        
        print("✅ Celery task completed!")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Processed: {result.get('processed', 0)}")
        print(f"Skipped: {result.get('skipped', 0)}")
        print(f"Failed: {result.get('failed', 0)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing Celery task: {str(e)}")
        return None

if __name__ == "__main__":
    print("🚀 Starting Celery Task Tests")
    print("=" * 50)
    
    # Test 1: Direct function call
    print("\n1️⃣ Testing direct function call...")
    direct_result = test_task_manually()
    
    print("\n" + "=" * 50)
    
    # Test 2: Celery task (requires worker running)
    print("\n2️⃣ Testing Celery task (requires worker)...")
    print("Note: Make sure to run 'celery -A tasks worker --loglevel=info' in another terminal")
    
    try:
        celery_result = test_task_with_celery()
    except Exception as e:
        print(f"Celery test failed (worker not running?): {str(e)}")
        print("To test with Celery, run: celery -A tasks worker --loglevel=info")
    
    print("\n🎉 Testing completed!")
