# Kimai Daily Report Workflow

## Purpose
Automates the process of analyzing Kimai timesheet data to generate daily reports with alerts for suspicious or out-of-norm activity.

## Key Features
- **Daily Log:** Who worked yesterday, hours worked, clock-in/out status
- **Suspicious Activity Alerts:** Flags for unusual patterns (over 13 hours, not clocked out, etc.)
- **Active Timer Monitoring:** Tracks employees currently clocked in
- **Clock-In/Out Times:** Displays times in 12-hour format (AM/PM)

## API Configuration
- **Base URL:** `https://tracking.damico.construction`
- **Token:** Admin token with `view_other_timesheet` permission
- **Critical Parameter:** Always use `?user=all` to see all employees' timesheets

## Steps to Execute

### 1. Use the Custom Python Tool
**IMPORTANT:** Use the custom Python script `tools/reporting/kimai_report_generator.py` to generate the daily report. This tool handles all API calls, data analysis, and report generation automatically.

**Command:**
```bash
just kimai-daily
# Or directly:
python3 tools/reporting/kimai_report_generator.py --daily
```

This will:
- Automatically calculate yesterday's date
- Query all employees' timesheets using the API with `?user=all` parameter
- Check for active timers and stale timers (> 24 hours)
- Analyze data for suspicious activity (over 13 hours, not clocked out, etc.)
- Generate a comprehensive markdown report
- Save the report to `reports/YYYY-MM-DD/kimai_daily_report_YYYY-MM-DD.md` (today's date folder)

### 2. Report Structure
The generated report includes:

1. **Executive Summary**
   - Date of report
   - Total employees (worked and not clocked in)
   - Total hours worked
   - Number of suspicious activities found

2. **Daily Work Summary**
   - Table of all employees (including those who didn't clock in)
   - Columns: User ID, Name, Entries, Hours, Clock In, Clock Out, Status
   - Sorted by hours (descending), then employees with 0 hours

3. **Detailed Clock-In/Out Times**
   - All clock-in/out entries per employee
   - Times displayed in 12-hour format (AM/PM)

4. **Critical Issues**
   - Employees who did not clock out
   - Stale active timers (> 24 hours)
   - Very long single entries (> 14 hours)

5. **Warnings**
   - Employees who worked over 13 hours
   - Very short entries (< 0.5 hours)

6. **Active Timers**
   - List of employees currently clocked in
   - Shows start time and duration running

### 3. Alternative: Specific Date
If you need to generate a report for a specific date (not yesterday), use:
```bash
just kimai-daily-date 2025-11-21
# Or directly:
python3 tools/reporting/kimai_report_generator.py --daily --date 2025-11-21
```

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

---

## User ID to Name Mapping

The tool fetches user information dynamically from `/api/users` endpoint, with fallback to static mapping if needed.

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

## Notes
- **Always use the custom Python tool** (`tools/kimai_report_generator.py`) instead of manual API calls
- The tool handles all API interactions with `?user=all` parameter automatically
- Reports are saved to `reports/YYYY-MM-DD/` (today's date folder)
- Date format: YYYY-MM-DD for filenames
- Time format: ISO 8601 (YYYY-MM-DDTHH:MM:SS) for API queries
- All times are in America/New_York timezone
- Clock-in/out times are displayed in 12-hour format (AM/PM)
- Reports include both summary and detailed breakdowns for review
- The tool includes all employees in reports (even those who didn't clock in) for complete visibility

---

**Last Updated:** 2025-11-22

