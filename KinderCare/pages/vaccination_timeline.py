import streamlit as st
import json

def load_vaccine_data():
    """Load vaccine data from JSON files"""
    data = {
        "India (UIP)": None,
        "WHO": None
    }
    
    try:
        with open("data/vaccines_uip_india.json", "r") as f:
            data["India (UIP)"] = json.load(f)
    except FileNotFoundError:
        pass
    
    try:
        with open("data/vaccines_who.json", "r") as f:
            data["WHO"] = json.load(f)
    except FileNotFoundError:
        pass
    
    return data

def render():
    st.markdown("""
    <style>
        h2, h3 {
            color: #1a1a1a !important;
        }
        p {
            color: #000 !important;
        }
        [data-testid="stExpander"] details > summary {
            color: #000 !important;
        }
        [data-testid="stExpander"] details > summary svg {
            stroke: #000 !important;
        }
        [data-testid="stExpander"] button svg {
            stroke: #000 !important;
        }
        
        /* Vaccination Timeline Boxes - Ensure white text visibility */
        .vaccine-stat-box p {
            color: white !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
        }
        
        .vaccine-stat-box {
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="color: #667eea; margin-top: 0;">📈 Vaccination Timeline</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #000; margin-bottom: 1.5rem;">A visual guide showing when your child needs each vaccine.</p>', unsafe_allow_html=True)
    
    vaccine_data = load_vaccine_data()
    
    guideline = st.selectbox(
        "Select Vaccination Guideline",
        ["India (UIP)", "WHO"],
        help="Choose the vaccination guideline to view the recommended schedule"
    )
    
    if guideline not in vaccine_data or vaccine_data[guideline] is None:
        st.error(f"⚠️ Vaccine data for {guideline} is not available")
        return
    
    data = vaccine_data[guideline]
    
    st.info(f"""
    **{data.get('name', guideline)}**  
    Source: {data.get('source', 'Unknown')}
    """)
    
    st.markdown("---")
    
    vaccines = data.get('vaccines', [])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="vaccine-stat-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; text-align: center;">
            <p style="margin: 0; font-size: 18px; color: white !important; font-weight: 600; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">Total Vaccines</p>
            <p style="margin: 10px 0 0 0; font-size: 40px; font-weight: 900; color: white !important; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">{len(vaccines)}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        age_groups = set([v['age_label'] for v in vaccines])
        st.markdown(f"""
        <div class="vaccine-stat-box" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 10px; text-align: center;">
            <p style="margin: 0; font-size: 18px; color: white !important; font-weight: 600; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">Age Groups</p>
            <p style="margin: 10px 0 0 0; font-size: 40px; font-weight: 900; color: white !important; text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);">{len(age_groups)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<h2 style="color: #1a1a1a; margin-top: 2rem; margin-bottom: 1rem; font-weight: 700;">📅 Vaccination Schedule by Age</h2>', unsafe_allow_html=True)
    
    age_groups = {}
    for vaccine in vaccines:
        age_label = vaccine['age_label']
        if age_label not in age_groups:
            age_groups[age_label] = {
                'weeks': vaccine['age_weeks'],
                'vaccines': []
            }
        age_groups[age_label]['vaccines'].append(vaccine)
    
    sorted_groups = sorted(age_groups.items(), key=lambda x: x[1]['weeks'])
    
    for age_label, group_data in sorted_groups:
        vaccines_in_group = group_data['vaccines']
        vaccine_count = len(vaccines_in_group)
        vaccine_text = "vaccine" if vaccine_count == 1 else "vaccines"
        
        with st.expander(f"**{age_label}** — {vaccine_count} {vaccine_text} 💉", expanded=False):
            for vaccine in vaccines_in_group:
                doses_text = f"({vaccine['doses']} dose{'s' if vaccine['doses'] > 1 else ''})"
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin-bottom: 12px; color: white;">
                    <div style="font-weight: 700; font-size: 15px; margin-bottom: 5px;">
                        {vaccine['name']}
                    </div>
                    <div style="font-size: 13px; opacity: 0.9; margin-bottom: 5px;">
                        {vaccine['full_name']} {doses_text}
                    </div>
                    <div style="font-size: 12px; opacity: 0.85;">
                        📝 {vaccine['description']}
                    </div>
                    <div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">
                        ℹ️ {vaccine['notes']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div class="info-box" style="background: #f0f7ff; border-left: 4px solid #667eea; padding: 1.5rem; border-radius: 8px;">
        <h3 style="color: #667eea; margin: 0 0 0.5rem 0;">💡 Important</h3>
        <p style="color: #333; margin: 0;">This timeline shows the standard recommended vaccination schedule. Always consult your pediatrician for advice specific to your child's health needs. Some vaccines may need to be adjusted based on your child's medical history.</p>
    </div>
    """, unsafe_allow_html=True)
