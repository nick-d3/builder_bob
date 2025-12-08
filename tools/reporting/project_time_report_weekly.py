#!/usr/bin/env python3
"""
Weekly Project-Based Time Report Generator

Groups timesheet entries by project/job for a full week and shows:
- Employee time on each project across the week
- Daily breakdowns
- Descriptions from time logs (machine hours, work completed, etc.)
"""

import requests
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import re

# Configuration
KIMAI_URL = "https://tracking.damico.construction"
KIMAI_TOKEN = "828f0382d52e29b0ddfbc49fb"
REPORTS_DIR = Path("/Users/ndamico/Agent/builder/reports")

# User ID to name mapping
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


def get_projects():
    """Fetch all projects from Kimai API"""
    url = f"{KIMAI_URL}/api/projects"
    headers = {
        "Authorization": f"Bearer {KIMAI_TOKEN}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        projects = response.json()
        return {p['id']: p for p in projects}
    except Exception as e:
        print(f"Error fetching projects: {e}")
        return {}


def get_activities():
    """Fetch all activities from Kimai API"""
    url = f"{KIMAI_URL}/api/activities"
    headers = {
        "Authorization": f"Bearer {KIMAI_TOKEN}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        activities = response.json()
        return {a['id']: a for a in activities}
    except Exception as e:
        print(f"Error fetching activities: {e}")
        return {}


def get_timesheets(begin, end):
    """Fetch timesheets from Kimai API"""
    url = f"{KIMAI_URL}/api/timesheets"
    headers = {
        "Authorization": f"Bearer {KIMAI_TOKEN}",
        "Accept": "application/json"
    }
    params = {
        "user": "all",
        "begin": begin,
        "end": end,
        "size": 500
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching timesheets: {e}")
        return []


def format_time(time_str):
    """Format ISO datetime string to readable time"""
    if not time_str:
        return None
    try:
        time_str_clean = time_str.replace('Z', '+00:00').replace('-0500', '-05:00').replace('-0400', '-04:00')
        dt = datetime.fromisoformat(time_str_clean)
        return dt.strftime('%I:%M %p').lstrip('0')
    except:
        return time_str[:5] if len(time_str) >= 5 else time_str


def extract_date(date_str):
    """Extract date from ISO datetime string"""
    if not date_str:
        return None
    try:
        time_str_clean = date_str.replace('Z', '+00:00').replace('-0500', '-05:00').replace('-0400', '-04:00')
        dt = datetime.fromisoformat(time_str_clean)
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str[:10] if len(date_str) >= 10 else date_str


def extract_machine_info(description):
    """Extract machine hours and equipment info from description"""
    if not description:
        return None
    
    info = {
        'machines': [],
        'hours': [],
        'work': description
    }
    
    # Look for patterns like "2hrs backhoe", "3 hours excavator", "D5 dozer", etc.
    hour_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:hrs?|hours?)\s+([a-zA-Z\s]+?)(?:,|\.|$)',
        r'(\d+(?:\.\d+)?)\s*(?:hrs?|hours?)\s+([a-zA-Z\s]+?)(?:\s|$)',
    ]
    
    # Pattern: equipment name + number + hrs
    equipment_patterns = [
        r'([A-Z]\d+|[a-zA-Z\s]+(?:dozer|backhoe|excavator|loader|truck|compactor|paver|milling|machine))\s+(\d+(?:\.\d+)?)\s*(?:hrs?|hours?)',
    ]
    
    # Extract hour patterns
    for pattern in hour_patterns:
        matches = re.finditer(pattern, description, re.IGNORECASE)
        for match in matches:
            hours = match.group(1)
            equipment = match.group(2).strip()
            info['hours'].append(f"{hours}hrs {equipment}")
            info['machines'].append(equipment)
    
    # Extract equipment patterns
    for pattern in equipment_patterns:
        matches = re.finditer(pattern, description, re.IGNORECASE)
        for match in matches:
            equipment = match.group(1).strip()
            hours = match.group(2)
            info['hours'].append(f"{equipment} {hours}hrs")
            info['machines'].append(equipment)
    
    # Look for equipment mentions without hours (e.g., "D5 dozer", "backhoe")
    equipment_keywords = ['dozer', 'backhoe', 'excavator', 'loader', 'truck', 'compactor', 
                         'paver', 'milling', 'grader', 'roller', 'skid', 'steer']
    for keyword in equipment_keywords:
        pattern = r'\b([A-Z]?\d*\s*[a-zA-Z\s]*' + keyword + r'[a-zA-Z\s]*)\b'
        matches = re.finditer(pattern, description, re.IGNORECASE)
        for match in matches:
            equipment = match.group(1).strip()
            if equipment not in info['machines']:
                info['machines'].append(equipment)
    
    return info if (info['machines'] or info['hours']) else None


def generate_weekly_project_report(monday_date):
    """Generate weekly project-based time report starting from Monday"""
    user_map = get_users()
    projects = get_projects()
    activities = get_activities()
    
    monday = datetime.strptime(monday_date, '%Y-%m-%d')
    sunday = monday + timedelta(days=6)
    
    begin = f"{monday_date}T00:00:00"
    end = f"{sunday.strftime('%Y-%m-%d')}T23:59:59"
    
    timesheets = get_timesheets(begin, end)
    
    if not timesheets:
        print(f"No timesheet entries found for week starting {monday_date}")
        return None
    
    # Group by project, then by date
    by_project = defaultdict(lambda: defaultdict(list))
    for entry in timesheets:
        project_id = entry.get('project')
        if project_id:
            entry_date = extract_date(entry.get('begin'))
            by_project[project_id][entry_date].append(entry)
    
    # Generate report
    report = f"""# Weekly Project Time Report - {monday_date} to {sunday.strftime('%Y-%m-%d')}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Week:** {monday.strftime('%A, %B %d')} - {sunday.strftime('%A, %B %d, %Y')}  
**Total Timesheet Entries:** {len(timesheets)}  
**Projects with Activity:** {len(by_project)}

---

"""
    
    # Sort projects by total hours (descending)
    project_totals = []
    for project_id, dates_dict in by_project.items():
        total_hours = sum(
            sum(e.get('duration', 0) for e in entries) 
            for entries in dates_dict.values()
        ) / 3600
        project_totals.append((project_id, total_hours, dates_dict))
    
    project_totals.sort(key=lambda x: x[1], reverse=True)
    
    # Generate report for each project
    for project_id, total_hours, dates_dict in project_totals:
        project = projects.get(project_id, {})
        project_name = project.get('name', f'Project {project_id}')
        parent_title = project.get('parentTitle')
        
        if parent_title:
            project_display = f"{project_name} ({parent_title})"
        else:
            project_display = project_name
        
        report += f"""## {project_display}

**Total Hours:** {total_hours:.2f}h  
**Days Worked:** {len(dates_dict)}  
**Total Entries:** {sum(len(entries) for entries in dates_dict.values())}

"""
        
        # Group by employee for summary
        by_employee = defaultdict(float)
        for date_entries in dates_dict.values():
            for entry in date_entries:
                user_id = entry.get('user')
                hours = entry.get('duration', 0) / 3600
                by_employee[user_id] += hours
        
        # Employee summary
        report += "### Employee Summary\n\n"
        report += "| Employee | Total Hours |\n"
        report += "|----------|-------------|\n"
        
        for user_id, hours in sorted(by_employee.items(), key=lambda x: x[1], reverse=True):
            user_name = user_map.get(user_id, f"User {user_id}")
            report += f"| {user_name} | {hours:.2f}h |\n"
        
        report += "\n"
        
        # Daily breakdown
        report += "### Daily Breakdown\n\n"
        
        for date_str in sorted(dates_dict.keys()):
            date_entries = dates_dict[date_str]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day_name = date_obj.strftime('%A, %B %d')
            day_hours = sum(e.get('duration', 0) for e in date_entries) / 3600
            
            report += f"#### {day_name} ({day_hours:.2f}h)\n\n"
            
            # Group by employee for this day
            by_employee_day = defaultdict(list)
            for entry in date_entries:
                user_id = entry.get('user')
                by_employee_day[user_id].append(entry)
            
            for user_id, user_entries in sorted(by_employee_day.items(), 
                                                key=lambda x: user_map.get(x[0], '')):
                user_name = user_map.get(user_id, f"User {user_id}")
                user_day_hours = sum(e.get('duration', 0) for e in user_entries) / 3600
                
                report += f"**{user_name}** ({user_day_hours:.2f}h):\n\n"
                
                for entry in sorted(user_entries, key=lambda x: x.get('begin', '')):
                    activity_id = entry.get('activity')
                    activity = activities.get(activity_id, {})
                    activity_name = activity.get('name', f'Activity {activity_id}')
                    
                    description = entry.get('description') or ''
                    description = description.strip() if description else ''
                    hours = entry.get('duration', 0) / 3600
                    begin_time = format_time(entry.get('begin'))
                    end_time = format_time(entry.get('end'))
                    
                    if description:
                        report += f"- **{activity_name}** ({hours:.2f}h)"
                        if begin_time and end_time:
                            report += f" - {begin_time} to {end_time}"
                        report += f"\n  - {description}\n"
                        
                        # Show extracted machine info if available
                        machine_info = extract_machine_info(description)
                        if machine_info:
                            if machine_info['hours']:
                                report += f"  - **Machine Hours:** {', '.join(machine_info['hours'])}\n"
                            if machine_info['machines']:
                                unique_machines = list(set(machine_info['machines']))
                                report += f"  - **Equipment:** {', '.join(unique_machines)}\n"
                        report += "\n"
                    else:
                        report += f"- **{activity_name}** ({hours:.2f}h)"
                        if begin_time and end_time:
                            report += f" - {begin_time} to {end_time}"
                        report += " - *No description*\n\n"
            
            report += "\n"
        
        report += "---\n\n"
    
    # Summary section
    report += f"""## Summary

**Total Projects:** {len(by_project)}  
**Total Hours:** {sum(e.get('duration', 0) for e in timesheets) / 3600:.2f}h  
**Total Employees:** {len(set(e.get('user') for e in timesheets))}  
**Days in Week:** {len(set(extract_date(e.get('begin')) for e in timesheets))}

### Projects by Total Hours

| Project | Total Hours | Days | Entries | Employees |
|---------|-------------|------|---------|-----------|
"""
    
    for project_id, total_hours, dates_dict in project_totals:
        project = projects.get(project_id, {})
        project_name = project.get('name', f'Project {project_id}')
        parent_title = project.get('parentTitle')
        if parent_title:
            project_display = f"{project_name} ({parent_title})"
        else:
            project_display = project_name
        
        total_entries = sum(len(entries) for entries in dates_dict.values())
        unique_employees = len(set(
            e.get('user') 
            for entries in dates_dict.values() 
            for e in entries
        ))
        days_worked = len(dates_dict)
        
        report += f"| {project_display} | {total_hours:.2f}h | {days_worked} | {total_entries} | {unique_employees} |\n"
    
    report += f"\n---\n\n**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # Save report
    today_str = datetime.now().strftime('%Y-%m-%d')
    date_dir = REPORTS_DIR / today_str
    date_dir.mkdir(parents=True, exist_ok=True)
    report_file = date_dir / f"project_time_report_weekly_{monday_date}.md"
    report_file.write_text(report)
    print(f"✅ Weekly project time report saved to: {report_file}")
    
    return report_file


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        monday_date = sys.argv[1]
    else:
        # Get Monday of last week
        today = datetime.now()
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        monday_date = last_monday.strftime('%Y-%m-%d')
    
    generate_weekly_project_report(monday_date)













