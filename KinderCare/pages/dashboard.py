import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import database as db
from vaccination_guidelines import categorize_vaccinations, get_age_string
from notifications import get_in_app_notifications
import pandas as pd


def render():
    st.markdown("""
    <style>
        .category-card {
            height: 140px;
            padding: 1.5rem;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 style="color: #667eea; margin-top: 0;">Dashboard</h1>', unsafe_allow_html=True)

    user_id = st.session_state.get('user_id')
    children = db.get_all_children(user_id=user_id) if user_id else []

    if not children:
        st.info("Welcome! Please add a child profile in the Settings page to get started.")
        return

    if 'selected_child_id' not in st.session_state or st.session_state.selected_child_id is None:
        st.session_state.selected_child_id = children[0]['id']

    child_options = {c['name']: c['id'] for c in children}
    selected_name = st.selectbox(
        "Select Child",
        options=list(child_options.keys()),
        index=list(child_options.values()).index(st.session_state.selected_child_id)
        if st.session_state.selected_child_id in child_options.values() else 0
    )
    st.session_state.selected_child_id = child_options[selected_name]

    child = db.get_child(st.session_state.selected_child_id)
    vaccinations = db.get_vaccinations(st.session_state.selected_child_id)

    notifications = get_in_app_notifications(st.session_state.selected_child_id)
    if notifications:
        st.markdown('<h2 style="color: #667eea; margin-bottom: 1rem; font-weight: 700;">🔔 Notifications</h2>', unsafe_allow_html=True)
        for notif in notifications:
            if notif['type'] == 'error':
                st.error(f"**{notif['title']}**: {notif['message']}")
            elif notif['type'] == 'warning':
                st.warning(f"**{notif['title']}**: {notif['message']}")
            else:
                st.info(f"**{notif['title']}**: {notif['message']}")

    st.markdown("---")

    dob = child['date_of_birth']
    if isinstance(dob, str):
        dob = date.fromisoformat(dob)
    age = get_age_string(dob)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg,#667eea,#764ba2);
                    padding:20px;border-radius:10px;color:white;">
            <h3 style="margin:0;">Child Profile</h3>
            <p style="font-size:24px;font-weight:bold;margin:10px 0;">{child['name']}</p>
            <p style="margin:0;">Age: {age}</p>
        </div>
        """, unsafe_allow_html=True)

    categories = categorize_vaccinations(vaccinations)

    with col2:
        total = len(vaccinations)
        completed = len(categories['completed'])
        progress = (completed / total * 100) if total > 0 else 0
        st.markdown(f"""
        <div style="background: linear-gradient(135deg,#11998e,#38ef7d);
                    padding:20px;border-radius:10px;color:white;">
            <h3 style="margin:0;">Vaccination Progress</h3>
            <p style="font-size:24px;font-weight:bold;margin:10px 0;">{completed}/{total}</p>
            <p style="margin:0;">Completed: {progress:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        upcoming = len(categories['upcoming'])
        st.markdown(f"""
        <div style="background: linear-gradient(135deg,#ff9a56,#ff6a88);
                    padding:20px;border-radius:10px;color:white;">
            <h3 style="margin:0;">Upcoming Vaccines</h3>
            <p style="font-size:24px;font-weight:bold;margin:10px 0;">{upcoming}</p>
            <p style="margin:0;">Pending</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<h2 style="color:#667eea;margin-top:2rem;">💉 Vaccination Categories</h2>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="category-card" style="background:#E8F5E9;border-left:4px solid #81C784;">
            <h4 style="color:#2E7D32;margin-bottom:8px;">✓ Completed</h4>
            <p style="font-size:1.6rem;font-weight:bold;color:#81C784;margin:0;">
                {len(categories['completed'])}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="category-card" style="background:#E3F2FD;border-left:4px solid #64B5F6;">
            <h4 style="color:#1565C0;margin-bottom:8px;">➜ Upcoming</h4>
            <p style="font-size:1.6rem;font-weight:bold;color:#64B5F6;margin:0;">
                {len(categories['upcoming'])}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="category-card" style="background:#FFEBEE;border-left:4px solid #EF5350;">
            <h4 style="color:#C62828;margin-bottom:8px;">⚠️ Overdue</h4>
            <p style="font-size:1.6rem;font-weight:bold;color:#EF5350;margin:0;">
                {len(categories['overdue'])}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="category-card" style="background:#FFF3E0;border-left:4px solid #FFB74D;">
            <h4 style="color:#E65100;margin-bottom:8px;">⏳ Pending</h4>
            <p style="font-size:1.6rem;font-weight:bold;color:#FFB74D;margin:0;">
                {len(categories['pending'])}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<h2 style="color:#667eea;margin-top:2rem;">📊 Vaccination Analytics</h2>', unsafe_allow_html=True)

    if vaccinations:
        status_colors = {
            'completed': '#81C784',
            'upcoming': '#64B5F6',
            'overdue': '#EF5350',
            'pending': '#FFB74D'
        }
        
        status_counts = {
            'completed': len(categories['completed']),
            'upcoming': len(categories['upcoming']),
            'overdue': len(categories['overdue']),
            'pending': len(categories['pending'])
        }
        
        anal_col1, anal_col2 = st.columns(2)
        
        with anal_col1:
            st.markdown('<h3 style="color: #667eea; font-size: 1.2rem;">Vaccination Status Distribution</h3>', unsafe_allow_html=True)
            
            colors = [status_colors.get(status, '#999') for status in status_counts.keys()]
            
            fig_status = go.Figure(data=[go.Pie(
                labels=[s.capitalize() for s in status_counts.keys()],
                values=list(status_counts.values()),
                marker=dict(colors=colors),
                hole=0.3,
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
            )])
            fig_status.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                font=dict(size=11)
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with anal_col2:
            st.markdown('<h3 style="color: #667eea; font-size: 1.2rem;">Vaccination Status Count</h3>', unsafe_allow_html=True)
            
            colors = [status_colors.get(status, '#999') for status in status_counts.keys()]
            
            fig_bar = go.Figure(data=[go.Bar(
                x=[s.capitalize() for s in status_counts.keys()],
                y=list(status_counts.values()),
                marker=dict(color=colors),
                text=list(status_counts.values()),
                textposition='auto',
                hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
            )])
            fig_bar.update_layout(
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis_title='Status',
                yaxis_title='Number of Vaccines',
                showlegend=False,
                font=dict(size=11)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown('<h3 style="color: #667eea; font-size: 1.2rem;">📅 Vaccination Timeline by Status</h3>', unsafe_allow_html=True)
        
        timeline_data = []
        for category_name, vax_list in categories.items():
            for vax in vax_list:
                due = vax.get('due_date')
                if due and (isinstance(due, str) or isinstance(due, date)):
                    if isinstance(due, str):
                        try:
                            due = datetime.fromisoformat(due).date()
                        except:
                            continue
                    timeline_data.append({
                        'vaccine': vax['vaccine_name'],
                        'due_date': due,
                        'status': category_name.capitalize()
                    })
        
        if timeline_data:
            timeline_df = pd.DataFrame(timeline_data).sort_values('due_date')
            status_map = {'Completed': 0, 'Upcoming': 1, 'Overdue': 2, 'Pending': 3}
            timeline_df['status_order'] = timeline_df['status'].map(status_map)
            
            fig_timeline = px.scatter(
                timeline_df,
                x='due_date',
                y='status_order',
                color='status',
                size_max=12,
                hover_name='vaccine',
                hover_data={'due_date': True, 'status': True, 'status_order': False},
                color_discrete_map={
                    'Completed': '#81C784',
                    'Upcoming': '#64B5F6',
                    'Overdue': '#EF5350',
                    'Pending': '#FFB74D'
                },
                title=None
            )
            fig_timeline.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=0, b=0),
                yaxis=dict(
                    tickvals=[0, 1, 2, 3],
                    ticktext=['Completed', 'Upcoming', 'Overdue', 'Pending'],
                    title='Status'
                ),
                xaxis_title='Date',
                showlegend=True,
                hovermode='closest',
                font=dict(size=11),
                plot_bgcolor='rgba(240, 240, 240, 0.5)'
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        st.markdown("---")
        
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            compliance_rate = (len(categories['completed']) / total * 100) if total > 0 else 0
            st.metric("Compliance Rate", f"{compliance_rate:.0f}%", 
                     f"{len(categories['completed'])}/{total}")
        
        with metric_col2:
            overdue_count = len(categories['overdue'])
            st.metric("Overdue Vaccines", overdue_count, 
                     "⚠️ Need attention" if overdue_count > 0 else "All on track")
        
        with metric_col3:
            age_months = int((date.today() - dob).days / 30.44)
            st.metric("Age", f"{age_months} months", f"Born: {dob.strftime('%b %Y')}")
        
        with metric_col4:
            if categories['upcoming']:
                next_vax = min(categories['upcoming'], 
                             key=lambda x: datetime.fromisoformat(x['due_date']).date() 
                             if isinstance(x['due_date'], str) else x['due_date'])
                due_date = next_vax['due_date']
                if isinstance(due_date, str):
                    due_date = datetime.fromisoformat(due_date).date()
                days_until = (due_date - date.today()).days
                st.metric("Next Vaccine Due", f"{days_until} days", 
                         next_vax['vaccine_name'][:20])
            else:
                st.metric("Next Vaccine Due", "None", "All scheduled vaccines done")
        
        st.markdown("---")
        
        st.markdown('<h2 style="color:#667eea;margin-top:2rem;">📋 Vaccination Details by Category</h2>', unsafe_allow_html=True)
        
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.markdown('<h3 style="color: #81C784;">✓ Completed Vaccinations</h3>', unsafe_allow_html=True)
            
            if categories['completed']:
                completed_df = pd.DataFrame(categories['completed']).sort_values('due_date')
                completed_df['due_date'] = pd.to_datetime(completed_df['due_date']).dt.strftime('%Y-%m-%d')
                completed_df_display = completed_df[['vaccine_name', 'due_date', 'status']].rename(
                    columns={'vaccine_name': 'Vaccine', 'due_date': 'Date', 'status': 'Status'}
                )
                st.dataframe(completed_df_display, use_container_width=True, hide_index=True)
            else:
                st.info("No completed vaccines yet.")
        
        with detail_col2:
            st.markdown('<h3 style="color: #64B5F6;">➜ Upcoming Vaccinations</h3>', unsafe_allow_html=True)
            
            if categories['upcoming']:
                upcoming_df = pd.DataFrame(categories['upcoming']).sort_values('due_date')
                upcoming_df['due_date'] = pd.to_datetime(upcoming_df['due_date']).dt.strftime('%Y-%m-%d')
                upcoming_df_display = upcoming_df[['vaccine_name', 'due_date', 'status']].rename(
                    columns={'vaccine_name': 'Vaccine', 'due_date': 'Date', 'status': 'Status'}
                )
                st.dataframe(upcoming_df_display, use_container_width=True, hide_index=True)
            else:
                st.info("No upcoming vaccines.")
        
        detail_col3, detail_col4 = st.columns(2)
        
        with detail_col3:
            st.markdown('<h3 style="color: #EF5350;">⚠️ Overdue Vaccinations</h3>', unsafe_allow_html=True)
            
            if categories['overdue']:
                overdue_df = pd.DataFrame(categories['overdue']).sort_values('due_date')
                overdue_df['due_date'] = pd.to_datetime(overdue_df['due_date']).dt.strftime('%Y-%m-%d')
                overdue_df_display = overdue_df[['vaccine_name', 'due_date', 'status']].rename(
                    columns={'vaccine_name': 'Vaccine', 'due_date': 'Date', 'status': 'Status'}
                )
                st.dataframe(overdue_df_display, use_container_width=True, hide_index=True)
            else:
                st.info("No overdue vaccines.")
        
        with detail_col4:
            st.markdown('<h3 style="color: #FFB74D;">⏳ Pending Vaccinations</h3>', unsafe_allow_html=True)
            
            if categories['pending']:
                pending_df = pd.DataFrame(categories['pending']).sort_values('due_date')
                pending_df['due_date'] = pd.to_datetime(pending_df['due_date']).dt.strftime('%Y-%m-%d')
                pending_df_display = pending_df[['vaccine_name', 'due_date', 'status']].rename(
                    columns={'vaccine_name': 'Vaccine', 'due_date': 'Date', 'status': 'Status'}
                )
                st.dataframe(pending_df_display, use_container_width=True, hide_index=True)
            else:
                st.info("No pending vaccines.")
    else:
        st.info("No vaccination records yet. Start adding vaccinations to see analytics.")
