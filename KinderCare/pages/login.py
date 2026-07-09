import streamlit as st
import re
import user_database as udb

def render():
    st.markdown("""
    <style>
        /* Improve text input styling */
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
        /* Improve checkbox styling */
        [data-testid="stCheckbox"] {
            color: #000000 !important;
        }
        [data-testid="stCheckbox"] label {
            color: #000000 !important;
        }
        [data-testid="stCheckbox"] span {
            color: #000000 !important;
        }
        [data-testid="stCheckbox"] * {
            color: #000000 !important;
        }
        /* Style buttons */
        [data-testid="baseButton-primary"] {
            font-weight: 600 !important;
            font-size: 1.05em !important;
            border-radius: 12px !important;
        }
        [data-testid="baseButton-secondary"] {
            font-weight: 600 !important;
            font-size: 1.05em !important;
            border-radius: 12px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 3rem; margin-top: 2rem;">
            <h1 style="color: #667eea; font-size: 2.5rem; margin: 0; font-weight: 900;">Welcome Back</h1>
            <p style="color: #1a1a1a; margin-top: 0.75rem; font-size: 1.1rem; font-weight: 500;">Sign in to your KinderCare account</p>
        </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("📧 Email Address", placeholder="your@email.com", key="login_email")
        password = st.text_input("🔐 Password", type="password", placeholder="Enter your password", key="login_password")
        
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        col_remember, col_forgot = st.columns([1, 1])
        with col_remember:
            st.checkbox("Remember me", key="remember_login", value=False)
        with col_forgot:
            st.markdown('<p style="text-align: right; color: #667eea; cursor: pointer; margin: 0; font-weight: 500;">🔗 Forgot Password?</p>', unsafe_allow_html=True)
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        if st.button("🔓 Login", key="login_btn", width='stretch', type="primary"):
            email = email.strip()
            password = password.strip()
            if not email or not password:
                st.error("❌ Please enter both email and password")
            elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                st.error("❌ Please enter a valid email address")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters long")
            else:
                try:
                    user = udb.authenticate_user(email.lower(), password)
                    if user:
                        st.success("✅ Login successful!")
                        st.session_state.logged_in = True
                        st.session_state.user_id = user['id']
                        st.session_state.user_name = user['name']
                        st.session_state.user_email = user['email']
                        st.session_state.current_page = "Dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")
                except Exception as e:
                    st.error(f"❌ Error during login: {str(e)}")
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown('<hr style="border: none; border-top: 1px solid #ddd; margin: 1rem 0;">', unsafe_allow_html=True)
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        col_text, col_btn = st.columns([2, 1])
        with col_text:
            st.markdown('<p style="color: #1a1a1a; margin: 0; font-weight: 500;">Don\'t have an account?</p>', unsafe_allow_html=True)
        with col_btn:
            if st.button("Sign Up", key="switch_to_signup", width='stretch', type="secondary"):
                st.session_state.current_page = "Sign Up"
                st.rerun()
