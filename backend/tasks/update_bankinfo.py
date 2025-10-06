#!/usr/bin/env python3
"""
Bank info update functionality - direct function calls without Celery
"""

import datetime
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Default bank names to process
DEFAULT_BANK_NAMES = [
    # Major State-Owned Banks
    "Bank Mandiri",
    "Bank Rakyat Indonesia (BRI)",
    "Bank Negara Indonesia (BNI)",
    "Bank Tabungan Negara (BTN)",
    
    # Major Private Banks
    "Bank Central Asia (BCA)",
    "Bank Danamon",
    "Bank Permata",
    "Bank CIMB Niaga",
    "Bank OCBC NISP",
    "Bank Maybank Indonesia",
    "Bank UOB Indonesia",
    "Bank Standard Chartered",
    "Bank HSBC Indonesia",
    "Bank Citibank Indonesia",
    "Bank Deutsche Bank Indonesia",
    
    # Regional Development Banks
    "Bank DKI",
    "Bank Jateng",
    "Bank Jatim",
    "Bank Jabar Banten",
    "Bank Sumut",
    "Bank Sumsel Babel",
    "Bank Kaltim",
    "Bank Kalbar",
    "Bank Sulselbar",
    "Bank Papua",
    
    # Other Notable Banks
    "Bank Mayapada",
    "Bank Mega",
    "Bank Sinarmas",
    "Bank BTPN",
    "Bank Akasia Mas",
    "Neo Bank Commerce",
    "Bank Jago",
    "Bank Seabank",
]


def update_bank_info(bank_names=None, country="Indonesia"):
    """
    Update (upsert) bank information for a list of bank names.

    Args:
        bank_names (list[str]): List of bank names to process. If None, uses a default list.
        country (str): Country context passed to the summarizer.
    
    Returns:
        dict: Result summary with success status, counts, and details
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


def update_bank_info_custom(bank_names, country="Indonesia"):
    """
    Update bank information for a custom list of bank names.
    
    Args:
        bank_names (list[str]): Custom list of bank names to process
        country (str): Country context passed to the summarizer
    
    Returns:
        dict: Result summary with success status, counts, and details
    """
    return update_bank_info(bank_names, country)


def update_bank_info_default():
    """
    Update bank information using the default list of banks.
    
    Returns:
        dict: Result summary with success status, counts, and details
    """
    return update_bank_info()


if __name__ == "__main__":
    print("🧪 Testing Bank Info Update Functions")
    print("=" * 50)
    
    # Test with default banks
    print("\n1️⃣ Testing with default bank list...")
    result = update_bank_info_default()
    
    if result:
        print(f"✅ Default banks test completed!")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Updated: {result.get('updated', 0)}")
        print(f"Inserted: {result.get('inserted', 0)}")
        print(f"Failed: {result.get('failed', 0)}")
    else:
        print("❌ Default banks test failed!")
    
    print("\n" + "=" * 50)
    
    # Test with custom bank list
    print("\n2️⃣ Testing with custom bank list...")
    custom_banks = [
        "Bank Mandiri",
        "Bank Central Asia (BCA)",
        "Bank Rakyat Indonesia (BRI)"
    ]
    
    custom_result = update_bank_info_custom(custom_banks, "Indonesia")
    
    if custom_result:
        print(f"✅ Custom banks test completed!")
        print(f"Success: {custom_result.get('success')}")
        print(f"Message: {custom_result.get('message')}")
        print(f"Updated: {custom_result.get('updated', 0)}")
        print(f"Inserted: {custom_result.get('inserted', 0)}")
        print(f"Failed: {custom_result.get('failed', 0)}")
    else:
        print("❌ Custom banks test failed!")
    
    print("\n🎉 Testing completed!")
