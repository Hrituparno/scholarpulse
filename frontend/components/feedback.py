"""
Feedback and Status Components for ScholarPulse UI.

Modern, card-based feedback for success, warning, and error states.
"""
import streamlit as st
import textwrap
import re

def _sanitize(text: str) -> str:
    """Sanitize raw agent text to prevent HTML breakage."""
    if not text:
        return ""
    s = str(text).replace("```", "").replace("`", "")
    s = s.replace("<", "&lt;").replace(">", "&gt;")
    return s.strip()

def get_feedback_styles(theme: str = "Dark") -> str:
    """Get CSS for feedback components."""
    # Theme colors for icons and borders
    if theme == "Dark":
        success = "#10B981"
        warning = "#F59E0B"
        error = "#EF4444"
        info = "#3B82F6"
    elif theme == "Night":
        success = "#059669"
        warning = "#D97706"
        error = "#DC2626"
        info = "#2563EB"
    else: # Light
        success = "#10B981"
        warning = "#D97706"
        error = "#EF4444"
        info = "#3B82F6"

    return textwrap.dedent(f"""
        <style>
            .feedback-card {{
                padding: 16px 20px;
                border-radius: 16px;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
                gap: 16px;
                animation: slideInSide 0.5s ease-out;
            }}
            
            .feedback-success {{ border-left: 5px solid {success}; }}
            .feedback-warning {{ border-left: 5px solid {warning}; }}
            .feedback-error {{ border-left: 5px solid {error}; }}
            .feedback-info {{ border-left: 5px solid {info}; }}

            .feedback-icon {{
                font-size: 1.5rem;
                flex-shrink: 0;
            }}
            
            .feedback-content h4 {{
                margin: 0 0 4px 0 !important;
                font-size: 1rem !important;
                font-weight: 700 !important;
                color: inherit !important;
            }}
            
            .feedback-content p {{
                margin: 0 !important;
                font-size: 0.88rem !important;
                opacity: 0.9 !important;
                line-height: 1.5 !important;
            }}
        </style>
    """)

def render_success_card(title: str, message: str):
    """Render a premium success feedback card."""
    title = _sanitize(title)
    message = _sanitize(message)
    
    html = f"""
<div class="premium-card feedback-card feedback-success" style="transform: scale(1.02); box-shadow: 0 10px 20px rgba(16, 185, 129, 0.1);">
<div class="feedback-icon">✅</div>
<div class="feedback-content">
<h4>{title}</h4>
<p>{message}</p>
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

def render_warning_card(title: str, message: str):
    """Render a premium warning feedback card."""
    title = _sanitize(title)
    message = _sanitize(message)
    
    html = f"""
<div class="premium-card feedback-card feedback-warning">
<div class="feedback-icon">⚠️</div>
<div class="feedback-content">
<h4>{title}</h4>
<p>{message}</p>
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

def render_error_card(title: str, message: str, error_code: str = None, retry_callback=None):
    """Render a premium error feedback card with optional retry."""
    title = _sanitize(title)
    message = _sanitize(message)
    code_html = f"<br><code style='background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 4px; font-size: 0.75rem;'>Code: {error_code}</code>" if error_code else ""
    
    html = f"""
<div class="premium-card feedback-card feedback-error">
<div class="feedback-icon">❌</div>
<div class="feedback-content">
<h4>{title}</h4>
<p>{message}{code_html}</p>
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)
    
    if retry_callback:
        if st.button("🔄 Try Again", help="Attempt to reconnect or restart task"):
            retry_callback()

def render_connection_error():
    """Specific error for backend offline state."""
    render_error_card(
        "Backend Offline", 
        "The ScholarPulse backend server could not be reached. Please ensure the Django server is running on port 8000.",
        "CONN_REFUSED"
    )

def render_progress_card(progress: int, step_text: str, theme: str = "Dark"):
    """Render a modern progress indicator with premium styling."""
    accent = "#8B5CF6" if theme == "Dark" else "#6366F1" if theme == "Night" else "#7C3AED"
    bg = "rgba(139, 92, 246, 0.1)"
    
    step_text = _sanitize(step_text)
    
    html = f"""
<div class="premium-card" style="padding: 24px; margin-bottom: 24px; animation: fadeInUp 0.5s ease-out;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
<span style="font-weight: 700; font-size: 0.95rem; letter-spacing: 0.5px; color: {accent};">AGENT MISSION IN PROGRESS</span>
<span style="font-weight: 800; font-size: 1rem; color: {accent};">{progress}%</span>
</div>
<div style="width: 100%; background: {bg}; height: 10px; border-radius: 5px; overflow: hidden; margin-bottom: 16px; border: 1px solid {accent}20;">
<div style="width: {progress}%; background: linear-gradient(90deg, {accent}, #D8B4FE); height: 100%; border-radius: 5px; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);"></div>
</div>
<div style="display: flex; align-items: center; gap: 12px;">
<div class="status-dot pulsing" style="background: {accent}; width: 8px; height: 8px;"></div>
<div style="font-size: 0.9rem; opacity: 0.9; font-weight: 500;">{step_text}</div>
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)
