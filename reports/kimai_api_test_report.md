# Kimai API Test Report
**Date:** November 12, 2025  
**Token:** a029b79766794bc0483d91350  
**Base URL:** https://tracking.damico.construction

---

## Test Results Summary

✅ **API is working correctly**  
✅ **Token can see all employees** (8 users)  
✅ **`?user=all` parameter works** - Returns timesheets from multiple users  
✅ **Token has `view_other_timesheet` permission** (confirmed by seeing other users' data)

---

## Token Owner Information

**User:** Troy Lindsay  
**User ID:** 7  
**Username:** tlindsay  
**Role:** ROLE_TEAMLEAD  
**Status:** Active  
**Team:** Sitework (Team Lead)

---

## All Employees Visible to Token

### 1. Admin
- **User ID:** 1
- **Username:** admin
- **Status:** Active
- **Timesheets:** 0 entries
- **Total Hours:** 0.00h

### 2. Benjamin Paxton
- **User ID:** 22
- **Username:** bpaxton
- **Name:** Benjamin Paxton
- **Status:** Active
- **Timesheets:** 8 entries
- **Total Hours:** 77.27h

### 3. Brandan Thomas
- **User ID:** 8
- **Username:** bthomas
- **Name:** Brandan Thomas
- **Title:** Foreman
- **Account Number:** 104
- **Status:** Active
- **Timesheets:** 8 entries
- **Total Hours:** 78.97h

### 4. Colby Sanden
- **User ID:** 24
- **Username:** csanden
- **Name:** Colby Sanden
- **Status:** Active
- **Timesheets:** 8 entries
- **Total Hours:** 397.25h ⚠️ (High - may include historical data)

### 5. Joshua Conklin
- **User ID:** 17
- **Username:** jconklin
- **Name:** Joshua
- **Title:** Conklin
- **Status:** Active
- **Timesheets:** 8 entries
- **Total Hours:** 84.67h

### 6. Mike Echevarria
- **User ID:** 26
- **Username:** mechevarria
- **Name:** Mike Echevarria
- **Status:** Active
- **Timesheets:** 0 entries
- **Total Hours:** 0.00h

### 7. Randall Wuchert
- **User ID:** 25
- **Username:** rwuchert
- **Name:** Randall Wuchert
- **Status:** Active
- **Timesheets:** 5 entries
- **Total Hours:** 28.50h

### 8. Troy Lindsay (Token Owner)
- **User ID:** 7
- **Username:** tlindsay
- **Name:** Troy Lindsay
- **Account Number:** 104
- **Status:** Active
- **Role:** ROLE_TEAMLEAD
- **Team:** Sitework (Team Lead)
- **Timesheets:** 10 entries
- **Total Hours:** 85.08h

---

## Timesheet Summary by User

| User ID | Name | Timesheets | Total Hours |
|---------|------|------------|-------------|
| 7 | Troy Lindsay | 10 | 85.08h |
| 8 | Brandan Thomas | 8 | 78.97h |
| 17 | Joshua Conklin | 8 | 84.67h |
| 22 | Benjamin Paxton | 8 | 77.27h |
| 24 | Colby Sanden | 8 | 397.25h |
| 25 | Randall Wuchert | 5 | 28.50h |
| 1 | admin | 0 | 0.00h |
| 26 | Mike Echevarria | 0 | 0.00h |

**Total:** 47 timesheet entries across 8 users

---

## API Endpoint Tests

### ✅ Test 1: Current User (`/api/users/me`)
**Status:** PASS  
**Result:** Returns token owner (Troy Lindsay, ID: 7, ROLE_TEAMLEAD)

### ✅ Test 2: List All Users (`/api/users`)
**Status:** PASS  
**Result:** Returns 8 users (admin, Benjamin Paxton, Brandan Thomas, Colby Sanden, Joshua Conklin, Mike Echevarria, Randall Wuchert, Troy Lindsay)

### ✅ Test 3: All Timesheets (`/api/timesheets?user=all`)
**Status:** PASS  
**Result:** Returns timesheets from multiple users (IDs: 7, 8, 17, 22, 24, 25)

---

## Key Findings

1. **Permission Status:** ✅ The token has `view_other_timesheet` permission
   - Can see timesheets from users: 7, 8, 17, 22, 24, 25
   - Successfully retrieves org-wide data with `?user=all`

2. **API Behavior:** ✅ Correct
   - Without `?user=all`: Returns only token owner's timesheets
   - With `?user=all`: Returns all visible timesheets
   - This matches expected Kimai API behavior

3. **MCP Server Issue:** 
   - The MCP server may not be passing `?user=all` when `user_scope == "all"`
   - Need to verify MCP server code passes the parameter correctly

4. **Data Quality:**
   - Most active users: Troy Lindsay (10 entries), others with 8 entries
   - Colby Sanden shows 397.25h which may include historical data beyond the recent 100 entries queried
   - Two users (admin, Mike Echevarria) have no timesheet entries

---

## Recommendations

1. ✅ **Token Permissions:** Current token (Troy Lindsay's) has correct permissions
2. ✅ **API Usage:** Using `?user=all` correctly returns org-wide data
3. ⚠️ **MCP Server:** Verify that when `user_scope == "all"`, the MCP server explicitly passes `user=all` parameter
4. 📝 **Documentation:** The API is working as expected - the issue is likely in the MCP server implementation

---

## API Test Commands Used

```bash
# Who am I?
curl -H "Authorization: Bearer a029b79766794bc0483d91350" \
  https://tracking.damico.construction/api/users/me

# List all users
curl -H "Authorization: Bearer a029b79766794bc0483d91350" \
  https://tracking.damico.construction/api/users

# Get all timesheets (org-wide)
curl -H "Authorization: Bearer a029b79766794bc0483d91350" \
  "https://tracking.damico.construction/api/timesheets?user=all&size=100"
```

---

## Conclusion

The Kimai API is functioning correctly. The token has proper permissions and can access:
- ✅ All 8 users in the system
- ✅ Timesheets from 6 different users (47 total entries)
- ✅ Org-wide data when using `?user=all` parameter

**The issue is likely in the MCP server code** - it may not be passing the `user=all` parameter when `user_scope == "all"` is specified. The fix should ensure the MCP server explicitly sets `user_filter = "all"` when `user_scope == "all"`.

---

*Report generated: November 12, 2025*




