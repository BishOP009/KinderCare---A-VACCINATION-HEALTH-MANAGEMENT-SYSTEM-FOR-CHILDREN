import streamlit as st
from datetime import date, datetime
import os
import database as db
from vaccination_guidelines import generate_vaccination_schedule

def render():
    st.markdown("""
    <style>
        h2, h3 {
            color: #1a1a1a !important;
        }
        p {
            color: #000 !important;
        }
        
        /* Settings Tab Text - Force Black Color for Visibility */
        [data-testid="stTabs"] button {
            color: #000000 !important;
            font-weight: 600 !important;
        }
        
        [data-testid="stTabs"] button span {
            color: #000000 !important;
        }
        
        [data-testid="stTabs"] button p {
            color: #000000 !important;
        }
        
        [data-testid="stTabs"] button * {
            color: #000000 !important;
        }
        
        /* Calendar Month and Year Visibility */
        [data-testid="stDateInput"] button {
            color: #000000 !important;
        }
        
        .react-datepicker {
            background-color: #FFFFFF !important;
        }
        
        .react-datepicker__header {
            background-color: #FFFFFF !important;
        }
        
        .react-datepicker__header div {
            color: #333333 !important;
        }
        
        .react-datepicker__current-month,
        .react-datepicker__current-month-w3 {
            color: #000000 !important;
            font-weight: 700 !important;
            background-color: #FFFFFF !important;
            font-size: 1rem !important;
        }
        
        .react-datepicker__day {
            color: #333333 !important;
        }
        
        .react-datepicker__day:hover {
            background-color: #f0f0f0 !important;
            color: #333333 !important;
        }
        
        .react-datepicker__day--selected {
            background-color: #667eea !important;
            color: #FFFFFF !important;
        }
        
        .react-datepicker__navigation-icon::before {
            border-color: #333333 !important;
        }
        
        .react-datepicker__day-names {
            background-color: #FFFFFF !important;
        }
        
        .react-datepicker__day-name {
            color: #333333 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="color: #667eea; margin-top: 0;">⚙️ Settings</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #000; margin-bottom: 1.5rem;">Manage your child profiles, notification preferences, and account settings</p>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Child Profiles", "Notifications", "About", "Account"])
    
    with tab1:
        render_child_profiles()
    
    with tab2:
        render_notification_settings()
    
    with tab3:
        render_about()
    
    with tab4:
        render_account()

def render_child_profiles():
    st.subheader("Manage Child Profiles")
    
    if st.button("Add New Child Profile", type="primary"):
        st.session_state.show_add_child = True
    
    if st.session_state.get('show_add_child', False):
        render_add_child_form()
    
    user_id = st.session_state.get('user_id')
    children = db.get_all_children(user_id=user_id)
    
    if children:
        st.markdown("---")
        st.subheader("Existing Profiles")
        
        for child in children:
            render_child_profile_card(child)
    else:
        st.info("No child profiles yet. Add a child to get started with vaccination tracking.")

def render_add_child_form():
    with st.form(key="add_child_form"):
        st.subheader("Add New Child")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Child's Name", placeholder="Enter child's name")
        with col2:
            dob = st.date_input(
                "Date of Birth",
                value=date.today(),
                max_value=date.today(),
                min_value=date(2000, 1, 1)
            )
        
        col1, col2 = st.columns(2)
        with col1:
            country = st.selectbox(
                "Vaccination Guideline",
                ["India (UIP)", "WHO"],
                help="Select the vaccination guidelines to follow"
            )
        with col2:
            gender = st.selectbox("Gender", ["Not specified", "Male", "Female", "Other"])
        
        col1, col2 = st.columns(2)
        with col1:
            blood_group = st.selectbox(
                "Blood Group (Optional)",
                ["Not specified", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            )
        with col2:
            allergies = st.text_input("Known Allergies (Optional)", placeholder="e.g., Penicillin, Eggs")
        
        received_vaccines = st.text_area(
            "Already Received Vaccines (Optional)",
            placeholder="Enter vaccine names separated by commas (e.g., BCG, OPV, Hepatitis B)",
            help="If your child has already received some vaccines, enter their names here. They will be marked as completed."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Add Child", type="primary", width='stretch'):
                if not name:
                    st.error("Please enter the child's name.")
                else:
                    user_id = st.session_state.get('user_id')
                    child_id = db.add_child(
                        name=name,
                        date_of_birth=dob.isoformat(),
                        country_guideline=country,
                        user_id=user_id,
                        gender=gender if gender != "Not specified" else None,
                        blood_group=blood_group if blood_group != "Not specified" else None,
                        allergies=allergies if allergies else None
                    )
                    
                    received_list = []
                    if received_vaccines:
                        received_list = [v.strip().lower() for v in received_vaccines.split(',') if v.strip()]
                    
                    schedule = generate_vaccination_schedule(dob, country)
                    for vacc in schedule:
                        is_received = any(
                            recv in vacc['vaccine_name'].lower() or 
                            vacc['vaccine_name'].lower() in recv or
                            recv in vacc['vaccine_code'].lower()
                            for recv in received_list
                        )
                        
                        vacc_id = db.add_vaccination(
                            child_id=child_id,
                            vaccine_name=vacc['vaccine_name'],
                            vaccine_code=vacc['vaccine_code'],
                            due_date=vacc['due_date'].isoformat(),
                            status='completed' if is_received else 'pending'
                        )
                        
                        if is_received:
                            db.update_vaccination_status(
                                vacc_id,
                                status='completed',
                                administered_date=date.today().isoformat(),
                                notes='Marked as already received during profile creation'
                            )
                    
                    st.session_state.selected_child_id = child_id
                    st.session_state.show_add_child = False
                    completed_count = len([v for v in schedule if any(
                        recv in v['vaccine_name'].lower() or 
                        v['vaccine_name'].lower() in recv or
                        recv in v['vaccine_code'].lower()
                        for recv in received_list
                    )]) if received_list else 0
                    if completed_count > 0:
                        st.success(f"Child profile for {name} created! {completed_count} vaccine(s) marked as completed.")
                    else:
                        st.success(f"Child profile for {name} created with vaccination schedule!")
                    st.rerun()
        with col2:
            if st.form_submit_button("Cancel", width='stretch'):
                st.session_state.show_add_child = False
                st.rerun()

def render_child_profile_card(child):
    dob = child['date_of_birth']
    if isinstance(dob, str):
        dob = date.fromisoformat(dob)
    
    from vaccination_guidelines import get_age_string
    age = get_age_string(dob)
    
    with st.expander(f"{child['name']} - {age}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Date of Birth:** {dob.strftime('%B %d, %Y')}")
            st.write(f"**Age:** {age}")
            st.write(f"**Guideline:** {child['country_guideline']}")
        with col2:
            st.write(f"**Gender:** {child.get('gender', 'Not specified')}")
            st.write(f"**Blood Group:** {child.get('blood_group', 'Not specified')}")
            st.write(f"**Allergies:** {child.get('allergies', 'None recorded')}")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Edit", key=f"edit_{child['id']}", width='stretch'):
                st.session_state[f"edit_child_{child['id']}"] = True
        with col2:
            if st.button("Regenerate Schedule", key=f"regen_{child['id']}", width='stretch'):
                db.delete_all_vaccinations(child['id'])
                schedule = generate_vaccination_schedule(dob, child['country_guideline'])
                for vacc in schedule:
                    db.add_vaccination(
                        child_id=child['id'],
                        vaccine_name=vacc['vaccine_name'],
                        vaccine_code=vacc['vaccine_code'],
                        due_date=vacc['due_date'].isoformat(),
                        status='pending'
                    )
                st.success("Vaccination schedule regenerated!")
                st.rerun()
        with col3:
            if st.button("Delete", key=f"delete_{child['id']}", type="secondary", width='stretch'):
                st.session_state[f"confirm_delete_{child['id']}"] = True
        
        if st.session_state.get(f"confirm_delete_{child['id']}", False):
            st.warning(f"Are you sure you want to delete {child['name']}'s profile? This cannot be undone.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, Delete", key=f"confirm_yes_{child['id']}", type="primary"):
                    db.delete_child(child['id'])
                    st.session_state[f"confirm_delete_{child['id']}"] = False
                    if st.session_state.get('selected_child_id') == child['id']:
                        st.session_state.selected_child_id = None
                    st.success("Profile deleted.")
                    st.rerun()
            with col2:
                if st.button("Cancel", key=f"confirm_no_{child['id']}"):
                    st.session_state[f"confirm_delete_{child['id']}"] = False
                    st.rerun()
        
        if st.session_state.get(f"edit_child_{child['id']}", False):
            render_edit_child_form(child)

def render_edit_child_form(child):
    dob = child['date_of_birth']
    if isinstance(dob, str):
        dob = date.fromisoformat(dob)
    
    with st.form(key=f"edit_child_form_{child['id']}"):
        st.subheader(f"Edit {child['name']}")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Child's Name", value=child['name'])
        with col2:
            new_dob = st.date_input("Date of Birth", value=dob, max_value=date.today())
        
        col1, col2 = st.columns(2)
        with col1:
            guidelines = ["India (UIP)", "WHO"]
            country = st.selectbox(
                "Vaccination Guideline",
                guidelines,
                index=guidelines.index(child['country_guideline']) if child['country_guideline'] in guidelines else 0
            )
        with col2:
            genders = ["Not specified", "Male", "Female", "Other"]
            current_gender = child.get('gender', 'Not specified') or 'Not specified'
            gender = st.selectbox(
                "Gender",
                genders,
                index=genders.index(current_gender) if current_gender in genders else 0
            )
        
        col1, col2 = st.columns(2)
        with col1:
            blood_groups = ["Not specified", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            current_bg = child.get('blood_group', 'Not specified') or 'Not specified'
            blood_group = st.selectbox(
                "Blood Group",
                blood_groups,
                index=blood_groups.index(current_bg) if current_bg in blood_groups else 0
            )
        with col2:
            allergies = st.text_input("Known Allergies", value=child.get('allergies', '') or '')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Save Changes", type="primary", width='stretch'):
                db.update_child(
                    child['id'],
                    name=name,
                    date_of_birth=new_dob.isoformat(),
                    country_guideline=country,
                    gender=gender if gender != "Not specified" else None,
                    blood_group=blood_group if blood_group != "Not specified" else None,
                    allergies=allergies if allergies else None
                )
                st.session_state[f"edit_child_{child['id']}"] = False
                st.success("Profile updated!")
                st.rerun()
        with col2:
            if st.form_submit_button("Cancel", width='stretch'):
                st.session_state[f"edit_child_{child['id']}"] = False
                st.rerun()

def render_notification_settings():
    st.subheader("Notification Preferences")
    
    user_id = st.session_state.get('user_id')
    children = db.get_all_children(user_id=user_id)
    
    if not children:
        st.info("Add a child profile first to configure notifications.")
        return
    
    if 'selected_child_id' not in st.session_state or st.session_state.selected_child_id is None:
        st.session_state.selected_child_id = children[0]['id']
    
    child_options = {c['name']: c['id'] for c in children}
    selected_name = st.selectbox(
        "Select Child for Notification Settings",
        options=list(child_options.keys()),
        index=list(child_options.values()).index(st.session_state.selected_child_id) 
              if st.session_state.selected_child_id in child_options.values() else 0,
        key="notification_child_select"
    )
    child_id = child_options[selected_name]
    
    settings = db.get_reminder_settings(child_id) or {}
    
    with st.form(key="notification_settings_form"):
        st.markdown("### Email Notifications")
        
        email_enabled = st.checkbox(
            "Enable Email Reminders",
            value=bool(settings.get('email_enabled', False))
        )
        email_address = st.text_input(
            "Email Address",
            value=settings.get('email_address', ''),
            placeholder="your.email@example.com"
        )
        
        st.markdown("### Reminder Timing")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            reminder_7_days = st.checkbox(
                "7 days before",
                value=bool(settings.get('reminder_7_days', True))
            )
        with col2:
            reminder_1_day = st.checkbox(
                "1 day before",
                value=bool(settings.get('reminder_1_day', True))
            )
        with col3:
            reminder_on_day = st.checkbox(
                "On due date",
                value=bool(settings.get('reminder_on_day', True))
            )
        
        if st.form_submit_button("Save Notification Settings", type="primary"):
            db.save_reminder_settings(
                child_id=child_id,
                email_enabled=email_enabled,
                email_address=email_address,
                sms_enabled=False,
                phone_number="",
                reminder_7_days=reminder_7_days,
                reminder_1_day=reminder_1_day,
                reminder_on_day=reminder_on_day
            )
            st.success("Notification settings saved!")

def render_data_management():
    st.subheader("Data Management")
    
    st.markdown("### API Configuration")
    
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        st.success("OpenAI API Key is configured. AI Assistant is available.")
    else:
        st.warning("OpenAI API Key is not configured. Please add OPENAI_API_KEY to your secrets to enable the AI Assistant.")
    
    st.markdown("---")
    st.markdown("### Export Data")
    st.info("Data export functionality will be available in a future update.")
    
    st.markdown("---")
    st.markdown("### Database Information")
    
    user_id = st.session_state.get('user_id')
    children = db.get_all_children(user_id=user_id)
    total_vaccinations = 0
    total_events = 0
    
    for child in children:
        total_vaccinations += len(db.get_vaccinations(child['id']))
        total_events += len(db.get_health_events(child['id']))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Child Profiles", len(children))
    with col2:
        st.metric("Total Vaccinations", total_vaccinations)
    with col3:
        st.metric("Health Events", total_events)

def render_about():
    st.subheader("About Smart Child Vaccination & Health Assistant")
    
    st.markdown("""
    ### Overview
    
    Smart Child Vaccination & Health Assistant is a comprehensive application designed to help parents 
    track and manage their child's vaccination schedule and health history.
    
    ### Features
    
    - **Personalized Vaccination Scheduler**: Auto-generated schedules based on India (UIP) and WHO guidelines
    - **Health Timeline**: Track vaccinations, illnesses, symptoms, and doctor visits
    - **Smart Reminders**: Get notified about upcoming and overdue vaccines
    - **AI Assistant**: Natural language queries about your child's health and vaccinations
    - **Voice Input**: Hands-free interaction using voice commands
    
    ### Vaccination Guidelines
    
    This application supports two major vaccination guidelines:
    
    1. **India (UIP)**: Universal Immunization Programme - Government of India
    2. **WHO**: World Health Organization recommendations
    
    ### Technology Stack
    
    - **Frontend & Backend**: Streamlit (Python)
    - **Database**: SQLite
    - **AI/NLP**: OpenAI GPT-5 & Whisper
    - **Charts**: Plotly
    
    ### Privacy & Security
    
    - All data is stored locally in SQLite database
    - No personal data is shared with third parties
    - API keys are stored securely as environment secrets
    
    ### Medical Disclaimer
    
    This application is for informational and tracking purposes only. It is NOT a substitute for 
    professional medical advice, diagnosis, or treatment. Always consult your child's pediatrician 
    or healthcare provider for personalized medical guidance.
    
    ---
    
    **Version**: 1.0.0  
    **Last Updated**: December 2025
    
    ---
    
    *Designed to demonstrate real-world problem solving, data handling, and AI integration 
    suitable for MNC technical evaluations.*
    """)

def render_account():
    import user_database as udb
    
    st.markdown("""
    <style>
        /* Password input styling - consistent across all pages */
        [data-testid="stTextInput"] input {
            font-size: 1rem !important;
            padding: 14px 16px !important;
            border-radius: 12px !important;
            border: 2px solid #ddd !important;
            background-color: #f8f9fa !important;
            transition: all 0.3s ease !important;
            color: #1a1a1a !important;
        }
        [data-testid="stTextInput"] input::placeholder {
            color: #999 !important;
        }
        [data-testid="stTextInput"] input:focus {
            border-color: #667eea !important;
            background-color: #ffffff !important;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15) !important;
            outline: none !important;
        }
        [data-testid="stTextInput"] label {
            color: #000000 !important;
        }
        [data-testid="stTextInput"] label span {
            color: #000000 !important;
        }
        .stTextInput small {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h2 style="color: #1a1a1a; margin-top: 0; margin-bottom: 1rem; font-weight: 700;">Account Management</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #f0f7ff; border-left: 4px solid #667eea; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
        <h3 style="color: #667eea; margin-top: 0;">Account Information</h3>
        <p style="color: #333; margin: 0;">You are currently logged into your KinderCare account. Click the button below to securely logout.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🚪 Logout", key="settings_logout", width='stretch', type="secondary", help="Click to logout from your account"):
            st.session_state.logged_in = False
            st.session_state.current_page = "Home"
            st.session_state.conversation_history = []
            st.rerun()
    with col2:
        if st.button("🗑️ Delete Account", key="settings_delete", width='stretch', type="secondary", help="Permanently delete your account and all data"):
            st.session_state.show_delete_account = True
    
    if st.session_state.get('show_delete_account', False):
        st.markdown("---")
        st.markdown("""
        <div style="background: #ffebee; border-left: 4px solid #EF5350; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
            <h3 style="color: #C62828; margin-top: 0;">⚠️ Delete Account</h3>
            <p style="color: #333; margin: 0.5rem 0;"><strong>WARNING:</strong> This action is <strong>permanent and cannot be undone</strong>. Deleting your account will:</p>
            <ul style="color: #333; margin: 0.5rem 0;">
                <li>Remove all child profiles</li>
                <li>Delete all vaccination records</li>
                <li>Remove all health timeline data</li>
                <li>Clear all notification settings</li>
            </ul>
            <p style="color: #333; margin: 0.5rem 0;"><strong>Please ensure you have backed up any important data before proceeding.</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form(key="delete_account_form"):
            st.markdown("### Confirm Account Deletion")
            password = st.text_input("Enter your password to confirm deletion", type="password", placeholder="Your account password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Yes, Delete My Account", type="primary"):
                    user_email = st.session_state.get('user_email')
                    user_id = st.session_state.get('user_id')
                    
                    if not password:
                        st.error("Please enter your password to confirm deletion.")
                    else:
                        user = udb.authenticate_user(user_email, password)
                        if user and user['id'] == user_id:
                            udb.delete_user_account(user_id)
                            st.success("Account successfully deleted. Redirecting...")
                            import time
                            time.sleep(2)
                            st.session_state.logged_in = False
                            st.session_state.current_page = "Home"
                            st.session_state.conversation_history = []
                            st.rerun()
                        else:
                            st.error("Incorrect password. Account deletion cancelled.")
                            st.session_state.show_delete_account = False
            
            with col2:
                if st.form_submit_button("Cancel", type="secondary"):
                    st.session_state.show_delete_account = False
                    st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style="background: #fff3cd; border-left: 4px solid #ff9800; padding: 1.5rem; border-radius: 8px; margin-top: 2rem;">
        <h3 style="color: #e65100; margin-top: 0;">Security Tips</h3>
        <ul style="color: #333;">
            <li>Always logout from shared devices</li>
            <li>Keep your credentials confidential</li>
            <li>Regularly review your child profiles for accuracy</li>
            <li>Enable email notifications for important updates</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
