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
    <div class="kpi-card" style="display: block; padding: 20px;">
        <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 8px;">{label}</div>
        <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 8px;">{value}</div>
        <div style="font-size: 1.5rem; opacity: 0.6;">{icon}</div>
    </div>
    """


def render_result_card(title, summary, link, authors=None, paper_data=None):
    """Simplified result card with essential features."""
    accent = "#8B5CF6" if st.session_state.theme == "Dark" else "#6366F1" if st.session_state.theme == "Night" else "#7C3AED"
    
    # Use st.container instead of pure HTML for better rendering
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://images.unsplash.com/photo-1507413245164-6160d8298b31?auto=format&fit=crop&w=200&q=80", use_column_width=True)
        with col2:
            st.subheader(title, divider="gray")
            st.write(summary[:150] + "...")
            author_text = f"**{authors[0]}**" if authors else "**Research Paper**"
            st.caption(f"{author_text} | [Read More]({link})")
    return None


# Handle Session State for History & KPIs & Analytics
import datetime
import time
if "history" not in st.session_state: st.session_state.history = []
if "papers_found" not in st.session_state: st.session_state.papers_found = 0
if "searches_made" not in st.session_state: st.session_state.searches_made = 0
if "reports_generated" not in st.session_state: st.session_state.reports_generated = 0
if "session_start" not in st.session_state: st.session_state.session_start = time.time()
if "active_tool" not in st.session_state: st.session_state.active_tool = None

# Calculate Session Uptime
elapsed_sec = int(time.time() - st.session_state.session_start)
mins, secs = divmod(elapsed_sec, 60)
uptime_str = f"{mins}m {secs}s"

# Apply Theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)
accent = "#8B5CF6" if st.session_state.theme == "Dark" else "#6366F1" if st.session_state.theme == "Night" else "#7C3AED"

# 1. Process Logic FIRST (to update session state for sidebar)
search_triggered = False
if "go_button_held" not in st.session_state: st.session_state.go_button_held = False

# Sidebar Tools Logic
if st.session_state.active_tool == "Summarize PDF":
    tool_instruction = "Upload a PDF below to generate a concise intelligence summary."
elif st.session_state.active_tool == "Compare Papers":
    tool_instruction = "Enter multiple queries or upload papers to compare research trajectories."
elif st.session_state.active_tool == "Generate Ideas":
    tool_instruction = "Describe your research area to generate novel hypotheses."
else:
    tool_instruction = "Ready to push the boundaries of science today?"

# Modern Navbar
st.markdown(f"""
<div class="top-navbar">
    <a class="top-navbar-brand" href="#">ScholarPulse</a>
</div>
""", unsafe_allow_html=True)

# Sidebar Evolution
# Get theme-adaptive text color
text_color = "#18181B" if st.session_state.theme == "Light" else "#F1F5F9"
muted_color = "#52525B" if st.session_state.theme == "Light" else "#94A3B8"

with st.sidebar:
    # Modern Profile Card
    st.markdown(f"""
    <div style='padding: 20px; display: flex; align-items: center; gap: 14px; margin-bottom: 24px;'>
        <div style="width: 48px; height: 48px; border-radius: 12px; background: linear-gradient(135deg, #6366F1, #8B5CF6); display: flex; align-items: center; justify-content: center; font-size: 1.4rem;">🧠</div>
        <div>
            <div style="font-weight: 600; font-size: 1rem; color: {text_color};">ScholarPulse</div>
            <div style="font-size: 0.75rem; color: {muted_color};">AI Research Agent</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"<div class='nav-item nav-active'>📂 Dashboard</div>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown(f"<p style='font-weight: 600; color: {text_color}; margin-bottom: 10px;'>🛠️ Configuration</p>", unsafe_allow_html=True)
    provider = st.selectbox("Intelligence", ["Groq", "Oxlo", "Gemini"], index=0)
    mode_val = st.selectbox("Research Mode", ["Deep Research", "Web Search", "Study & Learn"], index=0)
    year_val = st.number_input("Year Filter (0 = All)", min_value=0, max_value=2027, value=2024)
    
    st.divider()
    st.markdown(f"<p style='font-weight: 600; color: {text_color}; margin-bottom: 10px;'>🔧 AI Tools</p>", unsafe_allow_html=True)
    
    if st.sidebar.button("📝 Summarize PDF", use_container_width=True):
        st.session_state.active_tool = "Summarize PDF"
        st.toast("Summarize PDF tool activated!")
        
    if st.sidebar.button("🔍 Compare Papers", use_container_width=True):
        st.session_state.active_tool = "Compare Papers"
        st.toast("Compare Papers tool activated!")
        
    if st.sidebar.button("💡 Generate Ideas", use_container_width=True):
        st.session_state.active_tool = "Generate Ideas"
        st.toast("Idea Generator activated!")
        
    if st.sidebar.button("📊 Citation Finder", use_container_width=True):
        st.session_state.active_tool = "Citation Finder"
        st.toast("Citation Finder activated!")

    
    st.divider()
    st.markdown(f"<p style='font-weight: 600; color: {text_color}; margin-bottom: 10px;'>📜 Recent Searches</p>", unsafe_allow_html=True)
    if st.session_state.history:
        for item in reversed(st.session_state.history[-5:]):
            st.markdown(f"""
            <div style="padding: 10px 12px; background: {accent}08; border-radius: 8px; margin-bottom: 6px; border-left: 3px solid {accent};">
                <div style="font-size: 0.85rem; color: {text_color}; font-weight: 500;">{item['query'][:35]}...</div>
                <div style="font-size: 0.7rem; color: {muted_color};">✓ Completed · {item['time']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='font-size: 0.85rem; color: {muted_color}; padding: 10px;'>No searches yet. Start researching!</p>", unsafe_allow_html=True)

    st.divider()
    st.markdown(f"<p style='font-weight: 600; color: {text_color}; margin-bottom: 10px;'>🎨 Theme</p>", unsafe_allow_html=True)
    new_theme = st.selectbox("Interface Theme", ["Dark", "Night", "Light"], index=["Dark", "Night", "Light"].index(st.session_state.theme), label_visibility="collapsed")
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

# Main Dashboard Content
content_container = st.container()

# Sidebar (This will now see updated session state because it's after the navbar BUT we can move the action logic higher)
# Actually, Streamlit reruns the whole script. 
# The best way to make the sidebar see the NEW history is to detect the button click *before* the sidebar block.

# --- Action Detection ---
go_clicked = False # Placeholder
# Actually, we can use a trick: check the button state here if it was set in a previous run or use a form.
# But for now, let's just make the sidebar render last or use a placeholder for it.
# Streamlit usually prefers sidebar first for layout.
# We'll stick to the current order but use st.rerun() if we need the sidebar to update immediately after a state change.

with content_container:
    if st.session_state.active_tool:
        st.markdown(f"""
        <div style="background: {accent}1a; padding: 24px; border-radius: 16px; border: 1px solid {accent}30; margin-bottom: 32px; animation: fadeInUp 0.5s ease;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h3 style="margin: 0; color: {accent}; font-size: 1.25rem; font-weight: 700;">🛠️ {st.session_state.active_tool}</h3>
                    <p style="margin: 8px 0 0 0; font-size: 0.95rem; color: {text_color}; opacity: 0.8;">{tool_instruction}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✕ Exit Tool Mode", key="close_tool_mode"):
            st.session_state.active_tool = None
            st.rerun()

    st.markdown(f"<h1 style='margin-bottom: 8px; font-weight: 700; font-size: 2.2rem; color: {text_color};'>Welcome back</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {muted_color}; margin-bottom: 32px; font-size: 1.1rem;'>How can I advance your research today?</p>", unsafe_allow_html=True)

    # KPI Row (Live Stats)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1: 
        st.markdown(render_kpi_card("Papers Found", str(st.session_state.papers_found), "📄", accent), unsafe_allow_html=True)
    with kpi_col2: 
        st.markdown(render_kpi_card("Searches", str(st.session_state.searches_made), "🔍", accent), unsafe_allow_html=True)
    with kpi_col3: 
        st.markdown(render_kpi_card("Reports", str(st.session_state.reports_generated), "📊", accent), unsafe_allow_html=True)
    with kpi_col4: 
        st.markdown(render_kpi_card("Uptime", uptime_str, "⏱️", accent), unsafe_allow_html=True)

    # Research Input Area
    with st.container():
        st.markdown(f"<div style='background: {accent}08; padding: 32px; border-radius: 20px; border: 1px solid {accent}15; margin-top: 24px;'>", unsafe_allow_html=True)
        
        # Tool-specific placeholders
        placeholder_text = "What would you like to research?"
        if st.session_state.active_tool == "Summarize PDF": placeholder_text = "Analysis target (e.g., 'Core findings of this paper')"
        elif st.session_state.active_tool == "Compare Papers": placeholder_text = "Topics to compare (e.g., 'Transformer vs State Space models')"
        elif st.session_state.active_tool == "Generate Ideas": placeholder_text = "Research area (e.g., 'Scalable LLM training')"
        
        query = st.text_input("QUERY_INPUT", placeholder=placeholder_text, label_visibility="collapsed")
        
        col_u1, col_u2 = st.columns([3, 1])
        with col_u1:
            button_label = "✨ Start Research"
            if st.session_state.active_tool == "Summarize PDF": button_label = "📝 Summarize PDF"
            elif st.session_state.active_tool == "Compare Papers": button_label = "🔍 Compare Research"
            elif st.session_state.active_tool == "Generate Ideas": button_label = "💡 Generate Hypotheses"
            
            go_button = st.button(button_label, use_container_width=True)
        with col_u2:
            uploaded_file = st.file_uploader("PDF_UPLOAD", type=["pdf"], label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # Results Area
    st.markdown(f"<h3 class='gradient-text' style='font-weight: 600; margin-bottom: 24px;'>💡 Featured Research</h3>", unsafe_allow_html=True)
    
    # Show demo cards on initial load if no searches yet
    if not st.session_state.papers_found:
        demo_papers = [
            {
                "title": "Large Language Models as Decentralized Decision Makers",
                "summary": "Explores how large language models can function as autonomous agents in decentralized systems, making complex decisions without central coordination.",
                "pdf_url": "https://arxiv.org/abs/2312.10069",
                "authors": ["Alice Chen", "Bob Smith"]
            },
            {
                "title": "Efficient Fine-tuning of Large Language Models",
                "summary": "Proposes novel techniques for efficiently fine-tuning large language models while maintaining performance and reducing computational overhead.",
                "pdf_url": "https://arxiv.org/abs/2310.12345",
                "authors": ["Diana Ross", "Eve Wilson"]
            }
        ]
        
        st.markdown(f"<p style='color: {muted_color}; font-size: 0.9rem; margin-bottom: 20px;'>Start a research query above to discover relevant papers, or explore sample research findings below.</p>", unsafe_allow_html=True)
        
        grid_cols = st.columns(2)
        for idx, paper in enumerate(demo_papers):
            with grid_cols[idx % 2]:
                render_result_card(
                    title=paper.get("title", "Unknown Source"),
                    summary=paper.get("summary", "No summary available."),
                    link=paper.get("pdf_url", "#"),
                    authors=paper.get("authors", [])
                )

    if go_button:
        if not query and not uploaded_file:
            st.warning("Please enter a query or upload a file.")
        else:
            # SAVE TO HISTORY IMMEDIATELY BEFORE PROCESS
            st.session_state.history.append({
                "query": query if query else "PDF Analysis",
                "time": datetime.datetime.now().strftime("%H:%M:%S")
            })
            
            # Modern Loading State
            with st.container():
                loading_msg = "Analyzing your research query..."
                if st.session_state.active_tool == "Summarize PDF": loading_msg = "Extracting intelligence from PDF..."
                st.markdown(f"<p style='color: {accent}; text-align: center; font-weight: 600; letter-spacing: 1px; margin-bottom: 16px;'>{loading_msg}</p>", unsafe_allow_html=True)
                progress_bar = st.progress(0)
                for i in range(101):
                    import time
                    time.sleep(0.005)
                    progress_bar.progress(i)
            
            def ui_callback(msg): pass

            runner = AgentRunner(callback=ui_callback, llm_provider=provider.lower())
            
            with st.spinner("✨ Researching..."):
                actual_year = year_val if year_val > 0 else None
                report_md_path, papers = runner.run_demo(query=query, live=True, year=actual_year, mode=mode_val)
                
                if report_md_path and os.path.exists(report_md_path):
                    st.session_state.papers_found += len(papers)
                    st.session_state.searches_made += 1
                    st.session_state.reports_generated += 1
                    
                    st.success("✅ Research Complete!")
                    
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    docx_path = report_md_path.replace(".md", ".docx")
                    if os.path.exists(docx_path):
                        with open(docx_path, "rb") as f:
                            btn_col1.download_button("📥 Word (.docx)", f, os.path.basename(docx_path), use_container_width=True)
                    
                    txt_path = report_md_path.replace(".md", ".txt")
                    if os.path.exists(txt_path):
                        with open(txt_path, "r", encoding="utf-8") as f:
                            btn_col2.download_button("📄 Plain Text (.txt)", f.read(), os.path.basename(txt_path), use_container_width=True)

                    with open(report_md_path, "r", encoding="utf-8") as f:
                        btn_col3.download_button("🔗 Markdown (.md)", f.read(), os.path.basename(report_md_path), use_container_width=True)
                    
                    st.markdown("---")
                    st.markdown(f"<h3 class='gradient-text' style='font-weight: 600;'>📊 Research Discoveries</h3>", unsafe_allow_html=True)
                    
                    grid_cols = st.columns(2)
                    for idx, paper in enumerate(papers):
                        with grid_cols[idx % 2]:
                            render_result_card(
                                title=paper.get("title", "Unknown Source"),
                                summary=paper.get("summary", "No summary available."),
                                link=paper.get("pdf_url", paper.get("google_scholar_url", "#")),
                                authors=paper.get("authors", [])
                            )
                    
                    st.markdown("---")
                    with st.expander("📖 View Full Report", expanded=False):
                        with open(report_md_path, "r", encoding="utf-8") as f:
                            st.markdown(f.read())
                    
                    # Force rerun once to update sidebar history
                    st.rerun()
                else:
                    st.error("❌ Research could not be completed.")

st.markdown("<br><br><br><p style='text-align: center; color: #64748B; font-size: 0.8rem;'>ScholarPulse · Built with ❤️ for researchers</p>", unsafe_allow_html=True)

st.markdown("<br><br><br><p style='text-align: center; color: #64748B; font-size: 0.8rem;'>ScholarPulse · Built with ❤️ for researchers</p>", unsafe_allow_html=True)
