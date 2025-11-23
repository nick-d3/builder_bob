# Justfile for Morning Playbook - D'amico Construction

# Default recipe - show help (runs when you type 'just' with no arguments)
default:
    @echo "Morning Playbook - D'amico Construction"
    @echo ""
    @echo "🌅 Main Workflows:"
    @echo "  just start            - Get started (status + context)"
    @echo "  just morning          - Run all daily morning workflows"
    @echo "  just weekly           - Run weekly workflows"
    @echo ""
    @echo "📊 Timesheet Reports (Kimai):"
    @echo "  just kimai-daily       - Daily report (yesterday)"
    @echo "  just kimai-weekly      - Weekly report (last week)"
    @echo "  just kimai-both        - Both daily and weekly"
    @echo "  just kimai-daily-date <DATE>  - Daily for specific date (YYYY-MM-DD)"
    @echo "  just kimai-weekly-date <DATE> - Weekly for specific week (Monday date)"
    @echo ""
    @echo "📧 Email Analysis:"
    @echo "  just email-analysis    - Email analysis (manual workflow)"
    @echo ""
    @echo "🛠️  Utilities:"
    @echo "  just status            - Check today's status"
    @echo "  just docs              - Show all source code"
    @echo ""

# Entry point for AI agents - shows status and context
start:
    @echo "🌅 Morning Playbook - D'amico Construction"
    @echo ""
    @echo "👋 Welcome! You're helping Nick D'Amico manage daily workflows."
    @echo ""
    @python3 tools/status_check.py
    @echo ""
    @echo "📖 Full onboarding: Read workflows/onboarding.md"
    @echo ""
    @echo "💡 Today's Context:"
    @python3 tools/context.py
    @echo ""
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "🎯 ACTION REQUIRED:"
    @python3 tools/action_check.py
    @echo ""
    @echo "📋 All Commands: just (to see full list)"
    @echo ""

# Check today's status (what's been done)
status:
    python3 tools/status_check.py

# Run all morning workflows
# Archives yesterday's reports, then generates today's reports
morning:
    @echo "🌅 Running morning workflows..."
    @echo ""
    @echo "1️⃣  Archiving yesterday's reports..."
    @just archive-yesterday
    @echo ""
    @echo "2️⃣  Generating timesheet report..."
    @just kimai-daily
    @echo ""
    @echo "3️⃣  Email analysis required (manual workflow)"
    @echo "   See: workflows/email/daily.md"
    @echo "   Or ask AI agent to run email analysis workflow"
    @echo ""
    @echo "✅ Morning workflow complete!"

# Archive yesterday's reports to history
archive-yesterday:
    python3 tools/archive_yesterday.py

# Weekly workflow
weekly:
    @echo "📅 Running weekly workflows..."
    @echo ""
    @just kimai-weekly
    @echo ""
    @echo "✅ Weekly workflow complete!"

# Show all source code in the repository
# Excludes reports/ directory
docs:
    python3 tools/codebase_docs.py

# Generate Kimai daily report (for yesterday)
kimai-daily:
    python3 tools/kimai_report_generator.py --daily

# Generate Kimai weekly report (for last week)
kimai-weekly:
    python3 tools/kimai_report_generator.py --weekly

# Generate both Kimai reports
kimai-both:
    python3 tools/kimai_report_generator.py --both

# Generate Kimai daily report for a specific date
# Usage: just kimai-daily-date 2025-11-21
kimai-daily-date DATE:
    python3 tools/kimai_report_generator.py --daily --date {{DATE}}

# Generate Kimai weekly report for a specific week (Monday date)
# Usage: just kimai-weekly-date 2025-11-17
kimai-weekly-date DATE:
    python3 tools/kimai_report_generator.py --weekly --week {{DATE}}

# Email analysis (manual - shows instructions)
email-analysis:
    @echo "📧 Email Analysis Workflow"
    @echo ""
    @echo "This workflow requires AI agent execution using MCP tools."
    @echo ""
    @echo "See: workflows/email/daily.md for detailed instructions"
    @echo ""
    @echo "Quick steps:"
    @echo "  1. Search Gmail for emails from last 24 hours"
    @echo "  2. Retrieve email content"
    @echo "  3. Analyze and prioritize"
    @echo "  4. Generate markdown report"
    @echo "  5. Save to reports/YYYY-MM-DD/email_report.md"
