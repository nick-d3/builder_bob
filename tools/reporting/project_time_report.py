#!/usr/bin/env python3
"""
Project-Based Time Report Generator

Groups timesheet entries by project/job and shows:
- Employee time on each project
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
    # Pattern: number + (hrs|hours|hr) + equipment name
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


def generate_project_report(date_str):
    """Generate project-based time report for a specific date"""
    user_map = get_users()
    projects = get_projects()
    activities = get_activities()
    
    begin = f"{date_str}T00:00:00"
    end = f"{date_str}T23:59:59"
    
    timesheets = get_timesheets(begin, end)
    
    if not timesheets:
        print(f"No timesheet entries found for {date_str}")
        return None
    
    # Group by project
    by_project = defaultdict(list)
    for entry in timesheets:
        project_id = entry.get('project')
        if project_id:
            by_project[project_id].append(entry)
    
    # Create directory for project reports
    today_str = datetime.now().strftime('%Y-%m-%d')
    date_dir = REPORTS_DIR / today_str
    date_dir.mkdir(parents=True, exist_ok=True)
    project_reports_dir = date_dir / f"project_reports_{date_str}"
    project_reports_dir.mkdir(parents=True, exist_ok=True)
    
    # Sort projects by total hours (descending)
    project_totals = []
    for project_id, entries in by_project.items():
        total_hours = sum(e.get('duration', 0) for e in entries) / 3600
        project_totals.append((project_id, total_hours, entries))
    
    project_totals.sort(key=lambda x: x[1], reverse=True)
    
    # Generate individual report for each project
    project_files = []
    for project_id, total_hours, entries in project_totals:
        project = projects.get(project_id, {})
        project_name = project.get('name', f'Project {project_id}')
        parent_title = project.get('parentTitle')
        
        if parent_title:
            project_display = f"{project_name} ({parent_title})"
        else:
            project_display = project_name
        
        # Create filename-safe version of project name
        safe_filename = project_display.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('/', '-').replace('\\', '-')
        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in ('-', '_'))
        project_file = project_reports_dir / f"{safe_filename}.md"
        
        # Start individual project report
        project_report = f"""# {project_display} - {date_str}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Date:** {date_str}  
**Total Hours:** {total_hours:.2f}h  
**Total Entries:** {len(entries)}

---
"""
        
        # Group by employee
        by_employee = defaultdict(list)
        for entry in entries:
            user_id = entry.get('user')
            by_employee[user_id].append(entry)
        
        # Employee time breakdown with start/stop times
        project_report += "### Employee Time Breakdown\n\n"
        project_report += "| Employee | Activity | Start Time | Stop Time | Hours |\n"
        project_report += "|----------|----------|------------|----------|-------|\n"
        
        employee_totals = []
        for user_id, user_entries in by_employee.items():
            user_name = user_map.get(user_id, f"User {user_id}")
            user_total_hours = sum(e.get('duration', 0) for e in user_entries) / 3600
            
            # Group by activity for this user
            by_activity = defaultdict(list)
            for entry in user_entries:
                activity_id = entry.get('activity')
                by_activity[activity_id].append(entry)
            
            for activity_id, activity_entries in by_activity.items():
                activity = activities.get(activity_id, {})
                activity_name = activity.get('name', f'Activity {activity_id}')
                activity_hours = sum(e.get('duration', 0) for e in activity_entries) / 3600
                
                # Get earliest start and latest end for this activity
                start_times = []
                end_times = []
                for e in activity_entries:
                    if e.get('begin'):
                        start_times.append(e.get('begin'))
                    if e.get('end'):
                        end_times.append(e.get('end'))
                
                if start_times and end_times:
                    # Sort to get earliest start and latest end
                    start_times.sort()
                    end_times.sort()
                    start_display = format_time(start_times[0])
                    end_display = format_time(end_times[-1])
                else:
                    start_display = '—'
                    end_display = '—'
                
                project_report += f"| {user_name} | {activity_name} | {start_display} | {end_display} | {activity_hours:.2f}h |\n"
            
            employee_totals.append((user_name, user_total_hours, user_entries))
        
        project_report += "\n"
        
        # Descriptions and additional information
        project_report += "### Time Log Details\n\n"
        
        # Collect all descriptions with context
        descriptions_by_employee = defaultdict(list)
        all_machine_hours = []  # Collect all machine hours for table
        
        for entry in entries:
            user_id = entry.get('user')
            user_name = user_map.get(user_id, f"User {user_id}")
            activity_id = entry.get('activity')
            activity = activities.get(activity_id, {})
            activity_name = activity.get('name', f'Activity {activity_id}')
            
            description = entry.get('description') or ''
            description = description.strip() if description else ''
            hours = entry.get('duration', 0) / 3600
            begin_time = format_time(entry.get('begin'))
            end_time = format_time(entry.get('end'))
            
            machine_info = extract_machine_info(description) if description else None
            
            descriptions_by_employee[user_name].append({
                'description': description,
                'hours': hours,
                'activity': activity_name,
                'begin': begin_time,
                'end': end_time,
                'machine_info': machine_info
            })
            
            # Collect machine hours for table
            if machine_info:
                # Clean up equipment list - remove duplicates and normalize
                unique_equipment = []
                seen = set()
                for eq in machine_info['machines']:
                    eq_lower = eq.lower().strip()
                    # Skip if it's just a number or hour reference
                    if eq_lower and not eq_lower.replace('hrs', '').replace('hours', '').replace('hr', '').strip().isdigit():
                        if eq_lower not in seen:
                            unique_equipment.append(eq.strip())
                            seen.add(eq_lower)
                
                equipment_str = ', '.join(unique_equipment) if unique_equipment else '—'
                
                if machine_info['hours']:
                    # Add entries with explicit hours
                    for hour_entry in machine_info['hours']:
                        all_machine_hours.append({
                            'employee': user_name,
                            'activity': activity_name,
                            'hours': hour_entry,
                            'equipment': equipment_str,
                            'start': begin_time,
                            'end': end_time
                        })
                elif unique_equipment:
                    # Add entries with equipment mentions but no explicit hours
                    all_machine_hours.append({
                        'employee': user_name,
                        'activity': activity_name,
                        'hours': '—',
                        'equipment': equipment_str,
                        'start': begin_time,
                        'end': end_time
                    })
        
        # Display descriptions as paragraphs - one per entry
        for user_name in sorted(descriptions_by_employee.keys()):
            user_descriptions = descriptions_by_employee[user_name]
            project_report += f"#### {user_name}\n\n"
            
            # Sort by start time
            user_descriptions.sort(key=lambda x: x['begin'] or '')
            
            for desc_entry in user_descriptions:
                activity_name = desc_entry['activity']
                start_time = desc_entry['begin'] or '—'
                end_time = desc_entry['end'] or '—'
                description = desc_entry['description']
                
                project_report += f"**{activity_name}** ({start_time} - {end_time}): "
                if description:
                    project_report += f"{description}\n\n"
                else:
                    project_report += "*No description*\n\n"
        
        # Machine Hours Table
        if all_machine_hours:
            project_report += "### Machine Hours\n\n"
            project_report += "| Employee | Activity | Start Time | Stop Time | Machine Hours | Equipment |\n"
            project_report += "|----------|----------|------------|----------|---------------|-----------|\n"
            
            for mh in all_machine_hours:
                project_report += f"| {mh['employee']} | {mh['activity']} | {mh['start'] or '—'} | {mh['end'] or '—'} | {mh['hours']} | {mh.get('equipment', '—')} |\n"
            
            project_report += "\n"
        
        project_report += f"\n**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # Save individual project report
        project_file.write_text(project_report)
        project_files.append((project_display, safe_filename, total_hours, len(entries)))
        print(f"✅ Project report saved: {project_file.name}")
    
    # Create summary/index file
    summary_report = f"""# Project Time Reports Summary - {date_str}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Date:** {date_str}  
**Total Timesheet Entries:** {len(timesheets)}  
**Projects with Activity:** {len(by_project)}

---

## Summary

**Total Projects:** {len(by_project)}  
**Total Hours:** {sum(e.get('duration', 0) for e in timesheets) / 3600:.2f}h  
**Total Employees:** {len(set(e.get('user') for e in timesheets))}

---

## Individual Project Reports

| Project | Total Hours | Entries | Report File |
|---------|-------------|---------|-------------|
"""
    
    for project_display, filename, total_hours, entry_count in project_files:
        summary_report += f"| [{project_display}](./{filename}.md) | {total_hours:.2f}h | {entry_count} | `{filename}.md` |\n"
    
    summary_report += f"\n---\n\n**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # Save summary file
    summary_file = project_reports_dir / "README.md"
    summary_file.write_text(summary_report)
    print(f"✅ Summary report saved: {summary_file}")
    
    return project_reports_dir


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
    
    generate_project_report(date_str)

