"""Service to check and send vaccination reminders."""
from datetime import date, timedelta
from typing import Optional
import database as db
import user_database as udb
import email_service

def check_and_send_reminders():
    """Check all users for due vaccinations and send email reminders."""
    today = date.today()
    
    try:
        # Get all users
        users = udb.get_all_users()
        
        for user in users:
            # Get all children for this user
            children = udb.get_all_children(user['id'])
            
            for child in children:
                # Get reminder settings
                settings = db.get_reminder_settings(child['id'])
                if not settings or not settings.get('email_enabled'):
                    continue
                
                email_address = settings.get('email_address')
                if not email_address:
                    continue
                
                # Get all vaccinations
                vaccinations = db.get_vaccinations(child['id'])
                
                for vacc in vaccinations:
                    # Skip if already administered
                    if vacc.get('status') == 'completed':
                        continue
                    
                    # Parse due date
                    due_date_str = vacc.get('due_date')
                    if not due_date_str:
                        continue
                    
                    try:
                        due_date = date.fromisoformat(due_date_str)
                    except (ValueError, TypeError):
                        continue
                    
                    # Check if we should send a reminder
                    days_until_due = (due_date - today).days
                    
                    should_send = False
                    reminder_type = None
                    
                    if days_until_due == 7 and settings.get('reminder_7_days'):
                        should_send = True
                        reminder_type = "7_days_before"
                    elif days_until_due == 1 and settings.get('reminder_1_day'):
                        should_send = True
                        reminder_type = "1_day_before"
                    elif days_until_due == 0 and settings.get('reminder_on_day'):
                        should_send = True
                        reminder_type = "on_due_date"
                    
                    # Check if reminder was already sent for this vaccination and type
                    if should_send and reminder_type:
                        # Check if this reminder was already sent
                        sent_reminders = db.get_sent_reminders(vacc['id'])
                        already_sent = any(r.get('reminder_type') == reminder_type for r in sent_reminders)
                        
                        if not already_sent:
                            # Send email reminder
                            success = email_service.send_vaccination_reminder(
                                user_id=user['id'],
                                child_id=child['id'],
                                child_name=child['name'],
                                recipient_email=email_address,
                                vaccine_name=vacc['vaccine_name'],
                                due_date=due_date.strftime('%B %d, %Y')
                            )
                            
                            if success:
                                # Record that reminder was sent
                                db.record_sent_reminder(vacc['id'], reminder_type, 'email')
    
    except Exception as e:
        print(f"Error in check_and_send_reminders: {e}")

