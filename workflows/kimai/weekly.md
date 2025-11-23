# Kimai Weekly Report Workflow

## Purpose
Automates the process of analyzing Kimai timesheet data to generate weekly reports with alerts for suspicious or out-of-norm activity patterns.

## Key Features
- **Weekly Log:** Summary of the week's work across all employees
- **Suspicious Activity Alerts:** Flags for excessive hours, multiple long days, unclosed entries
- **Top Performers:** Employees with highest total hours
- **Pattern Detection:** Identifies trends across the week

## API Configuration
- **Base URL:** `https://tracking.damico.construction`
- **Token:** Admin token with `view_other_timesheet` permission
- **Critical Parameter:** Always use `?user=all` to see all employees' timesheets

## Steps to Execute

### 1. Use the Custom Python Tool
**IMPORTANT:** Use the custom Python script `tools/reporting/kimai_report_generator.py` to generate the weekly report. This tool handles all API calls, data analysis, and report generation automatically.

**Command:**
```bash
just kimai-weekly
# Or directly:
python3 tools/reporting/kimai_report_generator.py --weekly
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
just kimai-weekly-date 2025-11-17
# Or directly:
python3 tools/reporting/kimai_report_generator.py --weekly --week 2025-11-17
```
(Provide Monday's date for the week)

**Note:** The tool uses the Kimai API directly with the `?user=all` parameter to bypass MCP server limitations and ensure all employees' data is retrieved.

---

## Suspicious Activity Thresholds

### Weekly Thresholds
- **Total Hours > 60:** ⚠️ Warning - Excessive weekly hours
- **3+ Days Over 13 Hours:** ⚠️ Warning - Pattern of long days
- **Average Hours/Day > 12:** ⚠️ Warning - Consistently high hours
- **2+ Unclosed Entries:** 🔴 Critical - Multiple clock-out issues
- **Days Worked < 3 (if expected 5):** 🟡 Low - May indicate absence

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
- Include horizontal rules (---) between major sections

### Status Indicators
- **✅ OK:** Normal weekly hours and patterns
- **⚠️ WARNING:** Excessive hours or multiple long days
- **🔴 CRITICAL:** Multiple unclosed entries or severe patterns

---

## Error Handling

### Common Issues
1. **401 Unauthorized:** Check token is valid and has correct permissions
2. **Empty Results:** Verify date range and `?user=all` parameter
3. **Missing User Names:** Fall back to user ID if name lookup fails

### Validation
- Verify week date range is valid (Monday to Sunday)
- Check that timesheet entries have required fields
- Handle null end times gracefully (unclosed entries)
- Validate hour calculations correctly

---

## Notes
- **Always use the custom Python tool** (`tools/kimai_report_generator.py`) instead of manual API calls
- The tool handles all API interactions with `?user=all` parameter automatically
- Reports are saved to `reports/YYYY-MM-DD/` (Monday's date folder)
- Date format: YYYY-MM-DD for filenames
- Time format: ISO 8601 (YYYY-MM-DDTHH:MM:SS) for API queries
- All times are in America/New_York timezone
- Reports include both summary and detailed breakdowns for review
- The tool includes all employees in reports (even those who didn't clock in) for complete visibility

---

**Last Updated:** 2025-11-22

