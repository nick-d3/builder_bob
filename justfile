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
    @echo "📋 Project Reports:"
    @echo "  just run               - Generate project reports (yesterday) + PDFs"
    @echo "  just run-date <DATE>   - Project reports for specific date (YYYY-MM-DD)"
    @echo ""
    @echo "🛠️  Utilities:"
    @echo "  just status            - Check today's status"
    @echo "  just docs              - Show all source code"
    @echo "  just read-all          - Read all files (including reports)"
    @echo "  just pdf-report [DATE] - Combine all reports into single PDF"
    @echo ""

# Entry point for AI agents - shows status and context
start:
    @echo "🌅 Morning Playbook - D'amico Construction"
    @echo ""
    @echo "👋 Welcome! You're helping Nick D'Amico manage daily workflows."
    @echo ""
    @python3 tools/utils/status_check.py
    @echo ""
    @echo "📖 Full onboarding: Read workflows/onboarding.md"
    @echo ""
    @echo "💡 Today's Context:"
    @python3 tools/utils/context.py
    @echo ""
    @echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    @echo "🎯 ACTION REQUIRED:"
    @python3 tools/utils/action_check.py
    @echo ""
    @echo "📋 All Commands: just (to see full list)"
    @echo ""

# Check today's status (what's been done)
status:
    python3 tools/utils/status_check.py

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
    python3 tools/utils/archive_yesterday.py

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
    python3 tools/docs/codebase_docs.py

# Read all files in the repository (including reports)
# Usage: just read-all [--no-reports] [--output FILE]
read-all:
    python3 tools/docs/read_all_files.py

# Generate Kimai daily report (for yesterday)
kimai-daily:
    python3 tools/reporting/kimai_report_generator.py --daily

# Generate Kimai weekly report (for last week)
kimai-weekly:
    python3 tools/reporting/kimai_report_generator.py --weekly

# Generate both Kimai reports
kimai-both:
    python3 tools/reporting/kimai_report_generator.py --both

# Generate Kimai daily report for a specific date
# Usage: just kimai-daily-date 2025-11-21
kimai-daily-date DATE:
    python3 tools/reporting/kimai_report_generator.py --daily --date {{DATE}}

# Generate Kimai weekly report for a specific week (Monday date)
# Usage: just kimai-weekly-date 2025-11-17
kimai-weekly-date DATE:
    python3 tools/reporting/kimai_report_generator.py --weekly --week {{DATE}}

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

# Generate project reports workflow
# Creates markdown files for each job worked, then converts to PDFs and combines
run:
    @echo "📋 Generating project reports for yesterday..."
    @echo ""
    @echo "1️⃣  Creating project markdown reports..."
    @python3 tools/reporting/project_time_report.py
    @echo ""
    @echo "2️⃣  Converting to PDFs and combining..."
    @python3 tools/reporting/combine_project_reports_pdf.py
    @echo ""
    @echo "✅ Project reports complete!"

# Generate project reports for a specific date
# Usage: just run-date 2025-12-09
run-date DATE:
    @echo "📋 Generating project reports for {{DATE}}..."
    @echo ""
    @echo "1️⃣  Creating project markdown reports..."
    @python3 tools/reporting/project_time_report.py {{DATE}}
    @echo ""
    @echo "2️⃣  Converting to PDFs and combining..."
    @python3 tools/reporting/combine_project_reports_pdf.py {{DATE}}
    @echo ""
    @echo "✅ Project reports complete!"

# Combine all reports in a date directory into a single PDF
# Usage: just pdf-report [DATE] (defaults to today)
pdf-report DATE='':
    @PATH="/Library/TeX/texbin:/usr/local/bin:/opt/homebrew/bin:$$PATH" /usr/bin/python3 tools/reporting/combine_reports_pdf.py {{DATE}}
