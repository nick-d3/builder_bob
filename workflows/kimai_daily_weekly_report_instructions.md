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

### 1. Use the Custom Python Tool
**IMPORTANT:** Use the custom Python script `tools/kimai_report_generator.py` to generate the daily report. This tool handles all API calls, data analysis, and report generation automatically.

Run the following command:
```bash
python3 /Users/ndamico/agents/tools/kimai_report_generator.py --daily
```

This will:
- Automatically calculate yesterday's date
- Query all employees' timesheets using the API with `?user=all` parameter
- Check for active timers and stale timers (> 24 hours)
- Analyze data for suspicious activity (over 13 hours, not clocked out, etc.)
- Generate a comprehensive markdown report
- Save the report to `reports/YYYY-MM-DD/kimai_daily_report_YYYY-MM-DD.md`

### 2. Report Structure
The generated report includes:

1. **Executive Summary**
   - Date of report
   - Total employees (worked and not clocked in)
   - Total hours worked
   - Number of suspicious activities found

2. **Daily Work Summary**
   - Table of all employees (including those who didn't clock in)
   - Columns: User ID, Name, Entries, Hours, Status
   - Sorted by hours (descending), then employees with 0 hours

3. **Critical Issues**
   - Employees who did not clock out
   - Stale active timers (> 24 hours)
   - Very long single entries (> 14 hours)

4. **Warnings**
   - Employees who worked over 13 hours
   - Very short entries (< 0.5 hours)

5. **Active Timers**
   - List of employees currently clocked in
   - Shows start time and duration running

### 3. Alternative: Specific Date
If you need to generate a report for a specific date (not yesterday), use:
```bash
python3 /Users/ndamico/agents/tools/kimai_report_generator.py --daily --date YYYY-MM-DD
```

**Note:** The tool uses the Kimai API directly with the `?user=all` parameter to bypass MCP server limitations and ensure all employees' data is retrieved.

---

## Steps to Execute - Weekly Report

### 1. Use the Custom Python Tool
**IMPORTANT:** Use the custom Python script `tools/kimai_report_generator.py` to generate the weekly report. This tool handles all API calls, data analysis, and report generation automatically.

Run the following command:
```bash
python3 /Users/ndamico/agents/tools/kimai_report_generator.py --weekly
```

This will:
- Automatically calculate the previous week (Monday to Sunday)
- Query all employees' timesheets for the week using the API with `?user=all` parameter
- Analyze weekly data for suspicious activity (excessive hours, multiple long days, etc.)
- Generate a comprehensive markdown report
- Save the report to `reports/YYYY-MM-DD/kimai_weekly_report_YYYY-MM-DD.md` (using Monday's date)

### 2. Report Structure
The generated report includes:

1. **Executive Summary**
   - Week range (Monday - Sunday)
   - Total employees (worked and not clocked in)
   - Total hours across all employees
   - Average hours per employee
   - Suspicious activities summary

2. **Weekly Summary by Employee**
   - Table with: User ID, Name, Total Hours, Days Worked, Avg Hours/Day, Days > 13h, Status
   - Sorted by total hours (descending), then employees with 0 hours

3. **Warnings**
   - Excessive weekly hours (> 60 hours)
   - Multiple days over 13 hours (3+ days)
   - High average hours/day (> 12 hours)

4. **Top Performers**
   - Employees with highest total hours

### 3. Alternative: Specific Week
If you need to generate a report for a specific week, use:
```bash
python3 /Users/ndamico/agents/tools/kimai_report_generator.py --weekly --week YYYY-MM-DD
```
(Provide Monday's date for the week)

**Note:** The tool uses the Kimai API directly with the `?user=all` parameter to bypass MCP server limitations and ensure all employees' data is retrieved.

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
- **Command:** `python3 /Users/ndamico/agents/tools/kimai_report_generator.py --daily`
- **Output:** `reports/YYYY-MM-DD/kimai_daily_report_YYYY-MM-DD.md`

### Weekly Report
- **Trigger:** Weekly (Monday morning for previous week)
- **Time:** Run Monday morning to review previous week
- **Command:** `python3 /Users/ndamico/agents/tools/kimai_report_generator.py --weekly`
- **Output:** `reports/YYYY-MM-DD/kimai_weekly_report_YYYY-MM-DD.md` (Monday's date)

### Both Reports
- **Command:** `python3 /Users/ndamico/agents/tools/kimai_report_generator.py --both`
- Generates both daily and weekly reports in one run

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

Execute this workflow by running:
```bash
# For daily report
python3 /Users/ndamico/agents/tools/kimai_report_generator.py --daily

# For weekly report
python3 /Users/ndamico/agents/tools/kimai_report_generator.py --weekly

# For both reports
python3 /Users/ndamico/agents/tools/kimai_report_generator.py --both
```

The tool will:
1. Query Kimai API for timesheet data (with `?user=all` parameter)
2. Analyze hours, clock-in/out status
3. Detect suspicious patterns
4. Generate comprehensive markdown reports
5. Highlight issues requiring attention
6. Save reports to the appropriate date folder

---

## API Usage Notes

### Tool Handles API Configuration
The `kimai_report_generator.py` tool automatically handles all API configuration:
- Uses `?user=all` parameter to see all employees' timesheets
- Includes proper authentication headers
- Handles rate limiting and pagination
- Caches user information to avoid repeated API calls

### Required Permissions
The API token configured in the tool must have:
- `view_other_timesheet` - To see all employees' timesheets
- `view_timesheet` - To see timesheet data
- `view_user` - To see user information

**Note:** The tool's token is configured in `tools/kimai_report_generator.py` and should not need modification unless the token expires.

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
- **Always use the custom Python tool** (`tools/kimai_report_generator.py`) instead of manual API calls
- The tool handles all API interactions with `?user=all` parameter automatically
- Reports are saved to `/Users/ndamico/agents/reports/YYYY-MM-DD/`
- Date format: YYYY-MM-DD for filenames
- Time format: ISO 8601 (YYYY-MM-DDTHH:MM:SS) for API queries
- All times are in America/New_York timezone
- Reports include both summary and detailed breakdowns for review
- The tool includes all employees in reports (even those who didn't clock in) for complete visibility

