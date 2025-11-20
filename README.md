# Morning Playbook - D'amico Construction

**Support Agent Instructions:** Every morning, when you read this README, you must immediately run both daily workflows to generate the morning reports for Nick D'Amico.

## Daily Morning Workflow

Upon reading this README, execute the following workflows in order:

### 1. Kimai Daily Report
**Workflow File:** `workflows/kimai_daily_weekly_report_instructions.md`

Follow the instructions to generate the daily timesheet report:
- Query Kimai API for today's timesheet data
- Analyze hours worked, clock-in/out status
- Detect suspicious activity (over 13 hours, not clocked out, stale timers)
- Generate markdown report

**Output:** `reports/YYYY-MM-DD/kimai_daily_report_YYYY-MM-DD.md`

### 2. Email Analysis Report
**Workflow File:** `workflows/email_analysis_instructions.md`

Follow the instructions to analyze and prioritize emails:
- Search for emails from the last 24 hours
- Retrieve full email content
- Analyze and categorize emails
- Generate prioritized markdown report

**Output:** `reports/YYYY-MM-DD/email_report.md`

**Important:** Both reports should be saved in the same date folder (e.g., `reports/2025-11-18/`) so everything from the same day is bundled together.

---

## Available Workflows

### Email Analysis Workflow
**File:** `workflows/email_analysis_instructions.md`

This workflow provides step-by-step instructions for:
- Searching and retrieving emails from Gmail
- Analyzing email content and extracting key information
- Generating a comprehensive markdown report with prioritized action items

**Output:** Creates `reports/YYYY-MM-DD/email_report.md` with:
- Executive summary
- Detailed email breakdown (ordered by priority: High → Medium → Low, newest first)
- Priority action items
- Important dates calendar
- Contact directory
- Project summaries
- Recommended next steps

**Priority Rules:**
- ALL surveys must be marked as at least Medium priority
- Construction/vendor emails must NEVER be marked as Low priority (minimum Medium)

### Kimai Daily & Weekly Report Workflow
**File:** `workflows/kimai_daily_weekly_report_instructions.md`

This workflow provides step-by-step instructions for:
- Analyzing Kimai timesheet data for daily and weekly reports
- Detecting suspicious activity (over 13 hours, not clocked out, etc.)
- Monitoring active timers and stale entries
- Generating comprehensive markdown reports with alerts

**Daily Report Output:** Creates `reports/YYYY-MM-DD/kimai_daily_report_YYYY-MM-DD.md` with:
- Executive summary (employees worked, total hours, suspicious activities)
- Daily work summary table (all employees with hours and status)
- Suspicious activity alerts (over 13 hours, not clocked out, stale timers)
- Active timers list (currently clocked in employees)
- Detailed breakdown per employee

**Weekly Report Output:** Creates `reports/YYYY-MM-DD/kimai_weekly_report_YYYY-MM-DD.md` with:
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

## Tools

**File:** `tools/kimai_report_generator.py`

Python script for generating Kimai reports:
- Daily reports: `python3 tools/kimai_report_generator.py --daily`
- Weekly reports: `python3 tools/kimai_report_generator.py --weekly`
- Both: `python3 tools/kimai_report_generator.py --both`
