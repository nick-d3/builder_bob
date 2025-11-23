# Agent Onboarding - Start Here

Welcome! You're helping Nick D'Amico, owner of D'amico Construction (paving, milling, sitework), manage his daily morning workflows.

## What You Need to Know

**Purpose:** Generate daily reports for timesheet tracking and email analysis.

**Key Concept:** Reports are saved in **today's date folder** (e.g., `reports/2025-11-22/`) but timesheet data covers **yesterday's work** (e.g., 2025-11-21). This is because reports are generated in the morning.

## Your First Steps

1. **Check Status:** You've already run `just start` - you can see what's been done today
2. **Run Daily Workflow:** Execute `just morning` to:
   - Archive yesterday's reports
   - Generate timesheet report (automated)
   - Get reminder to run email analysis
3. **Complete Email Analysis:** Follow `workflows/email/daily.md` to analyze emails
4. **Verify:** Both reports should be in `reports/YYYY-MM-DD/` (today's folder)

## Workflow Structure

- **Main Orchestrator:** `workflows/daily.md` - Read this first for the full workflow
- **Sub-workflows:**
  - `workflows/kimai/daily.md` - Timesheet reporting (automated)
  - `workflows/email/daily.md` - Email analysis (manual, you execute)

## Commands Reference

- `just start` - See status and context (you just ran this)
- `just morning` - Run all daily workflows
- `just kimai-daily` - Generate timesheet report only
- `just status` - Check what's been done today
- `just` - See all available commands

## Important Rules

**Email Priority:**
- ALL surveys = Minimum Medium priority (regardless of sender)
- Construction/vendor emails = Minimum Medium priority (never Low)

**Date Logic:**
- Folder: Today's date (e.g., `reports/2025-11-22/`)
- Timesheet data: Yesterday (e.g., 2025-11-21)
- Filename: Includes yesterday's date (e.g., `kimai_daily_report_2025-11-21.md`)

## Next Action

Based on the status you saw, proceed with:
- If timesheet report is pending: Run `just morning` or `just kimai-daily`
- If email analysis is pending: Read `workflows/email/daily.md` and execute the workflow
- If both are done: You're all set for today!

---

**Remember:** All workflows are documented in `workflows/`. Read the orchestrator files (`daily.md`, `weekly.md`) to understand the full flow.

