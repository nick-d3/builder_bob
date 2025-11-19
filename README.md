# Workflow Directory

This directory contains workflow instructions for automating common tasks.

## Available Workflows

### Email Analysis Workflow
**File:** `workflow/email_analysis_instructions.md`

This workflow provides step-by-step instructions for:
- Searching and retrieving emails from Gmail
- Analyzing email content and extracting key information
- Generating a comprehensive markdown report with prioritized action items

**Usage:** When asked to check emails or create an email report, follow the instructions in `workflow/email_analysis_instructions.md` to automatically:
1. Search for recent emails
2. Retrieve full email content
3. Analyze and categorize emails
4. Generate a detailed markdown report with all necessary information

**Output:** Creates `reports/email_report.md` with:
- Executive summary
- Detailed email breakdown
- Priority action items
- Important dates calendar
- Contact directory
- Project summaries
- Recommended next steps

### Kimai Daily & Weekly Report Workflow
**File:** `workflow/kimai_daily_weekly_report_instructions.md`

This workflow provides step-by-step instructions for:
- Analyzing Kimai timesheet data for daily and weekly reports
- Detecting suspicious activity (over 13 hours, not clocked out, etc.)
- Monitoring active timers and stale entries
- Generating comprehensive markdown reports with alerts

**Usage:** When asked to generate timesheet reports or check for suspicious activity, follow the instructions in `workflow/kimai_daily_weekly_report_instructions.md` to automatically:
1. Query Kimai API for timesheet data (using `?user=all` parameter)
2. Analyze hours worked, clock-in/out status
3. Detect suspicious patterns (over 13 hours, unclosed entries, stale timers)
4. Generate detailed markdown reports with alerts

**Daily Report Output:** Creates `reports/kimai_daily_report_YYYY-MM-DD.md` with:
- Executive summary (employees worked, total hours, suspicious activities)
- Daily work summary table (all employees with hours and status)
- Suspicious activity alerts (over 13 hours, not clocked out, stale timers)
- Active timers list (currently clocked in employees)
- Detailed breakdown per employee

**Weekly Report Output:** Creates `reports/kimai_weekly_report_YYYY-MM-DD.md` with:
- Executive summary (week range, total hours, averages)
- Weekly summary by employee (total hours, days worked, averages)
- Suspicious activity alerts (excessive hours, multiple long days, unclosed entries)
- Top performers
- Project summary
- Daily breakdown table

**Suspicious Activity Detection:**
- 🔴 Critical: Not clocked out, stale timers (> 24h), very long entries (> 14h)
- ⚠️ Warning: Over 13 hours, excessive weekly hours (> 60h), multiple long days
- 🟡 Low: Very short entries, inconsistent patterns

**Note:** The workflow uses the Kimai API directly (bypassing MCP server bug) to ensure `?user=all` parameter is properly passed.

