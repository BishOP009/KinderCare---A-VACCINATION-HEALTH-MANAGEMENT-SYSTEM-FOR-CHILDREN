import streamlit as st

def render():
    st.markdown('<h1 style="color: #667eea; margin-top: 0;">ℹ️ About Us</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #f9f9f9; padding: 2rem; border-radius: 8px; margin-bottom: 2rem;">
        <h3 style="color: #667eea; margin-top: 0;">Welcome to KinderCare</h3>
        <p style="color: #333; line-height: 1.8;">
            KinderCare is a comprehensive child health and vaccination management platform designed to help parents and caregivers track their children's vaccinations and health records with ease. Our mission is to make child healthcare management simple, accessible, and stress-free for every family.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #f9f9f9; padding: 2rem; border-radius: 8px; margin-bottom: 2rem;">
        <h3 style="color: #667eea; margin-top: 0;">Our Mission</h3>
        <p style="color: #333; line-height: 1.8;">
            We believe that every child deserves the best healthcare. KinderCare empowers parents with the tools and information they need to manage their child's health effectively. From vaccination schedules to health records and AI-powered health guidance, we're here to support your child's wellbeing every step of the way.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #f9f9f9; padding: 2rem; border-radius: 8px; margin-bottom: 2rem;">
        <h3 style="color: #667eea; margin-top: 0;">Key Features</h3>
        <ul style="color: #333; line-height: 1.8;">
            <li><strong>Vaccination Tracking:</strong> Never miss a vaccine with our intelligent scheduling system</li>
            <li><strong>Health Records:</strong> Maintain comprehensive health records for your children</li>
            <li><strong>AI Health Assistant:</strong> Get instant answers to your health and vaccination questions</li>
            <li><strong>Disease Information:</strong> Learn about common childhood illnesses and remedies</li>
            <li><strong>Multiple Standards:</strong> Support for India UIP, WHO, and other vaccination guidelines</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #f9f9f9; padding: 2rem; border-radius: 8px;">
        <h3 style="color: #667eea; margin-top: 0;">Contact & Support</h3>
        <p style="color: #333; line-height: 1.8;">
            For questions, feedback, or support, please reach out to us. We're committed to providing the best service to help you care for your child's health.
        </p>
    </div>
    """, unsafe_allow_html=True)
