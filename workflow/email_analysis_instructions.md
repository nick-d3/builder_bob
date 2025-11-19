# Email Analysis Workflow Instructions

## Purpose
This workflow automates the process of analyzing emails from the user's Gmail account and generating a comprehensive markdown report.

## Steps to Execute

### 1. Search for Recent Emails
Use the Gmail search function to find emails from the last 24 hours (or specified time period):

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

### 5. Identify Priority Items
Flag high-priority items that require immediate attention:
- Emails with deadlines
- Project estimates/quotes needed
- Bid opportunities with submission deadlines
- Follow-ups requiring response

### 6. Extract Key Information
For each email, extract:
- **Deadlines:** Any dates or times mentioned
- **Contact Information:** Names, phone numbers, email addresses
- **Project Details:** Project names, locations, scope of work
- **Financial Terms:** Retainage, payment terms, pricing
- **Action Items:** Specific tasks required

### 7. Create Markdown Report
Generate a comprehensive markdown report (`email_report.md`) with the following sections:

#### Report Structure:
1. **Executive Summary**
   - Total number of emails
   - Priority actions required
   - Key deadlines

2. **Detailed Email Breakdown**
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

### 10. Save Report
Save the completed report as:
```
/Users/ndamico/agents/reports/email_report.md
```

## Example Query to Trigger This Workflow

When the user asks to:
- "Check my emails"
- "What emails do I have?"
- "Review my inbox"
- "Create an email report"
- "Analyze my emails"

Execute this workflow to:
1. Search for recent emails
2. Retrieve and analyze content
3. Generate comprehensive markdown report
4. Present findings with prioritized action items

## Key Email Address
- Primary: `bdamico@damicoconstruction.net`
- Alternative: `bill@damico.construction` (may receive some emails)

## Notes
- Always check for emails from the last 24 hours by default
- If user specifies a different time period, adjust the search query accordingly
- Pay special attention to construction-related emails, bid opportunities, and project estimates
- Extract all deadlines and contact information for easy reference
- Categorize marketing emails separately to reduce clutter in priority sections

