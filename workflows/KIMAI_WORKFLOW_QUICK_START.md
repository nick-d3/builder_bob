# Kimai Workflow Quick Start Guide

## Quick Commands

### Generate Daily Report (Yesterday)
```bash
python3 /Users/ndamico/agents/workflow/kimai_report_generator.py --daily
```

### Generate Weekly Report (Last Week)
```bash
python3 /Users/ndamico/agents/workflow/kimai_report_generator.py --weekly
```

### Generate Both Reports
```bash
python3 /Users/ndamico/agents/workflow/kimai_report_generator.py --both
```

### Generate Report for Specific Date
```bash
# Daily report for specific date
python3 /Users/ndamico/agents/workflow/kimai_report_generator.py --daily --date 2025-11-13

# Weekly report starting on specific Monday
python3 /Users/ndamico/agents/workflow/kimai_report_generator.py --weekly --week 2025-11-10
```

## What Gets Detected

### 🔴 Critical Issues
- **Not Clocked Out:** Employee forgot to clock out
- **Stale Timers:** Active timer running > 24 hours
- **Very Long Entry:** Single entry > 14 hours (likely forgot to clock out)

### ⚠️ Warnings
- **Over 13 Hours:** Employee worked > 13 hours in a day
- **Excessive Weekly Hours:** > 60 hours in a week
- **Multiple Long Days:** 3+ days with > 13 hours
- **High Average:** Average > 12 hours/day

### 🟡 Low Priority
- **Very Short Entries:** < 0.5 hours (may be test/error)

## Report Locations

Reports are saved in date-organized folders:
- **Daily Reports:** `/Users/ndamico/agents/reports/YYYY-MM-DD/kimai_daily_report_YYYY-MM-DD.md`
- **Weekly Reports:** `/Users/ndamico/agents/reports/YYYY-MM-DD/kimai_weekly_report_YYYY-MM-DD.md` (using Monday's date)

## Automation

### Daily Report (Cron)
Add to crontab to run every morning at 8 AM:
```bash
0 8 * * * /usr/bin/python3 /Users/ndamico/agents/workflow/kimai_report_generator.py --daily
```

### Weekly Report (Cron)
Add to crontab to run every Monday at 8 AM:
```bash
0 8 * * 1 /usr/bin/python3 /Users/ndamico/agents/workflow/kimai_report_generator.py --weekly
```

## Manual API Usage

If you need to query the API directly:

```bash
# Get yesterday's timesheets
YESTERDAY=$(python3 -c "from datetime import datetime, timedelta; print((datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))")
curl -s -H "Authorization: Bearer 5f3d0820c5af4456937441752" \
  -H "Accept: application/json" \
  "https://tracking.damico.construction/api/timesheets?user=all&begin=${YESTERDAY}T00:00:00&end=${YESTERDAY}T23:59:59&size=200"

# Get active timers
curl -s -H "Authorization: Bearer 5f3d0820c5af4456937441752" \
  -H "Accept: application/json" \
  "https://tracking.damico.construction/api/timesheets?user=all&active=1"
```

## Troubleshooting

### "401 Unauthorized"
- Check that the token is valid
- Verify token has `view_other_timesheet` permission

### "Empty Results"
- Verify date range is correct
- Ensure `?user=all` parameter is included
- Check that employees actually worked on that date

### "Module not found: requests"
Install required Python package:
```bash
pip3 install requests
```

