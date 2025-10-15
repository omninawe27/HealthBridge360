#!/usr/bin/env python
import os
import sys
import django
import requests

# Setup Django environment
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthkart360.settings')

# Set environment variables for testing
os.environ['SECRET_KEY'] = 'test-key-for-debug'
os.environ['DEBUG'] = 'True'
os.environ['RATE_LIMIT_REQUESTS'] = '5'
os.environ['DATABASE_URL'] = 'sqlite:///db.sqlite3'

django.setup()

print("Testing rate limiting...")

# Test rate limiting
for i in range(8):
    try:
        r = requests.get('http://127.0.0.1:8000/')
        print(f'Request {i+1}: Status {r.status_code}')
        if r.status_code == 429:
            print("Rate limit triggered!")
            break
    except Exception as e:
        print(f'Request {i+1}: Error {e}')
        break
