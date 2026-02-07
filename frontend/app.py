"""
ScholarPulse - AI Research Agent (Premium SaaS Redesign)

This is the main Streamlit application that communicates with the Django backend
via REST APIs for all research operations.
"""
import streamlit as st
import os
import sys
import time
import datetime
import textwrap

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import ScholarPulseAPI, APIException
from components.feedback import (
    get_feedback_styles,
    render_success_card,
    render_warning_card,
    render_error_card,
    render_connection_error,
    render_progress_card,
    _sanitize
)
from components.cards import render_papers_grid, render_ideas_list, render_paper_card, render_idea_card
from styles.theme import get_theme_css, get_color_scheme

# Page Config
st.set_page_config(
    page_title="ScholarPulse | AI Research Agent",
    page_icon="🧠",
    layout="wide",
)

# Initialize API client
API_BASE_URL = os.environ.get('SCHOLARPULSE_API_URL', 'http://localhost:8000')
api = ScholarPulseAPI(base_url=API_BASE_URL)

# Session State Initialization
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
if 'history' not in st.session_state:
    st.session_state.history = []
if 'papers_found' not in st.session_state:
    st.session_state.papers_found = 0
if 'searches_made' not in st.session_state:
    st.session_state.searches_made = 0
if 'reports_generated' not in st.session_state:
    st.session_state.reports_generated = 0
if 'session_start' not in st.session_state:
    st.session_state.session_start = time.time()
if 'backend_healthy' not in st.session_state:
    st.session_state.backend_healthy = False
if 'selected_task_id' not in st.session_state:
    st.session_state.selected_task_id = None
if 'settings_tab' not in st.session_state:
    st.session_state.settings_tab = "General"

def sync_kpis():
    """Fetch live stats from backend and update session state."""
    if st.session_state.get('backend_healthy', False):
        try:
            stats = api.get_stats()
            st.session_state.papers_found = stats.get('total_papers', 0)
            st.session_state.searches_made = stats.get('total_searches', 0)
            st.session_state.reports_generated = stats.get('total_reports', 0)
        except:
            pass

# Check backend health periodically
try:
    st.session_state.backend_healthy = api.health_check()
    if st.session_state.backend_healthy:
        sync_kpis()
except:
    st.session_state.backend_healthy = False

# Apply Premium Theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)
st.markdown(get_feedback_styles(st.session_state.theme), unsafe_allow_html=True)
colors = get_color_scheme(st.session_state.theme)

# Helper for sidebar navigation
def nav_page(page_name):
    st.session_state.page = page_name
    st.session_state.selected_task_id = None
    st.rerun()

# --- SIDEBAR IMPLEMENTATION ---
with st.sidebar:
    branding_html = f"""
<div class="sidebar-logo-container">
<div style="width: 56px; height: 56px; border-radius: 16px; background: linear-gradient(135deg, #6366F1, #8B5CF6); display: flex; align-items: center; justify-content: center; font-size: 1.6rem; box-shadow: 0 8px 16px rgba(99, 102, 241, 0.3);">🧠</div>
<div style="text-align: center;">
<div style="font-weight: 700; font-size: 1.2rem; color: {colors['text']}; letter-spacing: -0.5px;">ScholarPulse</div>
<div style="font-size: 0.75rem; color: {colors['muted']}; font-weight: 500; text-transform: uppercase; letter-spacing: 1px;">AI Research Agent</div>
</div>
</div>
"""
    st.markdown(branding_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation
    if st.button("📂 Dashboard", use_container_width=True, type="secondary" if st.session_state.page != "Dashboard" else "primary"):
        nav_page("Dashboard")
    if st.button("📑 My Library", use_container_width=True, type="secondary" if st.session_state.page != "Library" else "primary"):
        nav_page("Library")
    if st.button("⚙️ Settings", use_container_width=True, type="secondary" if st.session_state.page != "Settings" else "primary"):
        nav_page("Settings")
    
    st.markdown("<div class='stDivider'></div>", unsafe_allow_html=True)
    
    if st.session_state.page == "Dashboard":
        st.markdown(f"<p style='font-weight: 600; color: {colors['text']}; margin: 0 16px 12px 0px; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.7;'>🛠️ Configuration</p>", unsafe_allow_html=True)
        provider = st.selectbox("Intelligence", ["Groq", "Oxlo", "Gemini"], index=0)
        mode_val = st.selectbox("Research Mode", ["Deep Research", "Web Search", "Study & Learn"], index=0)
        year_val = st.number_input("Year Filter", min_value=0, max_value=2030, value=2024)
    else:
        st.markdown(f"<p style='font-size: 0.85rem; color: {colors['muted']}; opacity: 0.6;'>Navigating to {st.session_state.page}...</p>", unsafe_allow_html=True)

    # Session Info at the bottom
    st.sidebar.markdown("<div style='position: fixed; bottom: 20px; width: 260px;'>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='font-size: 0.7rem; color: {colors['muted']}; text-align: center;'>Status: {('Online' if st.session_state.backend_healthy else 'Offline')}</p>", unsafe_allow_html=True)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# --- PAGE ROUTING ---

def render_dashboard():
    # Modern Navbar
    status_class = "" if st.session_state.backend_healthy else "offline"
    status_text = "Connected" if st.session_state.backend_healthy else "Disconnected"
    
    navbar_html = f"""
<div class="top-navbar">
<a class="top-navbar-brand gradient-text" href="#" style="font-size: 1.3rem;">ScholarPulse</a>
<div class="navbar-status">
<div class="status-dot {status_class}"></div>
<span style="font-weight: 500;">Backend: {status_text}</span>
</div>
</div>
"""
    st.markdown(navbar_html, unsafe_allow_html=True)
    
    # Wrapper for main content
    st.markdown("<div class='content-section'>", unsafe_allow_html=True)
    
    # Welcome Header
    st.markdown(f"<h1 style='margin-bottom: 8px; font-weight: 800; font-size: 2.4rem; color: {colors['text']};'>Welcome back</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {colors['muted']}; margin-bottom: 36px; font-size: 1.15rem; font-weight: 400;'>How can I accelerate your research today?</p>", unsafe_allow_html=True)

    # KPI Row
    elapsed_sec = int(time.time() - st.session_state.session_start)
    uptime_str = f"{elapsed_sec // 60}m {elapsed_sec % 60}s"
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
<div class="premium-card">
<div style="font-size: 1.4rem;">📄</div>
<div style="font-size: 0.72rem; color: {colors['muted']}; text-transform: uppercase; font-weight: 700; margin-top: 8px;">Papers Found</div>
<div style="font-size: 1.6rem; font-weight: 700;">{st.session_state.papers_found}</div>
</div>""", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
<div class="premium-card">
<div style="font-size: 1.4rem;">🔍</div>
<div style="font-size: 0.72rem; color: {colors['muted']}; text-transform: uppercase; font-weight: 700; margin-top: 8px;">Searches</div>
<div style="font-size: 1.6rem; font-weight: 700;">{st.session_state.searches_made}</div>
</div>""", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
<div class="premium-card">
<div style="font-size: 1.4rem;">📊</div>
<div style="font-size: 0.72rem; color: {colors['muted']}; text-transform: uppercase; font-weight: 700; margin-top: 8px;">Reports</div>
<div style="font-size: 1.6rem; font-weight: 700;">{st.session_state.reports_generated}</div>
</div>""", unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
<div class="premium-card">
<div style="font-size: 1.4rem;">⏱️</div>
<div style="font-size: 0.72rem; color: {colors['muted']}; text-transform: uppercase; font-weight: 700; margin-top: 8px;">Uptime</div>
<div style="font-size: 1.6rem; font-weight: 700;">{uptime_str}</div>
</div>""", unsafe_allow_html=True)

    # Search Area
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    query = st.text_input("QUERY_INPUT", placeholder="Describe your research topic or ask a technical question...", label_visibility="collapsed")
    
    col_u1, col_u2 = st.columns([3, 1])
    with col_u1:
        go_button = st.button("✨ START RESEARCH", use_container_width=True, disabled=not st.session_state.backend_healthy)
    with col_u2:
        st.file_uploader("PDF_UPLOAD", type=["pdf"], label_visibility="collapsed")

    if go_button and query:
        # Research Logic
        progress_container = st.empty()
        result_container = st.container()
        try:
            with progress_container:
                render_progress_card(5, "Initializing AI agents...", st.session_state.theme)
            
            # Submit using global mode/year/provider from sidebar
            # Note: In a real app, we'd pull these from st.sidebar inputs if we stored them there
            # Since they are in the sidebar with st.session_state access, they are persistent
            task_id = api.submit_research(
                query=query,
                mode=st.session_state.get('mode_val', 'Deep Research'),
                year_filter=st.session_state.get('year_val', 2024),
                llm_provider=st.session_state.get('provider', 'Groq').lower()
            )
            
            result = api.poll_until_complete(
                task_id=task_id,
                on_progress=lambda p, s: progress_container.empty() or render_progress_card(p, s, st.session_state.theme)
            )
            
            progress_container.empty()
            with result_container:
                render_success_card("Research Complete", f"Analyzed results for: {query}")
                render_papers_grid(result.get('papers', []), st.session_state.theme)
                render_ideas_list(result.get('ideas', []), st.session_state.theme)
                
                # Sync fresh stats from backend
                sync_kpis()
                
        except Exception as e:
            progress_container.empty()
            render_error_card("Mission Failed", str(e))

    # Demo mode if no search
    if not go_button:
        st.markdown("<h3 class='gradient-text' style='margin: 40px 0 20px 0;'>🛡️ Featured Insights</h3>", unsafe_allow_html=True)
        demo_papers = [
            {"title": "Multi-Agent Systems for Scientific Discovery", "summary": "How LLM agents collaborate...", "authors": ["S. Kumar", "A. Patel"], "method": "Agentic Framework", "objective": "Automate discovery"},
            {"title": "Neural Architecture Search via Evolution", "summary": "Optimizing models through...", "authors": ["R. Chen"], "method": "Evolutionary", "objective": "SOTA Performance"}
        ]
        render_papers_grid(demo_papers, st.session_state.theme)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_library_page():
    st.markdown("<h1 class='gradient-text'>📑 My Research Library</h1>", unsafe_allow_html=True)
    st.markdown("<p style='opacity: 0.7;'>Access all your past research missions and generated intelligence.</p>", unsafe_allow_html=True)
    
    try:
        tasks = api.list_tasks()
        if not tasks:
            st.info("Your library is currently empty. Start a research mission to see it here!")
            return
            
        # Group by history
        for task in tasks:
            with st.container():
                cols = st.columns([5, 1, 1, 1])
                with cols[0]:
                    st.markdown(f"### {_sanitize(task['query'])}")
                    st.markdown(f"<span style='font-size: 0.8rem; opacity: 0.6;'>Performed on {task['created_at']} · Status: {task['status']}</span>", unsafe_allow_html=True)
                with cols[1]:
                    st.metric("Papers", task['paper_count'])
                with cols[2]:
                    st.metric("Ideas", task['idea_count'])
                with cols[3]:
                    if st.button("View", key=task['task_id']):
                        st.session_state.selected_task_id = task['task_id']
                st.markdown("<div class='stDivider'></div>", unsafe_allow_html=True)
                
        # If a task is selected, show its full results below
        if st.session_state.selected_task_id:
            st.markdown("<div class='stDivider'></div>", unsafe_allow_html=True)
            st.markdown(f"## Mission Results: {st.session_state.selected_task_id}")
            result = api.get_result(st.session_state.selected_task_id)
            render_papers_grid(result.get('papers', []), st.session_state.theme)
            render_ideas_list(result.get('ideas', []), st.session_state.theme)
            
    except Exception as e:
        render_error_card("Library Load Error", str(e))


def render_settings_section_header(title, description):
    st.markdown(f"""
<div class="settings-header">{title}</div>
<p style="color: {colors['muted']}; margin-top: -16px; margin-bottom: 32px; font-size: 0.95rem;">{description}</p>
""", unsafe_allow_html=True)

def render_settings_row(label, description, widget_key=None):
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
<div class="settings-label-group">
    <div class="settings-label">{label}</div>
    <div class="settings-description">{description}</div>
</div>
""", unsafe_allow_html=True)
    return col2

def render_settings_page():
    st.markdown("<h1 class='gradient-text' style='margin-bottom: 32px;'>⚙️ System Settings</h1>", unsafe_allow_html=True)
    
    # Split Pane Layout
    st.markdown('<div class="settings-container">', unsafe_allow_html=True)
    
    # Using columns for the split layout to maintain Streamlit interactivity
    menu_col, content_col = st.columns([1, 3])
    
    with menu_col:
        st.markdown('<div class="settings-menu">', unsafe_allow_html=True)
        sections = [
            ("🌐 General", "General"),
            ("👤 Personalization", "Personalization"),
            ("🧪 Research", "Research"),
            ("🤖 Models", "Models"),
            ("🔔 Notifications", "Notifications"),
            ("🔒 Data & Privacy", "Privacy"),
            ("🎨 Appearance", "Appearance")
        ]
        
        for label, tab_id in sections:
            is_active = st.session_state.settings_tab == tab_id
            if st.button(label, key=f"tab_{tab_id}", use_container_width=True, 
                         type="primary" if is_active else "secondary"):
                st.session_state.settings_tab = tab_id
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with content_col:
        st.markdown('<div class="settings-pane">', unsafe_allow_html=True)
        
        current_tab = st.session_state.settings_tab
        
        if current_tab == "General":
            render_settings_section_header("General Settings", "Manage your basic application preferences.")
            with render_settings_row("Language", "Select your preferred display language."):
                st.selectbox("LANGUAGE", ["English (US)", "Spanish", "French", "German"], label_visibility="collapsed")
            with render_settings_row("Timezone", "Configure how dates and times are displayed."):
                st.selectbox("TIMEZONE", ["UTC (Greenwich Meantime)", "EST (Eastern Standard)", "PST (Pacific Standard)", "IST (India Standard)"], label_visibility="collapsed")
            with render_settings_row("Auto-Refresh", "Automatically refresh research status in the background."):
                st.toggle("AUTO_REFRESH", value=True, label_visibility="collapsed")

        elif current_tab == "Personalization":
            render_settings_section_header("Personalization", "Customize how ScholarPulse interacts with you.")
            with render_settings_row("Researcher Name", "How should the AI address you in reports?"):
                st.text_input("NAME", placeholder="e.g. Dr. Scholar", label_visibility="collapsed")
            with render_settings_row("Tone of Voice", "Select the preferred AI response style."):
                st.select_slider("TONE", options=["Academic", "Professional", "Concise"], label_visibility="collapsed")

        elif current_tab == "Research":
            render_settings_section_header("Research Configuration", "Fine-tune the deep research engine.")
            with render_settings_row("Search Depth", "Number of search iterations per query."):
                st.slider("DEPTH", 1, 10, 3, label_visibility="collapsed")
            with render_settings_row("Concurrency", "Maximum simultaneous search queries."):
                st.number_input("CONCURRENCY", 1, 5, 2, label_visibility="collapsed")
            with render_settings_row("Source Filtering", "Only include peer-reviewed journals."):
                st.toggle("PEER_REVIEW", value=True, label_visibility="collapsed")

        elif current_tab == "Models":
            render_settings_section_header("Models & Intelligence", "Manage LLM providers and versioning.")
            with render_settings_row("Primary Model", "Default LLM used for synthesis."):
                st.selectbox("DEFAULT_LLM", ["Llama 3 (Groq)", "GPT-4o (Oxlo)", "Gemini 1.5 Pro"], label_visibility="collapsed")
            with render_settings_row("Reasoning Mode", "Enable chain-of-thought processing for complex queries."):
                st.toggle("CoT", value=True, label_visibility="collapsed")
            with render_settings_row("Provider API Key", "Manage your custom provider credentials."):
                st.button("🔑 CONFIGURE KEYS", use_container_width=True)

        elif current_tab == "Notifications":
            render_settings_section_header("Notifications", "Control how you receive mission updates.")
            with render_settings_row("Desktop Alerts", "Show browser notifications when a task completes."):
                st.toggle("DESKTOP_NOTIF", value=True, label_visibility="collapsed")
            with render_settings_row("Email Summaries", "Receive a PDF export of your research via email."):
                st.toggle("EMAIL_NOTIF", label_visibility="collapsed")

        elif current_tab == "Privacy":
            render_settings_section_header("Data & Privacy", "Control your research footprint and data.")
            with render_settings_row("Training Opt-out", "Do not use my research data for future model training."):
                st.toggle("OPT_OUT", value=True, label_visibility="collapsed")
            with render_settings_row("Export Library", "Download all your research history as JSON."):
                st.button("📥 EXPORT ALL", use_container_width=True)
            with render_settings_row("Clear History", "Permanently delete all past research tasks."):
                st.button("🗑️ PURGE DATA", use_container_width=True, type="primary")

        elif current_tab == "Appearance":
            render_settings_section_header("Appearance", "Customize the look and feel of your dashboard.")
            with render_settings_row("Interface Theme", "Switch between visual modes."):
                new_theme = st.radio("THEME_SELECT", ["Dark", "Night", "Light"], 
                                     index=["Dark", "Night", "Light"].index(st.session_state.theme),
                                     horizontal=True, label_visibility="collapsed")
                if new_theme != st.session_state.theme:
                    st.session_state.theme = new_theme
                    st.rerun()
            with render_settings_row("Reduced Motion", "Minimize animations for better performance."):
                st.toggle("LOW_MOTION", label_visibility="collapsed")

        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN DISPATCHER ---
if st.session_state.page == "Dashboard":
    render_dashboard()
elif st.session_state.page == "Library":
    render_library_page()
elif st.session_state.page == "Settings":
    render_settings_page()

st.markdown("<br><br><br><p style='text-align: center; color: #64748B; font-size: 0.75rem; font-weight: 500; opacity: 0.6;'>ScholarPulse · Enterprise Research Dashboard · v2.1.0</p>", unsafe_allow_html=True)
