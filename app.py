"""
ScholarPulse - AI Research Agent (Premium SaaS Redesign)

Main Entry Point for Cloud Deployment.
Redirects logic to the high-fidelity frontend components.
"""
import streamlit as st
import os
import sys
import time

# CRITICAL: Add the frontend directory to sys.path so it works exactly like local
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend"))

# Now we can import the premium components
from frontend.api_client import ScholarPulseAPI, APIException
from frontend.components.feedback import (
    get_feedback_styles,
    render_success_card,
    render_warning_card,
    render_error_card,
    render_connection_error,
    render_progress_card,
    render_empty_state,
    _sanitize
)
from frontend.components.cards import render_papers_grid, render_ideas_list, render_paper_card, render_idea_card
from frontend.styles.theme import get_theme_css, get_color_scheme

# Import everything else from frontend/app.py or just replicate the logic
# To avoid double-nesting issues, we just use the premium logic directly here
# but pointed at frontend sub-modules

# Page Config
st.set_page_config(
    page_title="ScholarPulse | AI Research Agent",
    page_icon="🧠",
    layout="wide",
)

# Initialize API client
api = ScholarPulseAPI()

import json

# Settings Persistence Helpers
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_settings.json")

def load_settings():
    """Load settings from local JSON file."""
    defaults = {
        "theme": "Dark",
        "researcher_name": "Dr. Scholar",
        "llm_provider": "Groq",
        "search_depth": 3,
        "concurrency": 2,
        "tone": "Professional"
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                stored = json.load(f)
                defaults.update(stored)
        except:
            pass
    return defaults

def save_settings():
    """Save current session state settings to local JSON."""
    settings = {
        "theme": st.session_state.theme,
        "researcher_name": st.session_state.get("researcher_name", "Dr. Scholar"),
        "llm_provider": st.session_state.get("llm_provider", "Groq"),
        "search_depth": st.session_state.get("search_depth", 3),
        "concurrency": st.session_state.get("concurrency", 2),
        "tone": st.session_state.get("tone", "Professional")
    }
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except:
        pass

# Initialize settings from file
persisted_settings = load_settings()

# Session State Initialization
if 'theme' not in st.session_state:
    st.session_state.theme = persisted_settings["theme"]
if 'researcher_name' not in st.session_state:
    st.session_state.researcher_name = persisted_settings["researcher_name"]
if 'llm_provider' not in st.session_state:
    st.session_state.llm_provider = persisted_settings["llm_provider"]
if 'search_depth' not in st.session_state:
    st.session_state.search_depth = persisted_settings["search_depth"]
if 'concurrency' not in st.session_state:
    st.session_state.concurrency = persisted_settings["concurrency"]
if 'tone' not in st.session_state:
    st.session_state.tone = persisted_settings["tone"]

if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
if 'is_researching' not in st.session_state:
    st.session_state.is_researching = False
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
    if st.button("📂 Dashboard", key="nav_dash", use_container_width=True, type="secondary" if st.session_state.page != "Dashboard" else "primary"):
        nav_page("Dashboard")
    if st.button("📑 My Library", key="nav_lib", use_container_width=True, type="secondary" if st.session_state.page != "Library" else "primary"):
        nav_page("Library")
    if st.button("⚙️ Settings", key="nav_settings", use_container_width=True, type="secondary" if st.session_state.page != "Settings" else "primary"):
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
        if st.session_state.is_researching:
            go_button = st.button("✨ MISSION IN PROGRESS...", use_container_width=True, disabled=True)
        else:
            go_button = st.button("✨ START RESEARCH", use_container_width=True, disabled=not st.session_state.backend_healthy)
    
    with col_u2:
        st.file_uploader("PDF_UPLOAD", type=["pdf"], label_visibility="collapsed")

    if (go_button and query) or st.session_state.is_researching:
        if go_button and query:
            st.session_state.is_researching = True
            st.rerun()
            
        # Research Logic
        progress_container = st.empty()
        result_container = st.container()
        try:
            with progress_container:
                render_progress_card(5, "Initializing AI agents...", st.session_state.theme)
            
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
                st.session_state.is_researching = False
                
        except Exception as e:
            st.session_state.is_researching = False
            progress_container.empty()
            render_error_card("Mission Failed", str(e))

    # Empty State or Demo mode if no search
    if not go_button and not st.session_state.is_researching:
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        render_empty_state("🚀", "Ready for Discovery?", "Enter a research query above to start your deep discovery mission.")
        
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
            render_empty_state("📁", "No Research Found", "Your library is currently empty. Start a research mission to see it here!")
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
    
    menu_col, content_col = st.columns([1, 3])
    
    with menu_col:
        st.markdown('<div class="settings-menu">', unsafe_allow_html=True)
        sections = [
            ("🌐 General", "General"),
            ("👤 Personalization", "Personalization"),
            ("🧪 Research", "Research"),
            ("🤖 Models", "Models"),
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
            with render_settings_row("Auto-Refresh", "Automatically refresh research status."):
                st.toggle("AUTO_REFRESH", value=True, label_visibility="collapsed")

        elif current_tab == "Personalization":
            render_settings_section_header("Personalization", "Customize your identity.")
            with render_settings_row("Researcher Name", "How should we address you?"):
                new_name = st.text_input("NAME", value=st.session_state.researcher_name, label_visibility="collapsed")
                if new_name != st.session_state.researcher_name:
                    st.session_state.researcher_name = new_name
                    save_settings()

        elif current_tab == "Research":
            render_settings_section_header("Research Configuration", "Fine-tune engine parameters.")
            with render_settings_row("Search Depth", "Iterations per query."):
                new_depth = st.slider("DEPTH", 1, 10, st.session_state.search_depth, label_visibility="collapsed")
                if new_depth != st.session_state.search_depth:
                    st.session_state.search_depth = new_depth
                    save_settings()

        elif current_tab == "Models":
            render_settings_section_header("Models", "Select LLM providers.")
            with render_settings_row("Default Provider", "Primary AI engine."):
                st.selectbox("DEFAULT_LLM", ["Groq", "Oxlo", "Gemini"], label_visibility="collapsed")

        elif current_tab == "Appearance":
            render_settings_section_header("Appearance", "Themes and animations.")
            with render_settings_row("Theme", "Switch mode."):
                new_theme = st.radio("THEME_SELECT", ["Dark", "Night", "Light"], 
                                     index=["Dark", "Night", "Light"].index(st.session_state.theme),
                                     horizontal=True, label_visibility="collapsed")
                if new_theme != st.session_state.theme:
                    st.session_state.theme = new_theme
                    save_settings()
                    st.rerun()

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
