import streamlit as st
from datetime import date, datetime
import plotly.graph_objects as go
import database as db
from vaccination_guidelines import get_age_string

def render():
    st.markdown("""
    <style>
        h2, h3 {
            color: #1a1a1a !important;
        }
        p {
            color: #000 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="color: #667eea; margin-top: 0;">📅 Health Timeline</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #000; margin-bottom: 1.5rem;">Track your child\'s health events, vaccinations, and important milestones</p>', unsafe_allow_html=True)
    
    user_id = st.session_state.get('user_id')
    children = db.get_all_children(user_id=user_id) if user_id else []
    
    if not children:
        st.info("Please add a child profile first.")
        return
    
    if 'selected_child_id' not in st.session_state or st.session_state.selected_child_id is None:
        st.session_state.selected_child_id = children[0]['id']
    
    child_options = {c['name']: c['id'] for c in children}
    selected_name = st.selectbox(
        "Select Child",
        options=list(child_options.keys()),
        index=list(child_options.values()).index(st.session_state.selected_child_id) 
              if st.session_state.selected_child_id in child_options.values() else 0,
        key="timeline_child_select"
    )
    st.session_state.selected_child_id = child_options[selected_name]
    
    child = db.get_child(st.session_state.selected_child_id)
    vaccinations = db.get_vaccinations(st.session_state.selected_child_id)
    health_events = db.get_health_events(st.session_state.selected_child_id)
    
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Add Health Event", type="primary", width='stretch'):
            st.session_state.show_add_event = True
    
    if st.session_state.get('show_add_event', False):
        render_add_event_form(st.session_state.selected_child_id)
    
    filter_options = ["All", "Vaccines", "Illness", "Symptom", "Doctor Visit"]
    selected_filter = st.selectbox("Filter by Category", filter_options)
    
    st.markdown("---")
    
    timeline_items = []
    
    completed_vaccines = [v for v in vaccinations if v['status'] == 'completed']
    for vacc in completed_vaccines:
        administered_date = vacc.get('administered_date')
        if administered_date:
            if isinstance(administered_date, str):
                administered_date = date.fromisoformat(administered_date)
            timeline_items.append({
                'date': administered_date,
                'type': 'Vaccines',
                'title': f"Vaccine: {vacc['vaccine_name']}",
                'description': vacc.get('notes', ''),
                'icon': '💉',
                'color': '#4caf50'
            })
    
    for event in health_events:
        event_date = event['event_date']
        if isinstance(event_date, str):
            event_date = date.fromisoformat(event_date)
        
        event_type = event['event_type']
        icon_map = {
            'illness': '🤒',
            'symptom': '🌡️',
            'doctor_visit': '👨‍⚕️',
            'milestone': '🎯',
            'other': '📝'
        }
        
        timeline_items.append({
            'date': event_date,
            'type': event_type.title(),
            'title': event['title'],
            'description': event.get('description', ''),
            'icon': icon_map.get(event_type, '📝'),
            'color': '#667eea'
        })
    
    if selected_filter != "All":
        timeline_items = [item for item in timeline_items if item['type'] == selected_filter]
    
    timeline_items.sort(key=lambda x: x['date'], reverse=True)
    
    if not timeline_items:
        st.info("No health events recorded yet. Click 'Add Health Event' to get started!")
    else:
        for idx, item in enumerate(timeline_items):
            date_str = item['date'].strftime('%B %d, %Y')
            
            # Find the event ID for deletion (only for health events, not vaccines)
            event_id = None
            if item['type'] != 'Vaccines':
                for event in health_events:
                    if event['title'] == item['title'] and event['event_date'] == item['date'].isoformat():
                        event_id = event['id']
                        break
            
            col1, col2 = st.columns([0.95, 0.05])
            
            with col1:
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid {item['color']}; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
                        <span style="font-size: 1.5rem;">{item['icon']}</span>
                        <div>
                            <div style="font-weight: 700; color: #333;">{item['title']}</div>
                            <div style="font-size: 0.85rem; color: #999;">{date_str}</div>
                        </div>
                    </div>
                    {f'<div style="color: #666; font-size: 0.9rem; margin-left: 34px;">{item["description"]}</div>' if item['description'] else ''}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if event_id and st.button("🗑️", key=f"delete_event_{event_id}", help="Delete this event"):
                    st.session_state[f"confirm_delete_event_{event_id}"] = True
            
            # Show delete confirmation
            if event_id and st.session_state.get(f"confirm_delete_event_{event_id}", False):
                st.warning("Are you sure you want to delete this event?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Delete", key=f"confirm_delete_yes_{event_id}"):
                        db.delete_health_event(event_id)
                        st.success("Event deleted!")
                        st.session_state[f"confirm_delete_event_{event_id}"] = False
                        st.rerun()
                with col2:
                    if st.button("Cancel", key=f"confirm_delete_no_{event_id}"):
                        st.session_state[f"confirm_delete_event_{event_id}"] = False
                        st.rerun()

def render_add_event_form(child_id):
    st.markdown('<h2 style="color: #1a1a1a; margin-top: 0; margin-bottom: 1rem; font-weight: 700;">➕ Add New Health Event</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        event_date = st.date_input("Event Date", value=date.today())
    with col2:
        event_type = st.selectbox(
            "Event Type",
            ["illness", "symptom", "doctor_visit", "milestone", "other"],
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    title = st.text_input("Event Title", placeholder="e.g., High fever, Doctor checkup")
    description = st.text_area("Description", placeholder="Additional details about the event...")
    
    if st.button("Save Event", type="primary"):
        if title:
            db.add_health_event(
                child_id=child_id,
                event_type=event_type,
                event_date=event_date.isoformat(),
                title=title,
                description=description
            )
            st.success("✅ Health event recorded!")
            st.session_state.show_add_event = False
            st.rerun()
        else:
            st.error("Please enter an event title")
