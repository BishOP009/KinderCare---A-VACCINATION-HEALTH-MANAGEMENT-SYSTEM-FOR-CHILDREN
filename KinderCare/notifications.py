import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, timedelta
from typing import List, Dict, Optional
import database as db

def get_upcoming_reminders(child_id: int) -> List[Dict]:
    vaccinations = db.get_vaccinations(child_id)
    today = date.today()
    reminders = []
    
    for vacc in vaccinations:
        if vacc['status'] == 'completed':
            continue
            
        due_date = vacc['due_date']
        if isinstance(due_date, str):
            due_date = date.fromisoformat(due_date)
        
        days_until = (due_date - today).days
        
        if days_until == 7:
            reminders.append({
                "vaccination": vacc,
                "reminder_type": "7_days",
                "message": f"Reminder: {vacc['vaccine_name']} is due in 7 days ({due_date.strftime('%B %d, %Y')})"
            })
        elif days_until == 1:
            reminders.append({
                "vaccination": vacc,
                "reminder_type": "1_day",
                "message": f"Reminder: {vacc['vaccine_name']} is due tomorrow ({due_date.strftime('%B %d, %Y')})"
            })
        elif days_until == 0:
            reminders.append({
                "vaccination": vacc,
                "reminder_type": "on_day",
                "message": f"Reminder: {vacc['vaccine_name']} is due today!"
            })
        elif days_until < 0:
            reminders.append({
                "vaccination": vacc,
                "reminder_type": "overdue",
                "message": f"OVERDUE: {vacc['vaccine_name']} was due on {due_date.strftime('%B %d, %Y')} ({abs(days_until)} days ago)"
            })
    
    return reminders

def send_email_reminder(to_email: str, child_name: str, reminders: List[Dict], 
                        smtp_server: str = None, smtp_port: int = 587,
                        smtp_user: str = None, smtp_password: str = None) -> bool:
    if not smtp_server or not smtp_user or not smtp_password:
        return False
    
    try:
        subject = f"Vaccination Reminder for {child_name}"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .reminder {{ margin: 10px 0; padding: 15px; border-left: 4px solid #4CAF50; background: #f9f9f9; }}
                .overdue {{ border-left-color: #f44336; }}
                .footer {{ background: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Smart Child Vaccination Assistant</h1>
            </div>
            <div class="content">
                <h2>Vaccination Reminders for {child_name}</h2>
                <p>Here are your upcoming vaccination reminders:</p>
        """
        
        for reminder in reminders:
            reminder_class = "reminder overdue" if reminder['reminder_type'] == 'overdue' else "reminder"
            html_content += f'<div class="{reminder_class}">{reminder["message"]}</div>'
        
        html_content += """
                <p style="margin-top: 20px;">
                    <strong>Note:</strong> Please consult with your child's pediatrician before administering any vaccines.
                </p>
            </div>
            <div class="footer">
                <p>This is an automated reminder from Smart Child Vaccination & Health Assistant.</p>
                <p>For questions, please consult your healthcare provider.</p>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to_email
        
        text_content = f"Vaccination Reminders for {child_name}\n\n"
        for reminder in reminders:
            text_content += f"- {reminder['message']}\n"
        text_content += "\nPlease consult with your child's pediatrician before administering any vaccines."
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_email, msg.as_string())
        
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def get_in_app_notifications(child_id: int) -> List[Dict]:
    reminders = get_upcoming_reminders(child_id)
    notifications = []
    
    overdue = [r for r in reminders if r['reminder_type'] == 'overdue']
    today_due = [r for r in reminders if r['reminder_type'] == 'on_day']
    tomorrow = [r for r in reminders if r['reminder_type'] == '1_day']
    week_away = [r for r in reminders if r['reminder_type'] == '7_days']
    
    if overdue:
        notifications.append({
            "type": "error",
            "title": f"{len(overdue)} Overdue Vaccine(s)",
            "message": ", ".join([r['vaccination']['vaccine_name'] for r in overdue[:3]]),
            "count": len(overdue)
        })
    
    if today_due:
        notifications.append({
            "type": "warning",
            "title": f"{len(today_due)} Vaccine(s) Due Today",
            "message": ", ".join([r['vaccination']['vaccine_name'] for r in today_due]),
            "count": len(today_due)
        })
    
    if tomorrow:
        notifications.append({
            "type": "info",
            "title": f"{len(tomorrow)} Vaccine(s) Due Tomorrow",
            "message": ", ".join([r['vaccination']['vaccine_name'] for r in tomorrow]),
            "count": len(tomorrow)
        })
    
    if week_away:
        notifications.append({
            "type": "info",
            "title": f"{len(week_away)} Vaccine(s) Due in 7 Days",
            "message": ", ".join([r['vaccination']['vaccine_name'] for r in week_away]),
            "count": len(week_away)
        })
    
    return notifications

def check_and_send_reminders(child_id: int) -> Dict:
    child = db.get_child(child_id)
    settings = db.get_reminder_settings(child_id)
    
    if not child or not settings:
        return {"success": False, "message": "Child or settings not found"}
    
    reminders = get_upcoming_reminders(child_id)
    
    if not reminders:
        return {"success": True, "message": "No reminders to send", "sent": 0}
    
    filtered_reminders = []
    for r in reminders:
        if r['reminder_type'] == '7_days' and settings.get('reminder_7_days'):
            filtered_reminders.append(r)
        elif r['reminder_type'] == '1_day' and settings.get('reminder_1_day'):
            filtered_reminders.append(r)
        elif r['reminder_type'] == 'on_day' and settings.get('reminder_on_day'):
            filtered_reminders.append(r)
        elif r['reminder_type'] == 'overdue':
            filtered_reminders.append(r)
    
    sent_count = 0
    
    if settings.get('email_enabled') and settings.get('email_address'):
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_user = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if send_email_reminder(
            settings['email_address'],
            child['name'],
            filtered_reminders,
            smtp_server, smtp_port, smtp_user, smtp_password
        ):
            sent_count += 1
            for r in filtered_reminders:
                db.record_sent_reminder(r['vaccination']['id'], r['reminder_type'], 'email')
    
    return {
        "success": True,
        "message": f"Processed {len(filtered_reminders)} reminders",
        "sent": sent_count
    }
