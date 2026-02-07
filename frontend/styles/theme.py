"""
Premium Theme CSS for ScholarPulse UI.

Aurora Minimal Color Palette with advanced SaaS aesthetics and motion-enhanced interactions.
"""
import textwrap


def get_theme_css(theme: str = "Dark") -> str:
    """Get complete CSS for the selected premium theme."""
    
    # Aurora Minimal Color Palette
    primary_gradient = "linear-gradient(135deg, #6366F1, #8B5CF6)"
    accent_pink = "#EC4899"
    accent_amber = "#F59E0B"
    
    if theme == "Dark":
        bg_color = "#0F0F23"
        card_bg = "rgba(30, 30, 60, 0.4)"
        card_hover_bg = "rgba(40, 40, 80, 0.6)"
        sidebar_bg = "linear-gradient(180deg, #15152E 0%, #0F0F23 100%)"
        text_primary = "#F1F5F9"
        text_muted = "#94A3B8"
        accent = "#8B5CF6"
        border_color = "rgba(139, 92, 246, 0.12)"
        shadow_accent = "rgba(139, 92, 246, 0.2)"
    elif theme == "Night":
        bg_color = "#09090B"
        card_bg = "rgba(24, 24, 27, 0.6)"
        card_hover_bg = "rgba(32, 32, 35, 0.8)"
        sidebar_bg = "linear-gradient(180deg, #121214 0%, #09090B 100%)"
        text_primary = "#FAFAFA"
        text_muted = "#71717A"
        accent = "#6366F1"
        border_color = "rgba(99, 102, 241, 0.12)"
        shadow_accent = "rgba(99, 102, 241, 0.2)"
    else:  # Light
        bg_color = "#F8FAFC"
        card_bg = "rgba(255, 255, 255, 0.7)"
        card_hover_bg = "rgba(255, 255, 255, 0.9)"
        sidebar_bg = "linear-gradient(180deg, #EFF6FF 0%, #F8FAFC 100%)"
        text_primary = "#1E293B"
        text_muted = "#64748B"
        accent = "#7C3AED"
        border_color = "rgba(124, 58, 237, 0.08)"
        shadow_accent = "rgba(124, 58, 237, 0.15)"
    
    return textwrap.dedent(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Base Reset & Typography */
            .stApp {{ 
                background: {bg_color};
                color: {text_primary};
                font-family: 'Outfit', 'Inter', sans-serif;
            }}
            
            h1, h2, h3, h4, h5 {{ font-family: 'Outfit', sans-serif !important; letter-spacing: -0.02em; }}
            p, span, div {{ font-family: 'Inter', sans-serif; }}

            /* Global Motion Rules */
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(16px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            @keyframes glowPulse {{
                0% {{ box-shadow: 0 0 5px {shadow_accent}; }}
                50% {{ box-shadow: 0 0 20px {shadow_accent}; }}
                100% {{ box-shadow: 0 0 5px {shadow_accent}; }}
            }}
            
            @keyframes slideInSide {{
                from {{ transform: translateX(-20px); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}

            /* Reduced Motion Support */
            @media (prefers-reduced-motion: reduce) {{
                * {{
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                    scroll-behavior: auto !important;
                }}
            }}

            /* Refined Sidebar */
            [data-testid="stSidebar"] {{
                background: {sidebar_bg} !important;
                border-right: 1px solid {border_color};
            }}
            
            [data-testid="stSidebar"] section {{ padding-top: 2rem; }}
            
            /* Sidebar Branding Animation */
            .sidebar-logo-container {{
                transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 12px;
                padding: 1rem 0;
            }}
            .sidebar-logo-container:hover {{ transform: scale(1.05); }}

            /* Sidebar Navigation Items */
            .nav-item {{
                padding: 10px 16px;
                border-radius: 12px;
                margin: 4px 12px;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 12px;
                color: {text_muted};
                font-weight: 500;
                font-size: 0.92rem;
                position: relative;
                overflow: hidden;
            }}
            
            .nav-item:hover {{
                background: {accent}10;
                color: {text_primary} !important;
                padding-left: 20px;
            }}
            
            .nav-active {{
                background: {primary_gradient} !important;
                color: white !important;
                box-shadow: 0 4px 12px {shadow_accent};
            }}
            
            .nav-active::after {{
                content: '';
                position: absolute;
                left: 0;
                top: 20%;
                height: 60%;
                width: 4px;
                background: white;
                border-radius: 0 4px 4px 0;
            }}

            /* Premium Bento Cards */
            .premium-card {{
                background: {card_bg};
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border-radius: 20px;
                border: 1px solid {border_color};
                padding: 24px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                animation: fadeInUp 0.6s ease-out forwards;
            }}
            
            .premium-card:hover {{
                transform: translateY(-5px) scale(1.01);
                background: {card_hover_bg};
                border-color: {accent}40;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2), 0 0 15px {shadow_accent};
            }}

            /* Modern Inputs & Focus States */
            .stTextInput>div>div>input {{
                background: {card_bg} !important;
                border: 1px solid {border_color} !important;
                border-radius: 14px !important;
                color: {text_primary} !important;
                padding: 12px 18px !important;
                transition: all 0.3s ease !important;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.05) !important;
            }}
            
            .stTextInput>div>div>input:focus {{
                border-color: {accent} !important;
                box-shadow: 0 0 0 4px {shadow_accent} !important;
                transform: scale(1.005);
            }}

            /* Upgraded Buttons */
            .stButton>button {{
                background: {primary_gradient} !important;
                border: none !important;
                color: white !important;
                font-weight: 600 !important;
                border-radius: 14px !important;
                padding: 14px 28px !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                text-transform: none !important;
                letter-spacing: 0.3px !important;
                box-shadow: 0 4px 15px {shadow_accent} !important;
            }}
            
            .stButton>button:hover {{
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 25px {shadow_accent} !important;
                filter: brightness(1.1);
            }}
            
            .stButton>button:active {{
                transform: translateY(0px) scale(0.98) !important;
            }}

            /* Custom Tags/Pills */
            .premium-tag {{
                padding: 4px 10px;
                border-radius: 8px;
                font-size: 0.72rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                transition: all 0.2s ease;
            }}
            .premium-tag:hover {{
                transform: scale(1.1);
                filter: brightness(1.2);
            }}

            /* Elegant Scrollbar */
            ::-webkit-scrollbar {{ width: 6px; }}
            ::-webkit-scrollbar-track {{ background: transparent; }}
            ::-webkit-scrollbar-thumb {{ 
                background: {accent}25; 
                border-radius: 10px; 
            }}
            ::-webkit-scrollbar-thumb:hover {{ background: {accent}40; }}

            /* Page Loader & Utilities */
            .content-section {{
                animation: fadeInUp 0.8s ease-out;
            }}
            
            .gradient-text {{
                background: {primary_gradient};
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 800 !important;
            }}
            
            .stDivider {{ border-color: {border_color} !important; margin: 2rem 0 !important; }}
            
            /* Navbar Stickiness & Glow */
            .top-navbar {{
                background: {bg_color}cc !important;
                backdrop-filter: blur(20px);
                box-shadow: 0 4px 30px rgba(0,0,0,0.1);
            }}

            /* Settings Interface (ChatGPT-Style) */
            .settings-container {{
                display: flex;
                gap: 24px;
                background: {card_bg};
                border-radius: 24px;
                border: 1px solid {border_color};
                min-height: 500px;
                overflow: hidden;
                margin-top: 20px;
                animation: fadeInUp 0.7s ease-out;
            }}
            
            .settings-menu {{
                width: 240px;
                background: rgba(0,0,0,0.15);
                border-right: 1px solid {border_color};
                padding: 16px 8px;
                display: flex;
                flex-direction: column;
                gap: 4px;
            }}
            
            .settings-menu-item {{
                padding: 10px 16px;
                border-radius: 10px;
                color: {text_muted};
                font-weight: 500;
                font-size: 0.88rem;
                transition: all 0.2s ease;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .settings-menu-item:hover {{
                background: rgba(255,255,255,0.05);
                color: {text_primary};
            }}
            
            .settings-menu-item.active {{
                background: {accent}10;
                color: {accent};
                font-weight: 600;
            }}
            
            .settings-pane {{
                flex: 1;
                padding: 32px;
                overflow-y: auto;
                background: transparent;
            }}
            
            .settings-header {{
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 24px;
                color: {text_primary};
            }}
            
            .settings-section {{
                margin-bottom: 32px;
                padding-bottom: 24px;
                border-bottom: 1px solid {border_color};
            }}
            
            .settings-section:last-child {{ border-bottom: none; }}
            
            .settings-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
            }}
            
            .settings-label-group {{
                display: flex;
                flex-direction: column;
                gap: 4px;
            }}
            
            .settings-label {{
                font-weight: 600;
                font-size: 0.95rem;
                color: {text_primary};
            }}
            
            .settings-description {{
                font-size: 0.82rem;
                color: {text_muted};
                max-width: 450px;
            }}

            /* Empty States */
            .empty-state-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 60px 20px;
                text-align: center;
            }}
            .empty-state-icon {{
                font-size: 4rem;
                margin-bottom: 24px;
                opacity: 0.5;
                filter: grayscale(0.5);
            }}
            .empty-state-title {{
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 12px;
                color: {text_primary};
            }}
            .empty-state-description {{
                font-size: 1rem;
                color: {text_muted};
                max-width: 400px;
                line-height: 1.6;
            }}
        </style>
    """)


def get_color_scheme(theme: str = "Dark") -> dict:
    """Get color scheme dict for the theme."""
    if theme == "Dark":
        return {
            "bg": "#0F0F23",
            "card": "rgba(30, 30, 60, 0.4)",
            "text": "#F1F5F9",
            "muted": "#94A3B8",
            "accent": "#8B5CF6",
            "border": "rgba(139, 92, 246, 0.12)",
        }
    elif theme == "Night":
        return {
            "bg": "#09090B",
            "card": "rgba(24, 24, 27, 0.6)",
            "text": "#FAFAFA",
            "muted": "#71717A",
            "accent": "#6366F1",
            "border": "rgba(99, 102, 241, 0.12)",
        }
    else:
        return {
            "bg": "#F8FAFC",
            "card": "rgba(255, 255, 255, 0.7)",
            "text": "#1E293B",
            "muted": "#64748B",
            "accent": "#7C3AED",
            "border": "rgba(124, 58, 237, 0.08)",
        }
