#!/usr/bin/env python3
"""
Kimai Daily & Weekly Report Generator

This script generates daily and weekly timesheet reports from Kimai
with automatic detection of suspicious activity.

Usage:
    python kimai_report_generator.py --daily    # Generate daily report
    python kimai_report_generator.py --weekly    # Generate weekly report
    python kimai_report_generator.py --both      # Generate both reports
"""

import json
import sys
import argparse
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

# Configuration
KIMAI_URL = "https://tracking.damico.construction"
KIMAI_TOKEN = "5f3d0820c5af4456937441752"  # Admin token with view_other_timesheet permission
REPORTS_DIR = Path("/Users/ndamico/agents/reports")

# User ID to name mapping (can be fetched dynamically)
USER_MAP = {
    1: "admin", 2: "Nick D'Amico", 3: "Lori Holcomb", 4: "nbendas", 5: "John Burke",
    6: "Bill D'Amico", 7: "Troy Lindsay", 8: "Brandan Thomas", 9: "Carl Robinson",
    10: "Joe Loveall", 11: "Nate Loveall", 12: "Ben Olmo", 13: "Danny Lozada",
    14: "Elizabeth D'Amico", 15: "Alex Anglace", 16: "Stephen Calway", 17: "Joshua",
    18: "Timothy Genovese", 19: "Steven Hechevarria", 20: "Christopher Johnson",
    21: "Oscar Morales", 22: "Benjamin Paxton", 23: "Bill Rivera", 24: "Colby Sanden",
    25: "Randall Wuchert", 26: "Mike Echevarria"
}


def get_users():
    """Fetch user information from Kimai API"""
    url = f"{KIMAI_URL}/api/users"
    headers = {
        "Authorization": f"Bearer {KIMAI_TOKEN}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        users = response.json()
        user_map = {}
        for user in users:
            user_map[user['id']] = user.get('alias') or user.get('username', f"User {user['id']}")
        return user_map
    except Exception as e:
        print(f"Warning: Could not fetch users, using static map: {e}")
        return USER_MAP


def get_timesheets(begin, end, active=False):
    """Fetch timesheets from Kimai API"""
    url = f"{KIMAI_URL}/api/timesheets"
    headers = {
        "Authorization": f"Bearer {KIMAI_TOKEN}",
        "Accept": "application/json"
    }
    params = {
        "user": "all",  # Critical: must include this to see all employees
        "begin": begin,
        "end": end,
        "size": 500
    }
    if active:
        params["active"] = 1
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching timesheets: {e}")
        return []


def analyze_daily(timesheets, user_map):
    """Analyze daily timesheet data - includes all employees even if they didn't clock in"""
    by_user = defaultdict(list)
    for entry in timesheets:
        by_user[entry['user']].append(entry)
    
    results = []
    suspicious = {
        'over_13h': [],
        'not_clocked_out': [],
        'very_long_entry': [],
        'very_short_entry': []
    }
    
    # Process employees who have timesheet entries
    for user_id, entries in by_user.items():
        name = user_map.get(user_id, f"User {user_id}")
        total_seconds = sum(e.get('duration', 0) for e in entries)
        total_hours = round(total_seconds / 3600, 2)
        
        unclosed = [e for e in entries if e.get('end') is None]
        
        # Check for very long single entry
        for e in entries:
            if e.get('duration', 0) > 14 * 3600:  # > 14 hours
                suspicious['very_long_entry'].append({
                    'user_id': user_id,
                    'name': name,
                    'hours': round(e.get('duration', 0) / 3600, 2),
                    'entry_id': e.get('id')
                })
        
        # Check for very short entries
        for e in entries:
            if 0 < e.get('duration', 0) < 0.5 * 3600:  # < 0.5 hours
                suspicious['very_short_entry'].append({
                    'user_id': user_id,
                    'name': name,
                    'hours': round(e.get('duration', 0) / 3600, 2),
                    'entry_id': e.get('id')
                })
        
        if total_hours > 13:
            suspicious['over_13h'].append({
                'user_id': user_id,
                'name': name,
                'hours': total_hours
            })
        
        if unclosed:
            suspicious['not_clocked_out'].append({
                'user_id': user_id,
                'name': name,
                'count': len(unclosed)
            })
        
        results.append({
            'user_id': user_id,
            'name': name,
            'entries': len(entries),
            'hours': total_hours,
            'unclosed': len(unclosed),
            'over_13h': total_hours > 13,
            'entries_detail': entries
        })
    
    # Add employees who didn't clock in (0 hours)
    for user_id, name in user_map.items():
        if user_id not in by_user:
            results.append({
                'user_id': user_id,
                'name': name,
                'entries': 0,
                'hours': 0.0,
                'unclosed': 0,
                'over_13h': False,
                'entries_detail': []
            })
    
    # Sort: employees with hours first (descending), then employees with 0 hours (by user ID)
    results.sort(key=lambda x: (x['hours'] == 0, -x['hours'], x['user_id']))
    return results, suspicious


def analyze_weekly(timesheets, user_map):
    """Analyze weekly timesheet data - includes all employees even if they didn't clock in"""
    by_user = defaultdict(list)
    for entry in timesheets:
        by_user[entry['user']].append(entry)
    
    results = []
    suspicious = {
        'excessive_hours': [],
        'multiple_long_days': [],
        'multiple_unclosed': [],
        'high_average': []
    }
    
    # Process employees who have timesheet entries
    for user_id, entries in by_user.items():
        name = user_map.get(user_id, f"User {user_id}")
        total_seconds = sum(e.get('duration', 0) for e in entries)
        total_hours = round(total_seconds / 3600, 2)
        
        # Count unique days
        days = set()
        days_over_13h = 0
        unclosed_count = 0
        
        # Group by day
        by_day = defaultdict(list)
        for e in entries:
            if e.get('begin'):
                date_str = e['begin'].split('T')[0]
                days.add(date_str)
                by_day[date_str].append(e)
                if e.get('end') is None:
                    unclosed_count += 1
        
        # Check each day for > 13 hours
        for day, day_entries in by_day.items():
            day_seconds = sum(e.get('duration', 0) for e in day_entries)
            day_hours = day_seconds / 3600
            if day_hours > 13:
                days_over_13h += 1
        
        days_worked = len(days)
        avg_hours = round(total_hours / days_worked, 2) if days_worked > 0 else 0
        
        # Check suspicious patterns
        if total_hours > 60:
            suspicious['excessive_hours'].append({
                'user_id': user_id,
                'name': name,
                'hours': total_hours
            })
        
        if days_over_13h >= 3:
            suspicious['multiple_long_days'].append({
                'user_id': user_id,
                'name': name,
                'days': days_over_13h
            })
        
        if unclosed_count >= 2:
            suspicious['multiple_unclosed'].append({
                'user_id': user_id,
                'name': name,
                'count': unclosed_count
            })
        
        if avg_hours > 12:
            suspicious['high_average'].append({
                'user_id': user_id,
                'name': name,
                'avg_hours': avg_hours
            })
        
        results.append({
            'user_id': user_id,
            'name': name,
            'total_hours': total_hours,
            'days_worked': days_worked,
            'avg_hours': avg_hours,
            'days_over_13h': days_over_13h,
            'unclosed_count': unclosed_count,
            'entries': entries
        })
    
    # Add employees who didn't clock in (0 hours)
    for user_id, name in user_map.items():
        if user_id not in by_user:
            results.append({
                'user_id': user_id,
                'name': name,
                'total_hours': 0.0,
                'days_worked': 0,
                'avg_hours': 0.0,
                'days_over_13h': 0,
                'unclosed_count': 0,
                'entries': []
            })
    
    # Sort: employees with hours first (descending), then employees with 0 hours (by user ID)
    results.sort(key=lambda x: (x['total_hours'] == 0, -x['total_hours'], x['user_id']))
    return results, suspicious


def check_active_timers(user_map):
    """Check for active timers"""
    timers = get_timesheets("", "", active=True)
    active = []
    stale = []
    
    for timer in timers:
        user_id = timer['user']
        name = user_map.get(user_id, f"User {user_id}")
        begin = timer.get('begin')
        
        if begin:
            try:
                start_time = datetime.fromisoformat(begin.replace('Z', '+00:00').replace('-0500', '-05:00'))
                now = datetime.now(start_time.tzinfo)
                duration = now - start_time
                hours_running = round(duration.total_seconds() / 3600, 1)
                
                timer_info = {
                    'user_id': user_id,
                    'name': name,
                    'start_time': begin,
                    'hours_running': hours_running,
                    'entry_id': timer.get('id')
                }
                
                if hours_running > 24:
                    stale.append(timer_info)
                else:
                    active.append(timer_info)
            except Exception as e:
                active.append({
                    'user_id': user_id,
                    'name': name,
                    'start_time': begin,
                    'error': str(e)
                })
    
    return active, stale


def generate_daily_report(date_str):
    """Generate daily report for a specific date"""
    user_map = get_users()
    begin = f"{date_str}T00:00:00"
    end = f"{date_str}T23:59:59"
    
    timesheets = get_timesheets(begin, end)
    active_timers, stale_timers = check_active_timers(user_map)
    
    results, suspicious = analyze_daily(timesheets, user_map)
    
    # Generate markdown report
    report = f"""# Kimai Daily Report - {date_str}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

- **Date:** {date_str}
- **Total Employees:** {len(results)}
- **Employees Worked:** {len([r for r in results if r['hours'] > 0])}
- **Employees Not Clocked In:** {len([r for r in results if r['hours'] == 0])}
- **Total Hours:** {sum(r['hours'] for r in results):.2f} hours
- **Suspicious Activities:** {len(suspicious['over_13h']) + len(suspicious['not_clocked_out']) + len(stale_timers)}

---

## Daily Work Summary

| User ID | Name | Entries | Hours | Status |
|---------|------|---------|-------|--------|
"""
    
    for r in results:
        status = []
        if r['unclosed'] > 0:
            status.append(f"⚠️ {r['unclosed']} NOT CLOCKED OUT")
        if r['over_13h']:
            status.append("🔴 OVER 13 HOURS")
        status_str = " | ".join(status) if status else ("✅ OK" if r['hours'] > 0 else "⚪ No Entry")
        report += f"| {r['user_id']} | {r['name']} | {r['entries']} | {r['hours']}h | {status_str} |\n"
    
    report += "\n---\n\n## 🔴 Critical Issues\n\n"
    
    if suspicious['not_clocked_out']:
        report += "### Employees Who Did Not Clock Out\n\n"
        for item in suspicious['not_clocked_out']:
            report += f"- **{item['name']}** (User {item['user_id']}): {item['count']} unclosed entr{'y' if item['count'] == 1 else 'ies'}\n"
        report += "\n"
    
    if stale_timers:
        report += "### Stale Active Timers (> 24 hours)\n\n"
        for timer in stale_timers:
            report += f"- **{timer['name']}** (User {timer['user_id']}): Running for {timer['hours_running']} hours (started {timer['start_time']})\n"
        report += "\n"
    
    if suspicious['very_long_entry']:
        report += "### Very Long Single Entries (> 14 hours)\n\n"
        for item in suspicious['very_long_entry']:
            report += f"- **{item['name']}** (User {item['user_id']}): {item['hours']} hours (Entry ID: {item['entry_id']})\n"
        report += "\n"
    
    if not suspicious['not_clocked_out'] and not stale_timers and not suspicious['very_long_entry']:
        report += "✅ No critical issues found.\n\n"
    
    report += "---\n\n## ⚠️ Warnings\n\n"
    
    if suspicious['over_13h']:
        report += "### Employees Who Worked Over 13 Hours\n\n"
        for item in suspicious['over_13h']:
            report += f"- **{item['name']}** (User {item['user_id']}): {item['hours']} hours\n"
        report += "\n"
    
    if suspicious['very_short_entry']:
        report += "### Very Short Entries (< 0.5 hours)\n\n"
        for item in suspicious['very_short_entry']:
            report += f"- **{item['name']}** (User {item['user_id']}): {item['hours']} hours (Entry ID: {item['entry_id']})\n"
        report += "\n"
    
    if not suspicious['over_13h'] and not suspicious['very_short_entry']:
        report += "✅ No warnings.\n\n"
    
    report += "---\n\n## Active Timers\n\n"
    
    if active_timers:
        report += f"**Currently Clocked In:** {len(active_timers)} employees\n\n"
        report += "| Name | User ID | Started | Running For |\n"
        report += "|------|---------|--------|-------------|\n"
        for timer in active_timers:
            report += f"| {timer['name']} | {timer['user_id']} | {timer['start_time']} | {timer.get('hours_running', 'N/A')}h |\n"
    else:
        report += "✅ No active timers - everyone is clocked out.\n"
    
    # Save report
    report_file = REPORTS_DIR / f"kimai_daily_report_{date_str}.md"
    report_file.write_text(report)
    print(f"✅ Daily report saved to: {report_file}")
    
    return report_file


def generate_weekly_report(monday_date):
    """Generate weekly report for a week starting on Monday"""
    user_map = get_users()
    monday = datetime.strptime(monday_date, '%Y-%m-%d')
    sunday = monday + timedelta(days=6)
    
    begin = f"{monday_date}T00:00:00"
    end = f"{sunday.strftime('%Y-%m-%d')}T23:59:59"
    
    timesheets = get_timesheets(begin, end)
    results, suspicious = analyze_weekly(timesheets, user_map)
    
    # Generate markdown report
    report = f"""# Kimai Weekly Report - {monday_date} to {sunday.strftime('%Y-%m-%d')}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Week:** {monday.strftime('%A, %B %d')} - {sunday.strftime('%A, %B %d, %Y')}

---

## Executive Summary

- **Week Range:** {monday_date} to {sunday.strftime('%Y-%m-%d')}
- **Total Employees:** {len(results)}
- **Employees Worked:** {len([r for r in results if r['total_hours'] > 0])}
- **Employees Not Clocked In:** {len([r for r in results if r['total_hours'] == 0])}
- **Total Hours:** {sum(r['total_hours'] for r in results):.2f} hours
- **Average Hours/Employee (Worked):** {sum(r['total_hours'] for r in results) / len([r for r in results if r['total_hours'] > 0]) if len([r for r in results if r['total_hours'] > 0]) > 0 else 0:.2f} hours
- **Suspicious Activities:** {len(suspicious['excessive_hours']) + len(suspicious['multiple_long_days']) + len(suspicious['multiple_unclosed'])}

---

## Weekly Summary by Employee

| User ID | Name | Total Hours | Days Worked | Avg Hours/Day | Days > 13h | Status |
|---------|------|-------------|-------------|---------------|------------|--------|
"""
    
    for r in results:
        status = []
        if r['total_hours'] > 60:
            status.append("⚠️ Excessive")
        if r['days_over_13h'] >= 3:
            status.append("⚠️ Multiple Long Days")
        if r['unclosed_count'] >= 2:
            status.append("🔴 Multiple Unclosed")
        status_str = " | ".join(status) if status else ("✅ OK" if r['total_hours'] > 0 else "⚪ No Entry")
        
        report += f"| {r['user_id']} | {r['name']} | {r['total_hours']}h | {r['days_worked']} | {r['avg_hours']}h | {r['days_over_13h']} | {status_str} |\n"
    
    report += "\n---\n\n## ⚠️ Warnings\n\n"
    
    if suspicious['excessive_hours']:
        report += "### Excessive Weekly Hours (> 60 hours)\n\n"
        for item in suspicious['excessive_hours']:
            report += f"- **{item['name']}** (User {item['user_id']}): {item['hours']} hours\n"
        report += "\n"
    
    if suspicious['multiple_long_days']:
        report += "### Multiple Days Over 13 Hours (3+ days)\n\n"
        for item in suspicious['multiple_long_days']:
            report += f"- **{item['name']}** (User {item['user_id']}): {item['days']} days\n"
        report += "\n"
    
    if suspicious['high_average']:
        report += "### High Average Hours/Day (> 12 hours)\n\n"
        for item in suspicious['high_average']:
            report += f"- **{item['name']}** (User {item['user_id']}): {item['avg_hours']} hours/day\n"
        report += "\n"
    
    if not any(suspicious.values()):
        report += "✅ No warnings.\n\n"
    
    report += "---\n\n## Top Performers\n\n"
    
    if results:
        top_hours = sorted(results, key=lambda x: x['total_hours'], reverse=True)[:5]
        report += "### Highest Total Hours\n\n"
        for r in top_hours:
            report += f"- **{r['name']}** (User {r['user_id']}): {r['total_hours']} hours\n"
        report += "\n"
    
    # Save report
    report_file = REPORTS_DIR / f"kimai_weekly_report_{monday_date}.md"
    report_file.write_text(report)
    print(f"✅ Weekly report saved to: {report_file}")
    
    return report_file


def main():
    parser = argparse.ArgumentParser(description='Generate Kimai daily and weekly reports')
    parser.add_argument('--daily', action='store_true', help='Generate daily report for yesterday')
    parser.add_argument('--weekly', action='store_true', help='Generate weekly report for last week')
    parser.add_argument('--both', action='store_true', help='Generate both daily and weekly reports')
    parser.add_argument('--date', type=str, help='Specific date for daily report (YYYY-MM-DD)')
    parser.add_argument('--week', type=str, help='Monday date for weekly report (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    if not (args.daily or args.weekly or args.both):
        parser.print_help()
        sys.exit(1)
    
    if args.daily or args.both:
        if args.date:
            date_str = args.date
        else:
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime('%Y-%m-%d')
        generate_daily_report(date_str)
    
    if args.weekly or args.both:
        if args.week:
            monday_date = args.week
        else:
            today = datetime.now()
            # Get Monday of last week
            days_since_monday = today.weekday()
            last_monday = today - timedelta(days=days_since_monday + 7)
            monday_date = last_monday.strftime('%Y-%m-%d')
        generate_weekly_report(monday_date)


if __name__ == '__main__':
    main()

