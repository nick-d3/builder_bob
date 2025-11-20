# Kimai Daily & Weekly Report Workflow Instructions

## Purpose
This workflow automates the process of analyzing Kimai timesheet data to generate daily and weekly reports with alerts for suspicious or out-of-norm activity.

## Key Features
- **Daily Log:** Who worked yesterday, hours worked, clock-in/out status
- **Weekly Log:** Summary of the week's work across all employees
- **Suspicious Activity Alerts:** Flags for unusual patterns (over 13 hours, not clocked out, etc.)
- **Active Timer Monitoring:** Tracks employees currently clocked in

## API Configuration
- **Base URL:** `https://tracking.damico.construction`
- **Token:** Use the admin token with `view_other_timesheet` permission
- **Critical Parameter:** Always use `?user=all` to see all employees' timesheets

## Steps to Execute - Daily Report

### 1. Get Yesterday's Date
Calculate yesterday's date in YYYY-MM-DD format:
```python
from datetime import datetime, timedelta
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
begin = f"{yesterday}T00:00:00"
end = f"{yesterday}T23:59:59"
```

### 2. Query Yesterday's Timesheets
Use the Kimai API directly (bypassing MCP bug):
```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  -H "Accept: application/json" \
  "https://tracking.damico.construction/api/timesheets?user=all&begin=${BEGIN}&end=${END}&size=200"
```

**Note:** The MCP server has a bug where `user_scope: "all"` doesn't pass `?user=all`. Use the API directly or ensure the MCP server is fixed.

### 3. Query Active Timers
Check for employees currently clocked in:
```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  -H "Accept: application/json" \
  "https://tracking.damico.construction/api/timesheets?user=all&active=1"
```

### 4. Get User Information
Map user IDs to names:
```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  -H "Accept: application/json" \
  "https://tracking.damico.construction/api/users"
```

### 5. Analyze Daily Data
For each employee who worked yesterday, calculate:
- **Total Hours:** Sum of all timesheet durations for the day
- **Number of Entries:** Count of timesheet entries
- **Clock-Out Status:** Check if any entries have `end: null` (not clocked out)
- **Hours Over 13:** Flag if total hours > 13
- **Multiple Entries:** Note if employee has multiple clock-in/out cycles

### 6. Detect Suspicious Activity
Flag the following as suspicious:
- **Over 13 Hours:** Total hours worked > 13 in a single day
- **Not Clocked Out:** Any timesheet entry with `end: null`
- **Stale Active Timers:** Active timers running for > 24 hours
- **Very Short Entries:** Entries < 0.5 hours (may indicate errors)
- **Very Long Single Entry:** Single entry > 14 hours (may indicate forgot to clock out)
- **Multiple Long Entries:** Multiple entries totaling > 15 hours

### 7. Generate Daily Report
Create a markdown report with the following sections:

#### Report Structure:
1. **Executive Summary**
   - Date of report
   - Total employees who worked
   - Total hours worked
   - Number of suspicious activities found

2. **Daily Work Summary**
   - Table of all employees who worked
   - Columns: User ID, Name, Entries, Hours, Status
   - Sort by hours (descending)

3. **Suspicious Activity Alerts**
   - **Over 13 Hours:** List employees who worked > 13 hours
   - **Not Clocked Out:** List employees with unclosed entries
   - **Stale Timers:** List active timers running > 24 hours
   - **Other Anomalies:** Very short/long entries, etc.

4. **Active Timers**
   - List of employees currently clocked in
   - Show start time and duration running
   - Flag stale timers (> 24 hours)

5. **Detailed Breakdown**
   - For each employee, show:
     - Clock-in times
     - Clock-out times
     - Duration per entry
     - Project/Activity worked on
     - Description (if any)

### 8. Save Daily Report
Save the report in the date-organized folder:
```
DATE=$(date +%F)  # or whichever date the report covers
mkdir -p /Users/ndamico/agents/reports/${DATE}
/Users/ndamico/agents/reports/${DATE}/kimai_daily_report_${DATE}.md
```

---

## Steps to Execute - Weekly Report

### 1. Calculate Week Range
Determine the week (Monday to Sunday):
```python
from datetime import datetime, timedelta
today = datetime.now()
# Get Monday of current week
monday = today - timedelta(days=today.weekday())
sunday = monday + timedelta(days=6)
begin = f"{monday.strftime('%Y-%m-%d')}T00:00:00"
end = f"{sunday.strftime('%Y-%m-%d')}T23:59:59"
```

### 2. Query Week's Timesheets
```bash
curl -s -H "Authorization: Bearer <TOKEN>" \
  -H "Accept: application/json" \
  "https://tracking.damico.construction/api/timesheets?user=all&begin=${BEGIN}&end=${END}&size=500"
```

### 3. Analyze Weekly Data
For each employee, calculate:
- **Total Hours:** Sum of all hours for the week
- **Days Worked:** Count of unique days with timesheet entries
- **Average Hours/Day:** Total hours / days worked
- **Days with Over 13 Hours:** Count of days where employee worked > 13 hours
- **Unclosed Entries:** Count of entries not clocked out during the week
- **Projects Worked:** List of unique projects
- **Activities:** List of unique activities

### 4. Detect Weekly Suspicious Activity
Flag:
- **Excessive Weekly Hours:** Total hours > 60 for the week
- **Too Many Days Over 13 Hours:** 3+ days with > 13 hours
- **Inconsistent Patterns:** Employee worked some days but not others (if expected to work full week)
- **Multiple Unclosed Entries:** 2+ entries not clocked out during the week
- **Very High Average:** Average hours/day > 12

### 5. Generate Weekly Report
Create a markdown report with:

#### Report Structure:
1. **Executive Summary**
   - Week range (Monday - Sunday)
   - Total employees who worked
   - Total hours across all employees
   - Average hours per employee
   - Suspicious activities summary

2. **Weekly Summary by Employee**
   - Table with: User ID, Name, Total Hours, Days Worked, Avg Hours/Day, Status
   - Sort by total hours (descending)

3. **Suspicious Activity Alerts**
   - **Excessive Weekly Hours:** Employees with > 60 hours
   - **Multiple Long Days:** Employees with 3+ days over 13 hours
   - **Unclosed Entries:** Employees with multiple unclosed entries
   - **Inconsistent Patterns:** Employees with unusual work patterns

4. **Top Performers**
   - Employees with highest total hours
   - Employees with most days worked
   - Employees with highest average hours/day

5. **Project Summary**
   - Hours by project
   - Employees per project
   - Most active projects

6. **Daily Breakdown**
   - Summary table showing hours per day for each employee
   - Highlight days with > 13 hours

### 6. Save Weekly Report
Save the report in the date-organized folder (using Monday's date):
```
MONDAY_DATE=$(date -v-mon +%F 2>/dev/null || date -d "last monday" +%F)  # Monday's date
mkdir -p /Users/ndamico/agents/reports/${MONDAY_DATE}
/Users/ndamico/agents/reports/${MONDAY_DATE}/kimai_weekly_report_${MONDAY_DATE}.md
```
(Use Monday's date for the filename)

---

## Suspicious Activity Thresholds

### Daily Thresholds
- **Over 13 Hours:** ⚠️ Warning - May indicate overtime or forgot to clock out
- **Not Clocked Out:** 🔴 Critical - Employee forgot to clock out
- **Stale Timer (> 24h):** 🔴 Critical - Timer running for over 24 hours
- **Very Short Entry (< 0.5h):** 🟡 Low - May be a test or error
- **Very Long Entry (> 14h):** 🔴 Critical - Likely forgot to clock out
- **Multiple Entries > 15h total:** ⚠️ Warning - Unusual pattern

### Weekly Thresholds
- **Total Hours > 60:** ⚠️ Warning - Excessive weekly hours
- **3+ Days Over 13 Hours:** ⚠️ Warning - Pattern of long days
- **Average Hours/Day > 12:** ⚠️ Warning - Consistently high hours
- **2+ Unclosed Entries:** 🔴 Critical - Multiple clock-out issues
- **Days Worked < 3 (if expected 5):** 🟡 Low - May indicate absence

---

## User ID to Name Mapping

Maintain this mapping for reports:
```python
user_map = {
    1: "admin", 2: "Nick D'Amico", 3: "Lori Holcomb", 4: "nbendas", 5: "John Burke",
    6: "Bill D'Amico", 7: "Troy Lindsay", 8: "Brandan Thomas", 9: "Carl Robinson",
    10: "Joe Loveall", 11: "Nate Loveall", 12: "Ben Olmo", 13: "Danny Lozada",
    14: "Elizabeth D'Amico", 15: "Alex Anglace", 16: "Stephen Calway", 17: "Joshua",
    18: "Timothy Genovese", 19: "Steven Hechevarria", 20: "Christopher Johnson",
    21: "Oscar Morales", 22: "Benjamin Paxton", 23: "Bill Rivera", 24: "Colby Sanden",
    25: "Randall Wuchert", 26: "Mike Echevarria"
}
```

Or fetch dynamically from `/api/users` endpoint.

---

## Report Formatting Guidelines

### Markdown Formatting
- Use headers (##, ###) for sections
- Use emoji indicators:
  - 🔴 Critical issues
  - ⚠️ Warnings
  - 🟡 Low priority alerts
  - ✅ Normal/OK status
- Use tables for data presentation
- Use code blocks for timestamps and IDs
- Include horizontal rules (---) between major sections

### Status Indicators
- **✅ OK:** Normal hours, clocked out properly
- **⚠️ WARNING:** Over 13 hours, but clocked out
- **🔴 CRITICAL:** Not clocked out, stale timer, or excessive hours

---

## Automation Schedule

### Daily Report
- **Trigger:** Daily (can be scheduled via cron or automation)
- **Time:** Run in morning to review previous day
- **Output:** `kimai_daily_report_YYYY-MM-DD.md`

### Weekly Report
- **Trigger:** Weekly (Monday morning for previous week)
- **Time:** Run Monday morning to review previous week
- **Output:** `kimai_weekly_report_YYYY-MM-DD.md` (Monday's date)

---

## Example Queries to Trigger This Workflow

When the user asks to:
- "Generate daily timesheet report"
- "Who worked yesterday?"
- "Check for employees who didn't clock out"
- "Find employees who worked over 13 hours"
- "Generate weekly timesheet report"
- "Review this week's hours"
- "Check for suspicious activity"

Execute this workflow to:
1. Query Kimai API for timesheet data
2. Analyze hours, clock-in/out status
3. Detect suspicious patterns
4. Generate comprehensive markdown reports
5. Highlight issues requiring attention

---

## API Usage Notes

### Critical: Use `?user=all` Parameter
The Kimai API requires `?user=all` to see all employees' timesheets. Without it, only the token owner's timesheets are returned.

**Correct:**
```
/api/timesheets?user=all&begin=2025-11-13T00:00:00&end=2025-11-13T23:59:59
```

**Incorrect (MCP bug):**
```
/api/timesheets?begin=2025-11-13T00:00:00&end=2025-11-13T23:59:59
```

### Required Permissions
The API token must have:
- `view_other_timesheet` - To see all employees' timesheets
- `view_timesheet` - To see timesheet data
- `view_user` - To see user information

### Rate Limiting
- Use reasonable `size` parameters (200-500 for daily/weekly)
- Don't query unnecessarily large date ranges
- Cache user information to avoid repeated API calls

---

## Error Handling

### Common Issues
1. **401 Unauthorized:** Check token is valid and has correct permissions
2. **Empty Results:** Verify date range and `?user=all` parameter
3. **Missing User Names:** Fall back to user ID if name lookup fails
4. **Stale Timers:** Calculate duration from start time to current time

### Validation
- Verify date ranges are valid
- Check that timesheet entries have required fields (user, begin, duration)
- Handle null end times gracefully (unclosed entries)
- Validate hour calculations (convert seconds to hours correctly)

---

## Sample Report Output

### Daily Report Example
```markdown
# Kimai Daily Report - November 13, 2025

## Executive Summary
- **Date:** November 13, 2025
- **Employees Worked:** 19
- **Total Hours:** 195.5 hours
- **Suspicious Activities:** 1 (1 employee not clocked out)

## Daily Work Summary
[Table of employees with hours and status]

## 🔴 Critical Issues
- **Elizabeth D'Amico (User 14):** Did not clock out yesterday

## ⚠️ Warnings
- None

## Active Timers
- 4 employees currently clocked in
- 1 stale timer: Elizabeth D'Amico (running 21+ hours)
```

### Weekly Report Example
```markdown
# Kimai Weekly Report - November 10-16, 2025

## Executive Summary
- **Week:** November 10-16, 2025 (Monday - Sunday)
- **Employees Worked:** 20
- **Total Hours:** 1,245.5 hours
- **Average Hours/Employee:** 62.3 hours
- **Suspicious Activities:** 2 (excessive hours, unclosed entries)

## Weekly Summary by Employee
[Table of employees with weekly totals]

## ⚠️ Warnings
- **Joshua (User 17):** 48 hours this week (high but acceptable)
- **Multiple employees:** 3+ days with > 13 hours
```

---

## Notes
- Always use the API directly with `?user=all` until MCP server bug is fixed
- Reports are saved to `/Users/ndamico/agents/reports/`
- Date format: YYYY-MM-DD for filenames
- Time format: ISO 8601 (YYYY-MM-DDTHH:MM:SS-0500) for API queries
- All times are in America/New_York timezone
- Reports include both summary and detailed breakdowns for review

