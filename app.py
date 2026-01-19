import streamlit as st
import os
import time
from pathlib import Path
from agent.runner import AgentRunner
from config import DEFAULT_QUERY

# Page Config
st.set_page_config(
    page_title="ScholarPulse",
    page_icon="🧠",
    layout="wide",
)

# Theme Management
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"

def get_theme_css(theme):
    # Neon Accent Colors
    neon_green = "#39FF14"
    neon_blue = "#00D2FF"
    
    accent = neon_green if theme == "Dark" else neon_blue if theme == "Night" else "#F44336"
    bg_color = "#0B0C10" if theme == "Dark" else "#000000" if theme == "Night" else "#F4F7F6"
    card_bg = "rgba(31, 41, 55, 0.7)" if theme != "Light" else "#FFFFFF"
    text_color = "#FFFFFF" if theme != "Light" else "#1F2937"
    
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        
        .stApp {{ 
            background-color: {bg_color}; 
            color: {text_color};
            font-family: 'Space Grotesk', sans-serif;
        }}
        
        /* Neon Glow Text */
        .neon-text {{
            color: {accent};
            text-shadow: 0 0 10px {accent}44, 0 0 20px {accent}22;
        }}

        /* Navbar Evolution */
        .top-navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 65px;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(12px);
            z-index: 1000;
            display: flex;
            align-items: center;
            padding: 0 30px;
            border-bottom: 1px solid {accent}33;
        }}
        .top-navbar-brand {{ 
            color: {accent}; 
            font-size: 1.6rem; 
            font-weight: 800; 
            letter-spacing: 1px;
            text-shadow: 0 0 15px {accent}55;
        }}

        /* Sidebar Social Styling */
        [data-testid="stSidebar"] {{
            background-color: {'#0F111A' if theme != 'Light' else '#FFFFFF'} !important;
            padding-top: 20px;
            border-right: 1px solid {accent}22;
        }}
        
        .nav-item {{
            padding: 12px 20px;
            border-radius: 12px;
            margin: 4px 10px;
            transition: all 0.3s;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 15px;
            color: {text_color}88;
        }}
        .nav-item:hover, .nav-active {{
            background: {accent}1a;
            color: {accent} !important;
        }}

        /* KPI Neon Cards */
        .kpi-card {{
            background: {card_bg};
            backdrop-filter: blur(10px);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid {accent}22;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            margin-bottom: 15px;
        }}
        .kpi-card:hover {{
            border-color: {accent};
            box-shadow: 0 0 25px {accent}22;
            transform: translateY(-5px);
        }}
        
        /* History Items */
        .history-item {{
            font-size: 0.85rem;
            padding: 8px 15px;
            border-left: 2px solid {accent}44;
            margin-bottom: 8px;
            opacity: 0.7;
            transition: 0.3s;
        }}
        .history-item:hover {{
            opacity: 1;
            border-left-color: {accent};
            background: {accent}11;
        }}

        /* Result Cards (Glassmorphism) */
        .result-card {{
            background: {card_bg};
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            transition: 0.4s;
        }}
        .result-card:hover {{
            border-color: {accent}66;
            background: {card_bg};
            box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        }}
        /* Master System Load Animation */
        @keyframes pulse-glow {{
            0% {{ box-shadow: 0 0 5px {accent}44; }}
            50% {{ box-shadow: 0 0 20px {accent}88; }}
            100% {{ box-shadow: 0 0 5px {accent}44; }}
        }}
        .stButton>button {{
            background: {accent}1a !important;
            border: 1px solid {accent}44 !important;
            color: {accent} !important;
            font-weight: 700 !important;
            letter-spacing: 2px !important;
            text-transform: uppercase !important;
            transition: 0.3s !important;
            animation: pulse-glow 2s infinite;
        }}
        .stButton>button:hover {{
            background: {accent} !important;
            color: black !important;
            box-shadow: 0 0 30px {accent}66 !important;
        }}

        .card-img:hover {{
            transform: scale(1.1);
        }}
        
        .block-container {{ padding-top: 6rem !important; }}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: {accent}33; border-radius: 10px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {accent}66; }}
    </style>
    """

def render_kpi_card(label, value, icon, accent_color):
    return f"""
    <div class="kpi-card">
        <div style="font-size: 1.5rem; margin-bottom: 10px;">{icon}</div>
        <div style="font-size: 0.75rem; color: #888; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;">{label}</div>
        <div style="font-size: 1.8rem; font-weight: 800; color: {accent_color};">{value}</div>
    </div>
    """

def render_result_card(title, summary, link, authors=None):
    """Generates HTML for a Neon Noir result card with imagery."""
    accent = "#39FF14" if st.session_state.theme == "Dark" else "#00D2FF" if st.session_state.theme == "Night" else "#F44336"
    
    # Generate a deterministic placeholder based on title length or random research theme
    img_seed = len(title) % 10
    research_images = [
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80", # Robotics
        "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80", # Tech
        "https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=800&q=80", # Lab
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&w=800&q=80", # Logic
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80", # Neural
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80", # Intelligence
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80", # Cybersecurity
        "https://images.unsplash.com/photo-1558494949-ef010958d684?auto=format&fit=crop&w=800&q=80", # Server
        "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80", # Data
        "https://images.unsplash.com/photo-1620712943543-bcc4628c9757?auto=format&fit=crop&w=800&q=80"  # AI Glass
    ]
    img_url = research_images[img_seed]

    # Added onerror fallback and more descriptive title
    return f"""
    <div class="result-card">
        <div style="width: 100%; height: 160px; border-radius: 12px; overflow: hidden; margin-bottom: 20px; border: 1px solid {accent}1a; background: #1a1a1a;">
            <img src="{img_url}" 
                 onerror="this.src='https://plus.unsplash.com/premium_photo-1661877737564-3dfd7282efcb?auto=format&fit=crop&w=800&q=80'"
                 style="width: 100%; height: 100%; object-fit: cover; opacity: 0.8; transition: transform 0.6s ease;" 
                 class="card-img">
        </div>
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
            <span style="background: {accent}22; color: {accent}; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800;">DISCOVERY</span>
            <span style="color: #888; font-size: 0.75rem; font-weight: 600;">{authors[0] if authors else 'Web Intelligence'}</span>
        </div>
        <a href="{link}" target="_blank" style="text-decoration: none; color: inherit;">
            <h4 style="margin-top: 0; font-size: 1.15rem; line-height: 1.4; margin-bottom: 10px; font-weight: 700;">{title}</h4>
            <div style="font-size: 0.85rem; color: #777; margin-bottom: 15px; line-height: 1.5; height: 3em; overflow: hidden;">{summary[:160]}...</div>
            <div style="border-top: 1px solid rgba(128,128,128,0.1); padding-top: 15px; color: {accent}; font-weight: 700; font-size: 0.85rem; display: flex; align-items: center; justify-content: space-between;">
                <span>View Full Discovery</span>
                <span style="font-size: 1.1rem; filter: drop-shadow(0 0 5px {accent}aa);">↗</span>
            </div>
        </a>
    </div>
    """

# Handle Session State for History & KPIs & Analytics
import datetime
import time
if "history" not in st.session_state: st.session_state.history = []
if "kpi_tasks" not in st.session_state: st.session_state.kpi_tasks = "125"
if "kpi_tickets" not in st.session_state: st.session_state.kpi_tickets = "257"
if "kpi_comments" not in st.session_state: st.session_state.kpi_comments = "243"
if "kpi_visitors" not in st.session_state: st.session_state.kpi_visitors = "1225"
if "session_start" not in st.session_state: st.session_state.session_start = time.time()
if "intensity_data" not in st.session_state: st.session_state.intensity_data = [10, 15, 8, 22, 18, 25, 30] # Static seed, dynamic growth

# Calculate Screen Time
elapsed_sec = int(time.time() - st.session_state.session_start)
hrs, rem = divmod(elapsed_sec, 3600)
mins, secs = divmod(rem, 60)
screen_time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"

st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# Apply Theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)
accent = "#39FF14" if st.session_state.theme == "Dark" else "#00D2FF" if st.session_state.theme == "Night" else "#F44336"

# Top Navbar (Glassmorphism)
st.markdown(f"""
<div class="top-navbar">
    <a class="top-navbar-brand" href="#">SCHOLARPULSE <span style="font-weight: 300; opacity: 0.7;">NOIR EDITION</span></a>
</div>
""", unsafe_allow_html=True)

# Sidebar Evolution
with st.sidebar:
    # Profile Card (Linda Stewart Style)
    st.markdown(f"""
    <div style='padding: 20px; color: white; display: flex; align-items: center; gap: 15px; margin-bottom: 20px;'>
        <img src="https://www.w3schools.com/howto/img_avatar.png" style="width: 60px; border-radius: 50%; border: 2px solid {accent}; box-shadow: 0 0 15px {accent}44;">
        <div>
            <div style="font-weight: 700; font-size: 1.1rem;">ScholarPulse</div>
            <div style="font-size: 0.75rem; opacity: 0.6;">research.agent@elite.ai</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div class='nav-item nav-active'>📂 Dashboard</div>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🛠️ Configuration")
    provider = st.selectbox("Intelligence", ["Groq", "Oxlo", "Gemini"], index=0)
    mode_val = st.selectbox("Research Mode", ["Deep Research", "Web Search", "Study & Learn"], index=0)
    year_val = st.number_input("Year Filter (0 = All)", min_value=0, max_value=2026, value=2024)
    
    st.divider()
    st.markdown("### 📜 Past Intel (History)")
    if st.session_state.history:
        for item in reversed(st.session_state.history[-5:]):
            st.markdown(f"<div class='history-item'>{item['query'][:30]}...<br><span style='font-size: 0.7rem; opacity: 0.5;'>{item['time']}</span></div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size: 0.8rem; opacity: 0.5; padding: 0 15px;'>No previous history available.</p>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📊 Usage Analytics")
    # Screen Time Metric
    st.markdown(f"""
    <div style='background: {accent}11; padding: 15px; border-radius: 12px; border: 1px solid {accent}33; margin: 10px;'>
        <div style='font-size: 0.7rem; color: #888; text-transform: uppercase; font-weight: 700;'>Total Screen Time</div>
        <div style='font-size: 1.4rem; font-weight: 800; color: {accent}; letter-spacing: 2px;'>{screen_time_str}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Research Intensity Graph
    import pandas as pd
    chart_data = pd.DataFrame(st.session_state.intensity_data, columns=['Intensity'])
    st.sidebar.area_chart(chart_data, color=accent, use_container_width=True)
    st.markdown("<p style='font-size: 0.65rem; color: #666; text-align: center; margin-top: -10px;'>Research Intensity over Time</p>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🎨 Aesthetics")
    new_theme = st.selectbox("Interface Theme", ["Dark", "Night", "Light"], index=["Dark", "Night", "Light"].index(st.session_state.theme))
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

# Main Dashboard Layout
st.markdown(f"<h1 style='margin-bottom: 5px; font-weight: 800;'>Hello, Researcher!</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #888; margin-bottom: 30px;'>Ready to push the boundaries of science today?</p>", unsafe_allow_html=True)

# KPI Row (Neon)
kpi_area = st.empty()
def update_kpi_row():
    with kpi_area.container():
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1: st.markdown(render_kpi_card("Discoveries", st.session_state.kpi_tasks, "🔥", accent), unsafe_allow_html=True)
        with kpi_col2: st.markdown(render_kpi_card("Records", st.session_state.kpi_tickets, "📈", accent), unsafe_allow_html=True)
        with kpi_col3: st.markdown(render_kpi_card("Insights", st.session_state.kpi_comments, "🧠", accent), unsafe_allow_html=True)
        with kpi_col4: st.markdown(render_kpi_card("Security", "Active", "🛡️", accent), unsafe_allow_html=True)

update_kpi_row()

# Research Input Area (Glassmorphism)
with st.container():
    st.markdown(f"<div style='background: {accent}11; padding: 30px; border-radius: 20px; border: 1px dashed {accent}33; margin-top: 20px;'>", unsafe_allow_html=True)
    query = st.text_input("QUERY_INPUT", placeholder="Enter your research query for the Neon engine...", label_visibility="collapsed")
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        go_button = st.button("⚡ EXECUTE NEON RESEARCH", width="stretch")
    with col_u2:
        uploaded_file = st.file_uploader("PDF_UPLOAD", type=["pdf"], label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# Results Area
status_area = st.empty()

if go_button:
    if not query and not uploaded_file:
        st.warning("Please enter a query or upload a file.")
    else:
        # Master System Load (Wow Factor)
        with st.container():
            st.markdown(f"<h3 style='color: {accent}; text-align: center; letter-spacing: 5px;'>INITIATING NEON DISCOVERY</h3>", unsafe_allow_html=True)
            progress_bar = st.progress(0)
            for i in range(101):
                import time
                time.sleep(0.01)
                progress_bar.progress(i)
        
        # Save to History
        st.session_state.history.append({
            "query": query if query else "PDF Analysis",
            "time": datetime.datetime.now().strftime("%H:%M:%S")
        })
        
        # Increment Intensity Chart
        import random
        st.session_state.intensity_data.append(st.session_state.intensity_data[-1] + random.randint(5, 15))
        if len(st.session_state.intensity_data) > 20: st.session_state.intensity_data.pop(0)
        
        logs = []
        def ui_callback(msg):
            logs.append(msg)
            with status_area.container():
                st.code("\n".join(logs), language="text")

        runner = AgentRunner(callback=ui_callback, llm_provider=provider.lower())
        
        with st.status("🧠 Neon Engine is Processing...", expanded=True) as status:
            actual_year = year_val if year_val > 0 else None
            report_md_path, papers = runner.run_demo(query=query, live=True, year=actual_year, mode=mode_val)
            
            if report_md_path and os.path.exists(report_md_path):
                # Update Dynamic KPIs
                st.session_state.kpi_tasks = str(int(st.session_state.kpi_tasks) + len(papers))
                st.session_state.kpi_tickets = str(int(st.session_state.kpi_tickets) + 1)
                update_kpi_row()
                
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                st.balloons()
                
                st.success(f"Intel Report Ready!")
                
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                docx_path = report_md_path.replace(".md", ".docx")
                if os.path.exists(docx_path):
                    with open(docx_path, "rb") as f:
                        btn_col1.download_button("📥 Word (.docx)", f, os.path.basename(docx_path), width="stretch")
                
                txt_path = report_md_path.replace(".md", ".txt")
                if os.path.exists(txt_path):
                    with open(txt_path, "r", encoding="utf-8") as f:
                        btn_col2.download_button("📄 Plain Text (.txt)", f.read(), os.path.basename(txt_path), width="stretch")

                with open(report_md_path, "r", encoding="utf-8") as f:
                    btn_col3.download_button("🔗 Markdown (.md)", f.read(), os.path.basename(report_md_path), width="stretch")
                
                st.markdown("---")
                st.markdown(f"<h3 class='neon-text'>📊 Discovery Dashboard</h3>", unsafe_allow_html=True)
                
                grid_cols = st.columns(2)
                for idx, paper in enumerate(papers):
                    with grid_cols[idx % 2]:
                        st.markdown(render_result_card(
                            title=paper.get("title", "Unknown Source"),
                            summary=paper.get("summary", "No summary available."),
                            link=paper.get("pdf_url", paper.get("google_scholar_url", "#")),
                            authors=paper.get("authors", [])
                        ), unsafe_allow_html=True)
                
                st.markdown("---")
                with st.expander("📖 View Strategic Intelligence Report", expanded=False):
                    st.markdown("### 🔍 Strategic Summary Preview")
                    with open(report_md_path, "r", encoding="utf-8") as f:
                        st.markdown(f.read())
            else:
                status.update(label="❌ Analysis Interrupted", state="error")

st.markdown("<br><br><br><br><p style='text-align: center; color: #4b5563; font-size: 0.8rem;'>ScholarPulse Noir | 2026 Production Environment</p>", unsafe_allow_html=True)
