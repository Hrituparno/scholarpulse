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
    # Aurora Minimal Color Palette (2027 Trends)
    primary_gradient = "linear-gradient(135deg, #6366F1, #8B5CF6)"
    accent_pink = "#EC4899"
    accent_amber = "#F59E0B"
    
    # Theme-specific colors
    if theme == "Dark":
        bg_color = "#0F0F23"
        card_bg = "rgba(30, 30, 60, 0.6)"
        text_primary = "#F1F5F9"
        text_muted = "#94A3B8"
        accent = "#8B5CF6"
        border_color = "rgba(139, 92, 246, 0.15)"
    elif theme == "Night":
        bg_color = "#09090B"
        card_bg = "rgba(24, 24, 27, 0.8)"
        text_primary = "#FAFAFA"
        text_muted = "#71717A"
        accent = "#6366F1"
        border_color = "rgba(99, 102, 241, 0.15)"
    else:  # Light
        bg_color = "#FAFBFC"
        card_bg = "rgba(255, 255, 255, 0.9)"
        text_primary = "#18181B"
        text_muted = "#52525B"
        accent = "#7C3AED"
        border_color = "rgba(124, 58, 237, 0.1)"
    
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Base Styles */
        .stApp {{ 
            background: {bg_color};
            background-image: radial-gradient(ellipse at top, {accent}08 0%, transparent 50%);
            color: {text_primary};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* Smooth Fade-in Animation */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        
        /* Modern Navbar */
        .top-navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 64px;
            background: {card_bg};
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            z-index: 1000;
            display: flex;
            align-items: center;
            padding: 0 32px;
            border-bottom: 1px solid {border_color};
        }}
        .top-navbar-brand {{ 
            background: {primary_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 1.4rem; 
            font-weight: 700; 
            letter-spacing: -0.5px;
        }}

        /* Refined Sidebar */
        [data-testid="stSidebar"] {{
            background: {card_bg} !important;
            backdrop-filter: blur(24px);
            border-right: 1px solid {border_color};
            padding-top: 24px;
        }}
        
        .nav-item {{
            padding: 12px 16px;
            border-radius: 10px;
            margin: 4px 12px;
            transition: all 0.2s ease;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            color: {text_muted};
            font-weight: 500;
            font-size: 0.9rem;
        }}
        .nav-item:hover, .nav-active {{
            background: {accent}15;
            color: {accent} !important;
        }}

        /* Bento-Style Cards */
        .kpi-card {{
            background: {card_bg};
            backdrop-filter: blur(20px);
            padding: 24px;
            border-radius: 20px;
            border: 1px solid {border_color};
            transition: all 0.3s ease;
            animation: fadeInUp 0.5s ease forwards;
        }}
        .kpi-card:hover {{
            border-color: {accent}40;
            transform: translateY(-4px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        /* History Items */
        .history-item {{
            font-size: 0.85rem;
            padding: 10px 14px;
            border-radius: 8px;
            background: {accent}08;
            margin-bottom: 8px;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }}
        .history-item:hover {{
            background: {accent}15;
            border-left-color: {accent};
        }}

        /* Modern Result Cards */
        .result-card {{
            background: {card_bg};
            backdrop-filter: blur(20px);
            border: 1px solid {border_color};
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
            animation: fadeInUp 0.5s ease forwards;
        }}
        .result-card:hover {{
            border-color: {accent}30;
            transform: translateY(-2px) scale(1.01);
            box-shadow: 0 24px 48px rgba(0,0,0,0.12);
        }}
        
        /* Modern Button Styling */
        .stButton>button {{
            background: {primary_gradient} !important;
            border: none !important;
            color: white !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            padding: 12px 24px !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 14px {accent}40 !important;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px {accent}50 !important;
        }}

        .card-img {{
            transition: transform 0.5s ease;
        }}
        .card-img:hover {{
            transform: scale(1.05);
        }}
        
        .block-container {{ padding-top: 5rem !important; }}
        
        /* Elegant Scrollbar */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ 
            background: {accent}30; 
            border-radius: 10px; 
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: {accent}50; }}
        
        /* Text Input Styling */
        .stTextInput>div>div>input {{
            background: {card_bg} !important;
            border: 1px solid {border_color} !important;
            border-radius: 12px !important;
            color: {text_primary} !important;
            padding: 14px 18px !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }}
        .stTextInput>div>div>input:focus {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 3px {accent}20 !important;
        }}
        
        /* Select Box Styling */
        .stSelectbox>div>div {{
            background: {card_bg} !important;
            border-color: {border_color} !important;
            border-radius: 10px !important;
        }}
        
        /* Gradient Text Utility */
        .gradient-text {{
            background: {primary_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
    </style>
    """

def render_kpi_card(label, value, icon, accent_color):
    """Modern Bento-style KPI card with gradient accent."""
    return f"""
    <div class="kpi-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 8px;">{label}</div>
                <div style="font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #6366F1, #8B5CF6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
            </div>
            <div style="font-size: 2rem; opacity: 0.6;">{icon}</div>
        </div>
    </div>
    """


def render_result_card(title, summary, link, authors=None):
    """Modern Aurora Minimal result card with refined aesthetics."""
    # Aurora palette accents
    accent = "#8B5CF6" if st.session_state.theme == "Dark" else "#6366F1" if st.session_state.theme == "Night" else "#7C3AED"
    
    # Generate a deterministic placeholder based on title length
    img_seed = len(title) % 10
    research_images = [
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1558494949-ef010958d684?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1620712943543-bcc4628c9757?auto=format&fit=crop&w=800&q=80"
    ]
    img_url = research_images[img_seed]

    return f"""
    <div class="result-card">
        <div style="width: 100%; height: 140px; border-radius: 14px; overflow: hidden; margin-bottom: 16px; background: linear-gradient(135deg, {accent}15, {accent}05);">
            <img src="{img_url}" 
                 onerror="this.src='https://images.unsplash.com/photo-1620712943543-bcc4628c9757?auto=format&fit=crop&w=800&q=80'"
                 style="width: 100%; height: 100%; object-fit: cover; opacity: 0.85;" 
                 class="card-img">
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="background: linear-gradient(135deg, {accent}20, {accent}10); color: {accent}; padding: 6px 14px; border-radius: 8px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px;">DISCOVERY</span>
            <span style="color: #94A3B8; font-size: 0.75rem; font-weight: 500;">{authors[0] if authors else 'AI Intelligence'}</span>
        </div>
        <a href="{link}" target="_blank" style="text-decoration: none; color: inherit;">
            <h4 style="margin: 0 0 10px 0; font-size: 1.1rem; line-height: 1.4; font-weight: 600; color: #F1F5F9;">{title}</h4>
            <p style="font-size: 0.85rem; color: #94A3B8; margin: 0 0 16px 0; line-height: 1.5; height: 3.2em; overflow: hidden;">{summary[:150]}...</p>
            <div style="display: flex; align-items: center; gap: 8px; color: {accent}; font-weight: 600; font-size: 0.85rem;">
                <span>Explore →</span>
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

# Apply Theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)
accent = "#8B5CF6" if st.session_state.theme == "Dark" else "#6366F1" if st.session_state.theme == "Night" else "#7C3AED"

# Modern Navbar
st.markdown(f"""
<div class="top-navbar">
    <a class="top-navbar-brand" href="#">ScholarPulse</a>
</div>
""", unsafe_allow_html=True)

# Sidebar Evolution
with st.sidebar:
    # Modern Profile Card
    st.markdown(f"""
    <div style='padding: 20px; display: flex; align-items: center; gap: 14px; margin-bottom: 24px;'>
        <div style="width: 48px; height: 48px; border-radius: 12px; background: linear-gradient(135deg, #6366F1, #8B5CF6); display: flex; align-items: center; justify-content: center; font-size: 1.4rem;">🧠</div>
        <div>
            <div style="font-weight: 600; font-size: 1rem; color: #F1F5F9;">ScholarPulse</div>
            <div style="font-size: 0.75rem; color: #94A3B8;">AI Research Agent</div>
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
st.markdown(f"<h1 style='margin-bottom: 8px; font-weight: 700; font-size: 2rem;'>Welcome back</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #94A3B8; margin-bottom: 32px; font-size: 1rem;'>What would you like to research today?</p>", unsafe_allow_html=True)

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

# Research Input Area (Modern Card)
with st.container():
    st.markdown(f"<div style='background: rgba(99, 102, 241, 0.05); padding: 28px; border-radius: 16px; border: 1px solid rgba(99, 102, 241, 0.1); margin-top: 16px;'>", unsafe_allow_html=True)
    query = st.text_input("QUERY_INPUT", placeholder="Enter your research query...", label_visibility="collapsed")
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        go_button = st.button("✨ Start Research", width="stretch")
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
        # Modern Loading State
        with st.container():
            st.markdown(f"<p style='color: {accent}; text-align: center; font-weight: 600; letter-spacing: 1px; margin-bottom: 16px;'>Analyzing your research query...</p>", unsafe_allow_html=True)
            progress_bar = st.progress(0)
            for i in range(101):
                import time
                time.sleep(0.008)
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
                st.markdown(f"<h3 class='gradient-text' style='font-weight: 600;'>📊 Research Discoveries</h3>", unsafe_allow_html=True)
                
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

st.markdown("<br><br><br><p style='text-align: center; color: #64748B; font-size: 0.8rem;'>ScholarPulse · Built with ❤️ for researchers</p>", unsafe_allow_html=True)
