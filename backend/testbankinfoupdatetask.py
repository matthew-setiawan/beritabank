#!/usr/bin/env python3
"""
Test script for the bank info Celery task
"""

from tasks import update_bank_info, DEFAULT_BANK_NAMES


def test_task_manually():
    """Test the task manually without Celery worker"""
    print("🧪 Testing update_bank_info function directly...")

    try:
        # Synchronous call
        result = update_bank_info(DEFAULT_BANK_NAMES, country="Indonesia")

        print("✅ Task completed!")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Updated: {result.get('updated', 0)}")
        print(f"Inserted: {result.get('inserted', 0)}")
        print(f"Failed: {result.get('failed', 0)}")

        return result

    except Exception as e:
        print(f"❌ Error testing task: {str(e)}")
        return None


def test_task_with_celery():
    """Test the task with Celery (asynchronous)"""
    print("🧪 Testing update_bank_info with Celery...")

    try:
        # Submit task to Celery
        task = update_bank_info.delay(DEFAULT_BANK_NAMES, country="Indonesia")
        print(f"Task submitted with ID: {task.id}")

        print("⏳ Waiting for task to complete...")
        result = task.get(timeout=600)  # up to 10 minutes

        print("✅ Celery task completed!")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Updated: {result.get('updated', 0)}")
        print(f"Inserted: {result.get('inserted', 0)}")
        print(f"Failed: {result.get('failed', 0)}")

        return result

    except Exception as e:
        print(f"❌ Error testing Celery task: {str(e)}")
        return None


if __name__ == "__main__":
    print("🚀 Starting Bank Info Celery Task Tests")
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
