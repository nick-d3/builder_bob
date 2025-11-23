#!/usr/bin/env python3
"""Show today's context"""
from datetime import datetime, timedelta

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

print(f"  Reports folder: reports/{today}/")
print(f"  Yesterday: {yesterday} - timesheet data")

