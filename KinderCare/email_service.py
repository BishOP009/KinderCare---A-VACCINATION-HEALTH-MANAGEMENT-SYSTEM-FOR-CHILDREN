import os
from typing import Optional
import user_database as udb
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_notification(user_id: int, child_id: int, recipient_email: str, 
                           subject: str, content: str) -> bool:
    """Send email notification and log it to the database."""
    try:
        # Try using SendGrid if available
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        if sendgrid_api_key:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=os.getenv("SENDGRID_FROM_EMAIL", "noreply@kindercare.app"),
                to_emails=recipient_email,
                subject=subject,
                html_content=content
            )
            
            try:
                sg = SendGridAPIClient(sendgrid_api_key)
                response = sg.send(message)
                
                # Log the email to database
                udb.log_email(user_id, child_id, recipient_email, subject, content, status='sent')
                return True
            except Exception as e:
                print(f"SendGrid error: {e}")
                # Fall through to try SMTP
        
        # Try using Gmail SMTP
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = os.getenv("SMTP_USERNAME", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        from_email = smtp_username  # Use Gmail address as sender
        
        if smtp_username and smtp_password:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = from_email
                msg["To"] = recipient_email
                
                html_part = MIMEText(content, "html")
                msg.attach(html_part)
                
                with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.sendmail(from_email, recipient_email, msg.as_string())
                
                # Log the email to database
                udb.log_email(user_id, child_id, recipient_email, subject, content, status='sent')
                print(f"✅ Email sent via SMTP to {recipient_email}")
                return True
            except Exception as e:
                print(f"SMTP error: {e}")
                # Log the failed email attempt
                udb.log_email(user_id, child_id, recipient_email, subject, content, status='failed')
                return False
        else:
            print("Email configuration missing: Please set SMTP_USERNAME and SMTP_PASSWORD")
            return False
            
    except Exception as e:
        print(f"Unexpected error in email service: {e}")
        try:
            udb.log_email(user_id, child_id, recipient_email, subject, content, status='failed')
        except:
            pass
        return False

def send_vaccination_reminder(user_id: int, child_id: int, child_name: str, 
                             recipient_email: str, vaccine_name: str, due_date: str) -> bool:
    """Send a vaccination reminder email."""
    subject = f"Vaccination Reminder for {child_name}"
    
    content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #667eea;">Vaccination Reminder</h2>
                <p>Hi,</p>
                <p>This is a reminder that <strong>{child_name}</strong> is due for the following vaccination:</p>
                <div style="background-color: #f0f7ff; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0;">
                    <p><strong>Vaccine:</strong> {vaccine_name}</p>
                    <p><strong>Due Date:</strong> {due_date}</p>
                </div>
                <p>Please schedule an appointment with your pediatrician to ensure your child's health and protection.</p>
                <p>Best regards,<br>KinderCare Team</p>
            </div>
        </body>
    </html>
    """
    
    return send_email_notification(user_id, child_id, recipient_email, subject, content)

def send_health_update_notification(user_id: int, child_id: int, child_name: str,
                                   recipient_email: str, event_type: str, 
                                   event_title: str, event_date: str) -> bool:
    """Send a health event update email."""
    subject = f"Health Update: {event_title} for {child_name}"
    
    content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #667eea;">Health Event Update</h2>
                <p>Hi,</p>
                <p>A new health event has been recorded for <strong>{child_name}</strong>:</p>
                <div style="background-color: #f0f7ff; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0;">
                    <p><strong>Event Type:</strong> {event_type}</p>
                    <p><strong>Event Title:</strong> {event_title}</p>
                    <p><strong>Date:</strong> {event_date}</p>
                </div>
                <p>You can view more details in your KinderCare dashboard.</p>
                <p>Best regards,<br>KinderCare Team</p>
            </div>
        </body>
    </html>
    """
    
    return send_email_notification(user_id, child_id, recipient_email, subject, content)
