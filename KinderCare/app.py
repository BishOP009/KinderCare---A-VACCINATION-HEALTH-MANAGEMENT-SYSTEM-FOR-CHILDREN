import streamlit as st
import database as db
from PIL import Image
import base64
from io import BytesIO
import reminder_service
import user_database as udb

st.set_page_config(
    page_title="KinderCare - Child Health & Vaccination",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stAppViewContainer"] { background-color: #ffffff; }
    
    body {
        background-color: #ffffff;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    
    .stApp {
        background-color: #ffffff;
    }
    
    /* Main content */
    .main {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

db.init_database()

# Check and send reminders for logged-in users
if st.session_state.get('logged_in') and st.session_state.get('user_id'):
    reminder_service.check_and_send_reminders()

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'selected_child_id' not in st.session_state:
    user_id = st.session_state.get('user_id')
    children = db.get_all_children(user_id=user_id) if user_id else []
    st.session_state.selected_child_id = children[0]['id'] if children else None

if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

st.markdown("""
<style>
    .nav-button-active {
        border-bottom: 4px solid #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    nav_home, nav_diseases, nav_about, nav_login, nav_signup = st.columns([1, 1, 1, 1, 1])

    with nav_home:
        button_label = "🏠 Home" if st.session_state.current_page == "Home" else "Home"
        if st.button(button_label, key="nav_Home", width='stretch'):
            st.session_state.current_page = "Home"
            st.rerun()

    with nav_diseases:
        button_label = "🏥 Common Diseases" if st.session_state.current_page == "Common Diseases" else "Common Diseases"
        if st.button(button_label, key="nav_DR", width='stretch'):
            st.session_state.current_page = "Common Diseases"
            st.rerun()

    with nav_about:
        button_label = "ℹ️ About us" if st.session_state.current_page == "About us" else "About us"
        if st.button(button_label, key="nav_About", width='stretch'):
            st.session_state.current_page = "About us"
            st.rerun()

    with nav_login:
        button_label = "🔐 Login" if st.session_state.current_page == "Login" else "Login"
        if st.button(button_label, key="nav_Login", width='stretch'):
            st.session_state.current_page = "Login"
            st.rerun()

    with nav_signup:
        button_label = "✍️ Sign Up" if st.session_state.current_page == "Sign Up" else "Sign Up"
        if st.button(button_label, key="nav_SignUp", width='stretch'):
            st.session_state.current_page = "Sign Up"
            st.rerun()
else:
    nav_dashboard, nav_vax_sched, nav_vax_timeline, nav_health_timeline, nav_assistant, nav_settings = st.columns([1, 1, 1, 1, 1, 1])

    with nav_dashboard:
        button_label = "📊 Dashboard" if st.session_state.current_page == "Dashboard" else "Dashboard"
        if st.button(button_label, key="nav_Dashboard", width='stretch'):
            st.session_state.current_page = "Dashboard"
            st.rerun()

    with nav_vax_sched:
        button_label = "💉 Vaccination Schedule" if st.session_state.current_page == "Vaccination Schedule" else "Vaccination Schedule"
        if st.button(button_label, key="nav_VaxSched", width='stretch'):
            st.session_state.current_page = "Vaccination Schedule"
            st.rerun()

    with nav_vax_timeline:
        button_label = "📅 Vaccination Timeline" if st.session_state.current_page == "Vaccination Timeline" else "Vaccination Timeline"
        if st.button(button_label, key="nav_VaxTimeline", width='stretch'):
            st.session_state.current_page = "Vaccination Timeline"
            st.rerun()

    with nav_health_timeline:
        button_label = "❤️ Health Timeline" if st.session_state.current_page == "Health Timeline" else "Health Timeline"
        if st.button(button_label, key="nav_HealthTimeline", width='stretch'):
            st.session_state.current_page = "Health Timeline"
            st.rerun()

    with nav_assistant:
        button_label = "🤖 Assistant" if st.session_state.current_page == "Assistant" else "Assistant"
        if st.button(button_label, key="nav_Assistant", width='stretch'):
            st.session_state.current_page = "Assistant"
            st.rerun()

    with nav_settings:
        button_label = "⚙️ Settings" if st.session_state.current_page == "Settings" else "Settings"
        if st.button(button_label, key="nav_Settings", width='stretch'):
            st.session_state.current_page = "Settings"
            st.rerun()

st.markdown("""
<style>
    /* Global button text styling */
    button, [role="button"], .stButton button {
        color: white !important;
    }
    
    button span, [role="button"] span, .stButton button span,
    button p, [role="button"] p, .stButton button p,
    button div, [role="button"] div, .stButton button div {
        color: white !important;
    }
    
    [data-testid="stButton"] button {
        color: white !important;
        background-color: #667eea !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        padding: 0.5rem 1rem !important;
    }
    
    [data-testid="stButton"] button:hover {
        color: white !important;
        background-color: #764ba2 !important;
    }
    
    [data-testid="stButton"] button:active {
        background-color: #667eea !important;
    }
    
    [data-testid="stButton"] button:focus {
        background-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Form submit buttons */
    [data-testid="baseButton-primary"] span, [data-testid="baseButton-secondary"] span {
        color: white !important;
    }
    
    /* Get Started button styling */
    .get-started-button [data-testid="stButton"] button {
        border-radius: 50px !important;
        padding: 0.5rem 1.5rem !important;
        font-size: 0.95rem !important;
        width: auto !important;
    }
</style>
""", unsafe_allow_html=True)

if st.session_state.current_page == "Home":
    col_text, col_image = st.columns([1.2, 1])

    with col_text:
        st.markdown("""
<h1 style="font-size: 5rem; font-weight: 800; color: #667eea; margin: 8rem 0 0 0; text-align: left; padding: 0;">
    KinderCare
</h1>
<h2 style="font-size: 2.5rem; font-weight: 600; color: #333; margin: 0 0 0.5rem 0; text-align: left; padding: 0;">
    Your Child's Health & Vaccination<br>Companion
</h2>
<p style="font-size: 1.4rem; color: #666; text-align: left; margin: 0.5rem 0 2rem 0; padding: 0;">
    Track vaccinations, monitor health milestones, and connect with healthcare experts
</p>
""", unsafe_allow_html=True)
        
        st.markdown('<div class="get-started-button">', unsafe_allow_html=True)
        if st.button("Get Started", key="get_started_btn"):
            st.session_state.current_page = "Sign Up"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_image:
        # Load and encode image as base64 to avoid fullscreen icon
        try:
            img = Image.open("home_hero.jpg")
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            st.markdown(f'<img src="data:image/jpeg;base64,{img_str}" style="width: 100%; max-width: 500px;">', unsafe_allow_html=True)
        except:
            st.write("Image not found")

if st.session_state.current_page == "Home":
    from pages import home
    home.render()
elif st.session_state.current_page == "Common Diseases":
    from pages import diseases_remedies
    diseases_remedies.render()
elif st.session_state.current_page == "About us":
    from pages import about_us
    about_us.render()
elif st.session_state.current_page == "Dashboard":
    from pages import dashboard
    dashboard.render()
elif st.session_state.current_page == "Vaccination Schedule":
    from pages import vaccination_schedule
    vaccination_schedule.render()
elif st.session_state.current_page == "Vaccination Timeline":
    from pages import vaccination_timeline
    vaccination_timeline.render()
elif st.session_state.current_page == "Health Timeline":
    from pages import health_timeline
    health_timeline.render()
elif st.session_state.current_page == "Assistant":
    from pages import assistant
    assistant.render()
elif st.session_state.current_page == "Settings":
    from pages import settings
    settings.render()
elif st.session_state.current_page == "Login":
    from pages import login
    login.render()
elif st.session_state.current_page == "Sign Up":
    from pages import signup
    signup.render()
