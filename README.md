# KinderCare - Smart Child Vaccination & Health Assistant

A comprehensive full-stack Streamlit web application designed for parents to track and manage their child's vaccination schedule and health timeline. The application is user-friendly, medically responsible, and production-ready.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Schema](#database-schema)
- [Environment Variables](#environment-variables)
- [Email Notifications Setup](#email-notifications-setup)
- [Vaccination Guidelines Supported](#vaccination-guidelines-supported)
- [Medical Disclaimer](#medical-disclaimer)
- [Future Enhancements](#future-enhancements)

## Overview

KinderCare is a comprehensive application that helps parents:
- Track their child's vaccination schedule across multiple guidelines (India UIP, WHO)
- Maintain a detailed health timeline with vaccinations, illnesses, symptoms, and doctor visits
- Receive smart email reminders for upcoming vaccinations
- Get health guidance through an AI-powered assistant
- Access medical information through voice and text queries

The application is built with security and privacy in mind, storing all data locally in SQLite with no third-party data sharing.

## Features

### 1. **Personalized Vaccination Scheduler**
- Auto-generates vaccination schedules based on India (UIP) and WHO guidelines
- Tracks upcoming, overdue, completed, and pending vaccines
- Mark vaccines as completed with details:
  - Administered date
  - Doctor name
  - Batch number
  - Additional notes
- Visual status indicators for vaccination progress

### 2. **Health Timeline & History**
- Visual chronological timeline of all health events
- Track multiple event types:
  - Vaccinations
  - Illnesses
  - Symptoms
  - Doctor visits
- Filterable by category and date range
- Detailed event descriptions and medical notes

### 3. **Smart Email Reminders & Alerts**
- Automatic email reminders for upcoming vaccinations
- Customizable reminder timing:
  - 7 days before due date
  - 1 day before due date
  - On the due date
- Per-child notification preferences
- Email logging and tracking in database
- Gmail SMTP integration for reliable delivery

### 4. **Voice & Chat-Based AI Assistant**
- Natural language queries about vaccination schedules
- Voice input using OpenAI Whisper transcription
- Health guidance with medical disclaimers
- Conversational interface for parent-friendly interactions
- Context-aware responses based on child's health data

### 5. **Interactive Dashboard**
- Vaccination progress overview with charts
- Quick statistics on child's health status
- Color-coded vaccine status indicators
- Quick-access navigation to all features

### 6. **Account & Profile Management**
- Secure user registration and authentication
- Multiple child profile support per account
- Child profile customization:
  - Date of birth
  - Gender
  - Blood group
  - Known allergies
- Account settings and preferences

## Technology Stack

- **Frontend & Backend**: Streamlit (Python web framework)
- **Database**: SQLite (local database with schema migrations)
- **AI/NLP**: OpenAI GPT models & Whisper for chat and voice
- **Data Visualization**: Plotly for interactive charts
- **Email**: SMTP (Gmail integration)
- **Authentication**: Built-in session management

## Project Structure

```
kindercare/
├── app.py                              # Main Streamlit application entry point
├── database.py                         # SQLite database module with schema
├── user_database.py                    # User authentication and profiles database
├── email_service.py                    # Email sending and logging functionality
├── reminder_service.py                 # Vaccination reminder checking and scheduling
├── vaccination_guidelines.py           # Vaccination schedule generation logic
├── ai_assistant.py                     # OpenAI integration for chat and voice
│
├── pages/                              # Streamlit pages
│   ├── __init__.py
│   ├── home.py                        # Landing page
│   ├── login.py                       # User login page
│   ├── signup.py                      # User registration page
│   ├── dashboard.py                   # Main dashboard with charts
│   ├── vaccination_schedule.py        # Vaccination tracking and completion
│   ├── vaccination_timeline.py        # Visual timeline of vaccinations
│   ├── health_timeline.py             # Health events timeline
│   ├── assistant.py                   # AI chat and voice assistant
│   ├── settings.py                    # Child profiles and notification settings
│   ├── about_us.py                    # About and information page
│   └── diseases_remedies.py           # Common diseases information
│
├── data/                              # Vaccination guideline data
│   ├── vaccines_uip_india.json       # India UIP vaccination schedule
│   ├── vaccines_who.json             # WHO vaccination schedule
│   └── disease_remedies.json         # Common diseases information
│
├── .streamlit/
│   └── config.toml                    # Streamlit server configuration
│
├── requirements.txt                   # Python package dependencies
├── README.md                          # This file
│
└── Databases (auto-created):
    ├── vaccination_health.db          # Main vaccination and health database
    └── user_database.db               # User accounts and emails database
```

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.9 or higher
- pip (Python package manager)
- Git (for version control)

## Installation & Setup

### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd kindercare

# Or download and extract the project folder
```

### Step 2: Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

This installs:
- `streamlit` - Web application framework
- `openai` - AI assistant functionality
- `plotly` - Interactive charts and visualizations
- `python-dateutil` - Date manipulation
- `pandas` - Data manipulation
- `audio-recorder-streamlit` - Voice input recording
- `pymongo` - Optional database support
- `sendgrid` - Optional email service
- `sendgrid` - Optional SendGrid email integration

### Step 3: Set Up Environment Variables

Create a `.env` file in the project root or use Replit's Secrets tab to add:

```bash
# Required for AI Assistant
OPENAI_API_KEY=your_openai_api_key_here

# Required for Email Notifications (Gmail SMTP)
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=your-app-password
```

### Step 4: Run the Application

```bash
streamlit run app.py --server.port 5000
```

The application will be available at:
- **Local**: http://localhost:5000
- **Replit**: https://[your-replit-url].replit.dev

## Configuration

### Streamlit Configuration

The Streamlit server is configured in `.streamlit/config.toml`:

```toml
[server]
port = 5000
headless = true
```

Do not modify the server configuration unless specifically requested.

### Custom Theming

To customize the app's theme, update the CSS styles in:
- `app.py` - Global styles
- Individual page files - Page-specific styles

## Running the Application

### Development Mode

```bash
streamlit run app.py --server.port 5000
```

### Production Deployment

The application is ready for production deployment on Replit:

1. Push code to your Replit project
2. Set up all required secrets (OPENAI_API_KEY, SMTP_USERNAME, SMTP_PASSWORD)
3. Click the "Publish" button in Replit
4. Your app will be live at `https://[project-name].replit.dev`

## Database Schema

### User Database (`user_database.db`)

#### users table
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT) - User's full name
- `email` (TEXT UNIQUE) - User's email address
- `password` (TEXT) - Hashed/encrypted password
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### child_profiles table
- `id` (INTEGER PRIMARY KEY)
- `user_id` (INTEGER FOREIGN KEY)
- `name` (TEXT) - Child's name
- `date_of_birth` (DATE)
- `country_guideline` (TEXT) - "India (UIP)" or "WHO"
- `gender` (TEXT)
- `blood_group` (TEXT)
- `allergies` (TEXT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### emails table
- `id` (INTEGER PRIMARY KEY)
- `user_id` (INTEGER FOREIGN KEY)
- `child_id` (INTEGER FOREIGN KEY)
- `recipient_email` (TEXT)
- `subject` (TEXT)
- `content` (TEXT) - Full email HTML content
- `status` (TEXT) - "sent" or "failed"
- `sent_at` (TIMESTAMP)

### Main Database (`vaccination_health.db`)

#### vaccinations table
- `id` (INTEGER PRIMARY KEY)
- `child_id` (INTEGER FOREIGN KEY)
- `vaccine_name` (TEXT)
- `vaccine_code` (TEXT)
- `due_date` (DATE)
- `administered_date` (DATE)
- `status` (TEXT) - "pending", "completed", "overdue"
- `notes` (TEXT)
- `administered_by` (TEXT) - Doctor name
- `batch_number` (TEXT)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### health_events table
- `id` (INTEGER PRIMARY KEY)
- `child_id` (INTEGER FOREIGN KEY)
- `event_type` (TEXT) - "illness", "symptom", "doctor_visit", etc.
- `event_date` (DATE)
- `title` (TEXT)
- `description` (TEXT)
- `severity` (TEXT) - "mild", "moderate", "severe"
- `symptoms` (TEXT)
- `treatment` (TEXT)
- `doctor_name` (TEXT)
- `hospital_clinic` (TEXT)
- `created_at` (TIMESTAMP)

#### reminder_settings table
- `id` (INTEGER PRIMARY KEY)
- `child_id` (INTEGER FOREIGN KEY)
- `email_enabled` (BOOLEAN)
- `email_address` (TEXT)
- `reminder_7_days` (BOOLEAN) - Send reminder 7 days before
- `reminder_1_day` (BOOLEAN) - Send reminder 1 day before
- `reminder_on_day` (BOOLEAN) - Send reminder on due date
- `updated_at` (TIMESTAMP)

#### sent_reminders table
- `id` (INTEGER PRIMARY KEY)
- `vaccination_id` (INTEGER FOREIGN KEY)
- `reminder_type` (TEXT) - "7_days_before", "1_day_before", "on_due_date"
- `sent_via` (TEXT) - "email"
- `sent_at` (TIMESTAMP)

## Environment Variables

### Required Variables

#### OPENAI_API_KEY
- **Purpose**: Enables the AI assistant for chat and voice features
- **How to get**: Visit https://platform.openai.com/api-keys
- **Type**: Secret (encrypted)

```bash
OPENAI_API_KEY=sk-your-key-here
```

### Optional Variables (Email Notifications)

#### SMTP_USERNAME
- **Purpose**: Gmail address for sending emails
- **Type**: Secret (encrypted)

```bash
SMTP_USERNAME=your-email@gmail.com
```

#### SMTP_PASSWORD
- **Purpose**: Gmail app password (if 2FA enabled) or Gmail password
- **Type**: Secret (encrypted)

```bash
SMTP_PASSWORD=your-app-password
```

### Email Configuration Details

The application uses the following SMTP settings for Gmail:
- **Server**: smtp.gmail.com
- **Port**: 587 (TLS)
- **Authentication**: Yes (SMTP_USERNAME and SMTP_PASSWORD)

## Email Notifications Setup

### Setting Up Gmail SMTP

Email reminders are sent automatically when vaccines are due. Follow these steps:

#### Option 1: Using App Password (Recommended with 2-Factor Authentication)

1. Enable 2-Step Verification in your Google Account
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. Generate an App Password
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or your device)
   - Click "Generate"
   - Copy the generated 16-character password

3. Add to Replit Secrets:
   - `SMTP_USERNAME`: your-email@gmail.com
   - `SMTP_PASSWORD`: (paste the 16-character password)

#### Option 2: Using Gmail Password (Less Secure Apps)

1. Allow less secure apps in your Google Account
   - Go to https://myaccount.google.com/security
   - Enable "Less secure app access"

2. Add to Replit Secrets:
   - `SMTP_USERNAME`: your-email@gmail.com
   - `SMTP_PASSWORD`: your-gmail-password

### Configuring Reminders

1. Log in to the application
2. Go to **Settings** → **Notifications**
3. For each child:
   - Enable "Email Reminders"
   - Enter recipient email address
   - Choose reminder timing:
     - 7 days before due date
     - 1 day before due date
     - On the due date
   - Click "Save Notification Settings"

### Email Reminder Features

- Reminders are sent automatically based on vaccination due dates
- Each reminder is tracked in the database to avoid duplicates
- Email content includes:
  - Child's name
  - Vaccine name
  - Due date
  - Call to action to schedule appointment
- All sent emails are logged in the emails table with:
  - Recipient
  - Subject
  - Full HTML content
  - Delivery status (sent/failed)
  - Timestamp

## Vaccination Guidelines Supported

### 1. India (UIP)
**Universal Immunization Programme**
- Government of India recommended schedule
- Covers birth to 16 years
- Includes: BCG, OPV, IPV, Hepatitis B, DPT, Japanese Encephalitis, etc.
- Data source: `data/vaccines_uip_india.json`

### 2. WHO
**World Health Organization Recommendations**
- Global best-practice recommendations
- Covers birth to 16 years
- Includes standard WHO-recommended vaccines
- Data source: `data/vaccines_who.json`

Parents can select their preferred guideline when creating a child profile. The application automatically generates the appropriate schedule based on the selected guideline.

## Medical Disclaimer

⚠️ **IMPORTANT**: This application is designed for informational and tracking purposes only.

**This application is NOT a substitute for professional medical advice, diagnosis, or treatment.**

- Always consult your child's pediatrician or qualified healthcare provider for:
  - Medical diagnosis
  - Treatment recommendations
  - Medication advice
  - Health concerns or emergencies
  - Personalized medical guidance

- In case of medical emergency, call your local emergency services immediately.

- The information provided in this app is for general informational purposes and should not be relied upon as medical advice.

- Parents should always follow their healthcare provider's recommendations regarding vaccinations and health management.

## Future Enhancements

- [ ] PostgreSQL migration for enterprise deployment
- [ ] Twilio SMS integration for text reminders
- [ ] PDF vaccination certificate generation
- [ ] QR code generation for vaccine certificates
- [ ] Multi-language support (Hindi, Tamil, Telugu, etc.)
- [ ] Mobile app version (React Native)
- [ ] Parent-to-pediatrician direct messaging
- [ ] Vaccine availability tracking
- [ ] Integration with government health portals
- [ ] Advanced analytics and reports
- [ ] Calendar synchronization (Google Calendar, Outlook)
- [ ] Integration with health insurance providers

## Support & Troubleshooting

### Common Issues

**Issue**: "OPENAI_API_KEY not found"
- **Solution**: Add your OpenAI API key to Replit Secrets

**Issue**: "Email notifications not sending"
- **Solution**: Check that SMTP_USERNAME and SMTP_PASSWORD are correctly set in Secrets

**Issue**: "Database locked" error
- **Solution**: This is temporary. The app will retry automatically.

**Issue**: "Vaccine schedule not generating"
- **Solution**: Ensure date of birth is valid and vaccination guideline is selected

### Getting Help

1. Check the console logs for error messages
2. Verify all environment variables are set correctly
3. Ensure database files have write permissions

## License

This project is built for educational and personal use.

## Version

**Current Version**: 1.0.0  
**Last Updated**: December 2025

---

**KinderCare** - Empowering parents with better vaccination and health tracking.
