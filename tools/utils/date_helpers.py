#!/usr/bin/env python3
"""Date helper utilities for justfile commands"""
import sys
from datetime import datetime, timedelta

if len(sys.argv) < 2:
    sys.exit(1)

command = sys.argv[1]

if command == "today":
    print(datetime.now().strftime('%Y-%m-%d'))
elif command == "yesterday":
    yesterday = datetime.now() - timedelta(days=1)
    print(yesterday.strftime('%Y-%m-%d'))
else:
    sys.exit(1)

