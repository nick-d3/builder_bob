#!/usr/bin/env python3
"""Archive yesterday's reports to history"""
from datetime import datetime, timedelta
from pathlib import Path
import shutil

yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
yesterday_dir = Path("reports") / yesterday
history_dir = Path("reports") / "history"
target_dir = history_dir / yesterday

if yesterday_dir.exists():
    history_dir.mkdir(exist_ok=True)
    if not target_dir.exists():
        shutil.move(str(yesterday_dir), str(target_dir))
        print(f"✅ Archived reports/{yesterday} to reports/history/{yesterday}")
    else:
        print(f"⚠️  reports/history/{yesterday} already exists, skipping archive")
else:
    print(f"ℹ️  No reports folder found for {yesterday}, nothing to archive")

