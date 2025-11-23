# Email Analysis Workflow

## Purpose
Automates the process of analyzing emails from Nick D'Amico's Gmail account and generating a comprehensive markdown report with prioritized action items.

## Frequency
Daily (part of morning workflow)

## Quick Reference for AI Agents

**When to run:** After `just morning` completes (or as part of daily workflow)

**Key Information:**
- Email: `bdamico@damicoconstruction.net`
- Time range: Last 24 hours
- Output: `reports/YYYY-MM-DD/email_report.md` (today's date folder)
- Priority order: High → Medium → Low (within each priority, newest first)

**Critical Priority Rules:**
1. **ALL surveys** = Minimum Medium priority (regardless of sender)
2. **Construction/vendor emails** = Minimum Medium priority (never Low)

## Steps to Execute

### 1. Search for Recent Emails
Use the Gmail search function to find emails from the last 24 hours:

```
mcp_google_workspace_search_gmail_messages(
    query: "in:inbox newer_than:1d",
    user_google_email: "bdamico@damicoconstruction.net",
    page_size: 20
)
```

### 2. Retrieve Email Content
After obtaining message IDs from the search, retrieve the full content of all emails:

```
mcp_google_workspace_get_gmail_messages_content_batch(
    message_ids: [list of message IDs],
    user_google_email: "bdamico@damicoconstruction.net",
    format: "full"
)
```

**Note:** If the output is too large and written to a file, read the file in chunks to extract information.

### 3. Analyze Email Content
For each email, extract and document:
- **From:** Sender name and email address
- **To:** Recipient(s)
- **Subject:** Email subject line
- **Date:** Email date and time
- **Message ID:** For reference
- **Content:** Full email body (convert HTML to readable text)
- **Attachments:** List any attachments with file names and sizes
- **Action Required:** Determine what action is needed
- **Priority:** Categorize as High, Medium, or Low priority

### 4. Categorize Emails
Organize emails into categories:
- **Business/Project Related** - Requires action or response
- **Bid Opportunities** - Construction bids with deadlines
- **Marketing/Promotional** - Can be archived or deleted
- **Personal** - Personal items (tickets, etc.)
- **Newsletters** - Informational only

**IMPORTANT PRIORITY RULES:**
- **Surveys:** ALL surveys (from any sender) must be marked as at least Medium priority. Nick D'Amico wants to see all surveys regardless of source.
- **Construction Companies & Vendors:** Any email from construction companies, vendors, suppliers, or industry partners containing information or updates must NEVER be marked as Low priority. These should be at least Medium priority, even if they appear informational.

### 5. Identify Priority Items
Flag high-priority items that require immediate attention:
- Emails with deadlines
- Project estimates/quotes needed
- Bid opportunities with submission deadlines
- Follow-ups requiring response
- **ALL surveys** (minimum Medium priority)
- **Construction company/vendor updates** (minimum Medium priority)

### 6. Extract Key Information
For each email, extract:
- **Deadlines:** Any dates or times mentioned
- **Contact Information:** Names, phone numbers, email addresses
- **Project Details:** Project names, locations, scope of work
- **Financial Terms:** Retainage, payment terms, pricing
- **Action Items:** Specific tasks required

### 7. Create Markdown Report
Generate a comprehensive markdown report (`email_report.md`) with the following sections:

**IMPORTANT: Email Ordering**
- Emails in the "Detailed Email Breakdown" section must be ordered by priority: High priority first, then Medium priority, then Low priority
- Within each priority level, order by date (newest first)
- This ensures the most important emails are seen first

#### Report Structure:
1. **Executive Summary**
   - Total number of emails
   - Priority actions required
   - Key deadlines

2. **Detailed Email Breakdown**
   - **Order emails by priority:** High priority first, then Medium priority, then Low priority
   - Within each priority level, order by date (newest first)
   - For each email, include:
     - From/To/Date/Subject
     - Full content summary
     - Attachments (if any)
     - Action required
     - Contact information

3. **Priority Action Items**
   - High Priority (immediate action)
   - Medium Priority
   - Low Priority / Informational

4. **Important Dates Calendar**
   - Table format with dates, times, events, and priorities

5. **Contact Directory**
   - All business contacts with:
     - Name and title
     - Company
     - Phone numbers
     - Email addresses
     - Project/context

6. **Project Summaries**
   - Detailed summaries of active projects
   - Scope of work
   - Timeline and deadlines
   - Key contacts

7. **Recommended Next Steps**
   - Immediate actions (today)
   - This week
   - Next week
   - Ongoing

### 8. Report Formatting Guidelines
- Use markdown headers (##, ###) for sections
- Use emoji indicators for priorities (🔴 High, 🟡 Medium, 🟢 Low)
- Include tables for dates and contacts
- Use code blocks for email addresses and URLs
- Bold important information (deadlines, amounts, etc.)
- Include horizontal rules (---) between major sections

### 9. Special Handling
- **Emails with attachments:** Note the attachment and suggest reviewing it
- **Threaded conversations:** Include full conversation context
- **Forwarded emails:** Note the original sender and forwarder
- **HTML emails:** Convert to readable text format
- **Large email batches:** Process in chunks if needed
- **Surveys:** Always mark as Medium or High priority, regardless of sender. Nick D'Amico wants visibility into all surveys.
- **Construction/Vendor Updates:** Any informational emails from construction companies, vendors, suppliers, material providers, or industry partners (e.g., Tilcon, Galasso, O&G Industries, equipment dealers, etc.) should be marked as Medium priority minimum, even if they appear to be routine updates or schedules.

### 10. Save Report
Save the completed report inside **today's** date folder (not yesterday's):

```python
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
report_path = f"reports/{today}/email_report.md"
```

**Important:** Use today's date for the folder (same as timesheet report), even though you're analyzing emails from the last 24 hours. This keeps all of today's reports together.

---

## Priority Rules

### 🔴 High Priority
- Deadlines (quotes, bids, responses needed)
- Project estimates/quotes needed
- Bid opportunities with submission deadlines
- Follow-ups requiring immediate response

### 🟡 Medium Priority
- **ALL surveys** (regardless of sender)
- Construction/vendor updates (schedules, plant closings, etc.)
- Business emails requiring action
- Industry partner communications

### 🟢 Low Priority
- Marketing/promotional emails
- Newsletters
- Personal items
- Informational only (non-construction related)

**Critical Rules:**
1. **Surveys:** ALL surveys must be marked as at least Medium priority, regardless of sender
2. **Construction Companies & Vendors:** Any email from construction companies, vendors, suppliers, material providers, equipment dealers, or industry partners must NEVER be marked as Low priority (minimum Medium)

---

## Key Email Address
- Primary: `bdamico@damicoconstruction.net`
- Alternative: `bill@damico.construction` (may receive some emails)

---

## Notes
- Always check for emails from the last 24 hours by default
- If user specifies a different time period, adjust the search query accordingly
- Pay special attention to construction-related emails, bid opportunities, and project estimates
- Extract all deadlines and contact information for easy reference
- Categorize marketing emails separately to reduce clutter in priority sections
- Reports are saved to `reports/YYYY-MM-DD/` (today's date folder)

---

**Last Updated:** 2025-11-22

