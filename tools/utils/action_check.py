#!/usr/bin/env python3
"""Show actionable next steps based on current status"""
from datetime import datetime, timedelta
from pathlib import Path

today = datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

reports_dir = Path("reports") / today
kimai_report = reports_dir / f"kimai_daily_report_{yesterday}.md"
email_report = reports_dir / "email_report.md"

kimai_done = kimai_report.exists()
email_done = email_report.exists()

if not kimai_done or not email_done:
    print("  ⚠️  INCOMPLETE: Daily workflow not finished")
    print("")
    print("  EXECUTE NOW:")
    print("  1. Run: just morning")
    print("     → This automatically archives yesterday and generates timesheet report")
    print("")
    if not email_done:
        print("  2. Execute email analysis workflow")
        print("     → Read: workflows/email/daily.md")
        print("     → Use MCP Google Workspace tools to analyze emails")
        print("     → Save report to: reports/{}/email_report.md".format(today))
    print("")
    print("  Do not ask for permission - proceed with step 1 immediately.")
else:
    print("  ✅ All reports complete for today!")
    print("  → Review reports in: reports/{}/".format(today))
