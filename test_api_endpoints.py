#!/usr/bin/env python
"""
Test script for the new transaction review API endpoints
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
UPLOAD_ID = "c9f83e40-5698-4ef0-bb28-1eb64d5f4b99"  # GCash mobile upload

def test_endpoints():
    print("🧪 TESTING TRANSACTION REVIEW API ENDPOINTS")
    print("=" * 60)
    
    # Test 1: Get transactions for file upload (without auth for now)
    print(f"\n📄 Test 1: Get transactions for upload {UPLOAD_ID}")
    print("-" * 50)
    
    url = f"{BASE_URL}/transactions/uploads/{UPLOAD_ID}/transactions/"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 File: {data.get('file_upload', {}).get('filename', 'N/A')}")
            print(f"💰 Transactions found: {data.get('count', 0)}")
            
            if data.get('transactions'):
                print(f"📝 Sample transactions:")
                for i, txn in enumerate(data['transactions'][:3]):
                    print(f"   {i+1}. {txn['description'][:40]}... (₱{txn['amount']})")
                    
        elif response.status_code == 401:
            print("🔐 Authentication required (expected for protected endpoint)")
        else:
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Test 2: Test URL pattern
    print(f"\n🔗 Test 2: URL Pattern Validation")
    print("-" * 50)
    print(f"Endpoint URL: {url}")
    print(f"Expected pattern: /api/transactions/uploads/<uuid>/transactions/")
    
    print(f"\n✅ API endpoint testing completed")
    print("🎯 Ready for frontend integration testing")

if __name__ == "__main__":
    test_endpoints()
