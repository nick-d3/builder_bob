# Morning Playbook - D'amico Construction

AI agent and MCP server management for Nick D'Amico, owner of D'amico Construction (paving, milling, sitework).

## Quick Start

**For AI Agents:** Run `just start` - This is your entry point. It will show status and guide you to `workflows/onboarding.md` for full onboarding.

```bash
just start    # See status and get started (AI agents: read workflows/onboarding.md next)
just          # See all available commands
```

## Structure

- `justfile` - All commands (run `just` to see them)
- `workflows/` - Workflow instructions
  - `daily.md` - Main daily morning workflow (orchestrator)
  - `weekly.md` - Main weekly workflow (orchestrator)
  - `kimai/` - Timesheet reporting workflows
  - `email/` - Email analysis workflows
- `tools/` - Executable scripts
- `reports/` - Generated reports (organized by date, archived to `history/`)

## For AI Agents

### First Time Setup

1. **Start here:** Run `just start` - This shows current status and context
2. **Check status:** See what's been done today and what's pending
3. **Read workflows:** Review `workflows/daily.md` for the main morning workflow
4. **Execute:** Run `just morning` to execute all daily workflows

### Daily Workflow

When starting a new day:
1. Run `just start` to see status
2. Run `just morning` - This automatically:
   - Archives yesterday's reports to `reports/history/`
   - Generates timesheet report for yesterday
   - Reminds you to run email analysis
3. Execute email analysis workflow (see `workflows/email/daily.md`)
4. Both reports will be in `reports/YYYY-MM-DD/` (today's date folder)

### Important Notes

- **Date Logic:** Reports are saved in today's folder (e.g., `reports/2025-11-22/`) because they're generated this morning, even though timesheet data is from yesterday
- **Timesheet Report:** Automated via `just kimai-daily` - queries yesterday's data
- **Email Analysis:** Manual workflow requiring MCP tools (see `workflows/email/daily.md`)

All workflows are exposed through the justfile. Run `just` to see everything available.

## Main Workflows

- **Daily Morning:** `just morning` - Runs all daily workflows
- **Weekly:** `just weekly` - Runs weekly workflows

See `workflows/daily.md` and `workflows/weekly.md` for orchestrator details.

---

**Last Updated:** 2025-11-22
