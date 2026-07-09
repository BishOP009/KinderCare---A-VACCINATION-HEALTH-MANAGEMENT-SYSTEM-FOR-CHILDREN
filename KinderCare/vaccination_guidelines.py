from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Dict
import json
import os

def load_vaccine_data(guideline: str) -> List[Dict]:
    """Load vaccine data from JSON files."""
    if guideline == "India (UIP)":
        json_path = "data/vaccines_uip_india.json"
    elif guideline == "WHO":
        json_path = "data/vaccines_who.json"
    else:
        json_path = "data/vaccines_who.json"
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            return data.get('vaccines', [])
    except FileNotFoundError:
        return []

def get_schedule_for_guideline(guideline: str) -> List[Dict]:
    """Get vaccination schedule for the specified guideline."""
    return load_vaccine_data(guideline)

def calculate_due_date(dob: date, age_weeks: int) -> date:
    """Calculate the due date for a vaccine based on birth date and age in weeks."""
    return dob + timedelta(weeks=age_weeks)

def generate_vaccination_schedule(dob: date, guideline: str) -> List[Dict]:
    """Generate a personalized vaccination schedule for a child."""
    schedule = get_schedule_for_guideline(guideline)
    vaccination_schedule = []
    
    for vaccine in schedule:
        due_date = calculate_due_date(dob, vaccine["age_weeks"])
        vaccination_schedule.append({
            "vaccine_name": vaccine["name"],
            "vaccine_code": vaccine["id"],
            "due_date": due_date,
            "age_label": vaccine["age_label"],
            "description": vaccine.get("description", ""),
            "full_name": vaccine.get("full_name", vaccine["name"]),
            "doses": vaccine.get("doses", 1),
            "route": vaccine.get("route", ""),
            "notes": vaccine.get("notes", "")
        })
    
    return vaccination_schedule

def get_vaccine_status(due_date: date, administered_date: date = None) -> str:
    """Determine the status of a vaccine based on dates."""
    today = date.today()
    
    if administered_date:
        return "completed"
    elif due_date < today:
        return "overdue"
    elif due_date <= today + timedelta(days=30):
        return "upcoming"
    else:
        return "pending"

def categorize_vaccinations(vaccinations: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize vaccinations into different status groups."""
    today = date.today()
    categories = {
        "overdue": [],
        "upcoming": [],
        "completed": [],
        "pending": []
    }
    
    for vacc in vaccinations:
        due_date = vacc.get('due_date')
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
        
        if vacc.get('status') == 'completed':
            categories["completed"].append(vacc)
        elif due_date < today:
            categories["overdue"].append(vacc)
        elif due_date <= today + timedelta(days=30):
            categories["upcoming"].append(vacc)
        else:
            categories["pending"].append(vacc)
    
    return categories

def get_age_string(dob: date) -> str:
    """Get a human-readable age string from a date of birth."""
    today = date.today()
    delta = relativedelta(today, dob)
    
    parts = []
    if delta.years > 0:
        parts.append(f"{delta.years} year{'s' if delta.years > 1 else ''}")
    if delta.months > 0:
        parts.append(f"{delta.months} month{'s' if delta.months > 1 else ''}")
    if delta.days > 0 and delta.years == 0:
        parts.append(f"{delta.days} day{'s' if delta.days > 1 else ''}")
    
    return ", ".join(parts) if parts else "Newborn"
