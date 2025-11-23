# Daily Morning Workflow

**Purpose:** Main orchestrator for daily morning workflows. Executes all sub-workflows needed for Nick D'Amico's daily reports.

**Frequency:** Daily (every morning)

**Command:** `just morning`

---

## Overview

This workflow coordinates all daily morning tasks:
1. Archive yesterday's reports to history
2. Generate timesheet report (Kimai) - **automated**
3. Analyze and prioritize emails - **manual (AI agent required)**

**Important Date Logic:**
- Reports are saved in **today's date folder** (e.g., `reports/2025-11-22/`)
- Timesheet data is from **yesterday** (e.g., 2025-11-21)
- This is because reports are generated in the morning, but cover the previous day's work
- Filename includes yesterday's date: `kimai_daily_report_2025-11-21.md`

---

## Execution Flow

### 1. Archive Previous Day
Before generating new reports, archive yesterday's folder to `reports/history/` if it exists.

### 2. Timesheet Report
**Sub-workflow:** `workflows/kimai/daily.md`

**Command:** `just kimai-daily`

Generates daily timesheet report for yesterday with:
- Who worked yesterday
- Clock-in/out times (12-hour format)
- Hours worked per employee
- Suspicious activity alerts
- Active timers

**Output:** `reports/YYYY-MM-DD/kimai_daily_report_YYYY-MM-DD.md`

### 3. Email Analysis
**Sub-workflow:** `workflows/email/daily.md`

**Execution:** Manual (AI agent must execute using MCP tools)

**Quick Steps:**
1. Read `workflows/email/daily.md` for detailed instructions
2. Use MCP Google Workspace tools to:
   - Search for emails from last 24 hours
   - Retrieve email content
   - Analyze and categorize by priority
   - Extract action items, deadlines, contacts
3. Generate markdown report following the template in `workflows/email/daily.md`
4. Save to: `reports/YYYY-MM-DD/email_report.md` (today's date folder)

**What it does:**
- Categorizes by priority (High → Medium → Low)
- Extracts action items and deadlines
- Creates contact directory
- Identifies project-related emails
- Orders emails by priority (High first, then Medium, then Low)

**Output:** `reports/YYYY-MM-DD/email_report.md`

---

## Sub-Workflows

- **Kimai Daily:** `workflows/kimai/daily.md` - Automated timesheet reporting
- **Email Daily:** `workflows/email/daily.md` - Manual email analysis

---

## Quick Execution Guide

### For Automated Steps:
```bash
just morning  # Runs archive + timesheet automatically
```

### For Manual Steps (AI Agent):
1. After `just morning` completes, execute email analysis:
   - Read `workflows/email/daily.md`
   - Use MCP Google Workspace tools to search and retrieve emails
   - Analyze, categorize, and generate report
   - Save to `reports/YYYY-MM-DD/email_report.md`

## Notes

- **Date Organization:** Both reports saved in today's folder (e.g., `reports/2025-11-22/`)
- **Timesheet Data:** Covers yesterday's work (e.g., 2025-11-21)
- **Archive:** Yesterday's folder automatically moved to `reports/history/` before generating new reports
- **Timesheet Report:** Fully automated via Python script
- **Email Analysis:** Requires AI agent to execute MCP tools and generate report

---

**Last Updated:** 2025-11-22

