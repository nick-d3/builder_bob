# Weekly Workflow

**Purpose:** Main orchestrator for weekly workflows. Executes all sub-workflows needed for Nick D'Amico's weekly reports.

**Frequency:** Weekly (Monday mornings)

**Command:** `just weekly`

---

## Overview

This workflow coordinates all weekly tasks:
1. Generate weekly timesheet summary (Kimai)

Reports are saved in `reports/YYYY-MM-DD/` (Monday's date folder).

---

## Execution Flow

### 1. Weekly Timesheet Report
**Sub-workflow:** `workflows/kimai/weekly.md`

**Command:** `just kimai-weekly`

Generates weekly timesheet summary for last week (Monday-Sunday) with:
- Total hours per employee
- Days worked
- Average hours per day
- Suspicious activity patterns
- Top performers

**Output:** `reports/YYYY-MM-DD/kimai_weekly_report_YYYY-MM-DD.md` (Monday's date)

---

## Sub-Workflows

- **Kimai Weekly:** `workflows/kimai/weekly.md` - Automated weekly timesheet reporting

---

## Notes

- Weekly reports use Monday's date for the folder name
- Report covers previous week (Monday-Sunday)
- Can be run independently or as part of weekly workflow

---

**Last Updated:** 2025-11-22

