#!/usr/bin/env python3
"""Status check for today's reports"""
from datetime import datetime, timedelta
from pathlib import Path

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

reports_dir = Path("reports") / today
kimai_report = reports_dir / f"kimai_daily_report_{yesterday}.md"
email_report = reports_dir / "email_report.md"

print(f"📊 Today's Status: {today}")
if kimai_report.exists():
    print("  ✅ Timesheet report: Generated")
else:
    print("  ⚠️  Timesheet report: Pending")

if email_report.exists():
    print("  ✅ Email analysis: Generated")
else:
    print("  ⚠️  Email analysis: Pending")

print(f"  📁 Reports folder: reports/{today}/")

