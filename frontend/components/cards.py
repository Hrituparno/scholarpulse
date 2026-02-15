"""
Result Card Components for ScholarPulse UI.

Modern, enterprise-grade paper and idea display cards.
"""
import streamlit as st
import textwrap
import re
from typing import Dict, List, Optional


def _sanitize(text: str) -> str:
    """Sanitize raw agent text to prevent HTML/Markdown breakage."""
    if not text:
        return ""
    # Remove common artifacts that might trigger Markdown code blocks
    s = str(text).replace("```", "").replace("`", "")
    # Escape some basic HTML sensitive chars if needed, though we trust our template structure
    s = s.replace("<", "&lt;").replace(">", "&gt;")
    return s.strip()


def _get_paper_pill_html(text: str, accent_color: str) -> str:
    """Generate HTML for a styled premium tag."""
    clean_text = _sanitize(text)
    return f"""<span class="premium-tag" style="background: {accent_color}15; color: {accent_color}; border: 1px solid {accent_color}30; margin-bottom: 4px; display: inline-block;">{clean_text}</span>"""


def render_paper_card(paper: Dict, theme: str = "Dark", index: int = 0):
    """
    Render an enhanced paper result card with ChatGPT/Gemini-style visual hierarchy.
    Includes paper thumbnail, better sections, and smooth interactions.
    """
    accent = "#8B5CF6" if theme == "Dark" else "#6366F1" if theme == "Night" else "#7C3AED"
    text_color = "#F1F5F9" if theme != "Light" else "#18181B"
    muted = "#94A3B8" if theme != "Light" else "#52525B"
    border = f"{accent}20"
    bg_hover = f"{accent}08"
    
    title = _sanitize(paper.get('title', 'Untitled'))
    summary = _sanitize(paper.get('summary', 'No summary available.'))
    authors = [_sanitize(a) for a in paper.get('authors', [])]
    author_str = ", ".join(authors[:2]) if len(authors) > 1 else (authors[0] if authors else "Unknown")
    if len(authors) > 2:
        author_str += f" +{len(authors) - 2} more"
    
    year = paper.get('year', '2024')
    source = _sanitize(paper.get('source', 'arXiv'))
    
    pdf_url = paper.get('pdf_url', '#')
    scholar_url = paper.get('google_scholar_url', '#')
    objective = _sanitize(paper.get('objective', 'N/A'))
    method = _sanitize(paper.get('method', 'N/A'))
    tools = _sanitize(paper.get('tools', 'N/A'))
    results = _sanitize(paper.get('results', 'N/A'))
    
    # Generate paper thumbnail using placeholder service (based on title hash)
    title_hash = abs(hash(title)) % 1000
    thumbnail_url = f"https://picsum.photos/seed/{title_hash}/400/250"
    
    # Extract key insights
    sentences = [s.strip() for s in re.split(r'[.!?]', summary) if len(s.strip()) > 15]
    insights = sentences[:2]
    
    # Build metadata badges
    metadata_badges = f"""
<div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
    <span style="background: {accent}15; color: {accent}; padding: 4px 10px; border-radius: 16px; font-size: 0.7rem; font-weight: 700; display: flex; align-items: center; gap: 4px;">
        <span>👤</span> {author_str}
    </span>
    <span style="background: {accent}15; color: {accent}; padding: 4px 10px; border-radius: 16px; font-size: 0.7rem; font-weight: 700; display: flex; align-items: center; gap: 4px;">
        <span>📅</span> {year}
    </span>
    <span style="background: {accent}15; color: {accent}; padding: 4px 10px; border-radius: 16px; font-size: 0.7rem; font-weight: 700; display: flex; align-items: center; gap: 4px;">
        <span>🌐</span> {source}
    </span>
</div>
"""
    
    # Build expandable sections
    sections_html = f"""
<details style="cursor: pointer; margin: 12px 0; background: {bg_hover}; padding: 12px; border-radius: 8px; border: 1px solid {border};">
    <summary style="font-size: 0.85rem; font-weight: 700; color: {accent}; outline: none; list-style: none; display: flex; align-items: center; gap: 6px;">
        <span>📝</span> Abstract
    </summary>
    <p style="color: {muted}; font-size: 0.88rem; margin-top: 12px; line-height: 1.7; opacity: 0.95;">{summary}</p>
</details>

<details style="cursor: pointer; margin: 12px 0; background: {bg_hover}; padding: 12px; border-radius: 8px; border: 1px solid {border};">
    <summary style="font-size: 0.85rem; font-weight: 700; color: {accent}; outline: none; list-style: none; display: flex; align-items: center; gap: 6px;">
        <span>🎯</span> Objective & Method
    </summary>
    <div style="margin-top: 12px;">
        <p style="color: {text_color}; font-size: 0.85rem; margin-bottom: 8px;"><strong>Objective:</strong> {objective}</p>
        <p style="color: {text_color}; font-size: 0.85rem; margin-bottom: 8px;"><strong>Method:</strong> {method}</p>
        <p style="color: {text_color}; font-size: 0.85rem;"><strong>Tools:</strong> {tools}</p>
    </div>
</details>

<details style="cursor: pointer; margin: 12px 0; background: {bg_hover}; padding: 12px; border-radius: 8px; border: 1px solid {border};">
    <summary style="font-size: 0.85rem; font-weight: 700; color: {accent}; outline: none; list-style: none; display: flex; align-items: center; gap: 6px;">
        <span>📊</span> Results
    </summary>
    <p style="color: {muted}; font-size: 0.88rem; margin-top: 12px; line-height: 1.7;">{results}</p>
</details>
"""
    
    # Key insights chips
    insights_html = ""
    if insights:
        chips = "".join([f'<div style="background: {accent}10; color: {text_color}; padding: 8px 12px; border-radius: 8px; font-size: 0.8rem; line-height: 1.4; border-left: 3px solid {accent};">💡 {i}</div>' for i in insights])
        insights_html = f"""
<div style="margin: 16px 0;">
    <div style="font-size: 0.75rem; font-weight: 800; color: {accent}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Key Insights</div>
    <div style="display: flex; flex-direction: column; gap: 8px;">{chips}</div>
</div>
"""
    
    # Main card HTML
    html = f"""
<div class="premium-card" style="animation-delay: {index * 0.1}s; overflow: hidden; transition: transform 0.3s ease, box-shadow 0.3s ease;">
    <div style="width: 100%; height: 180px; background: linear-gradient(135deg, {accent}40, {accent}20), url('{thumbnail_url}'); background-size: cover; background-position: center; border-radius: 12px; margin-bottom: 16px; position: relative;">
        <div style="position: absolute; top: 12px; right: 12px; background: rgba(0,0,0,0.7); backdrop-filter: blur(10px); padding: 6px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; color: white; text-transform: uppercase;">
            {source}
        </div>
    </div>
    
    <h4 style="margin: 0 0 12px 0; font-size: 1.2rem; font-weight: 800; color: {text_color}; line-height: 1.3; letter-spacing: -0.02em;">{title}</h4>
    
    {metadata_badges}
    {insights_html}
    {sections_html}
    
    <div style="display: flex; gap: 12px; padding-top: 16px; border-top: 1px solid {border}; margin-top: 16px;">
        <a href="{pdf_url}" target="_blank" style="flex: 1; background: {accent}; color: white; text-decoration: none; font-size: 0.85rem; font-weight: 700; padding: 10px; border-radius: 8px; text-align: center; transition: opacity 0.2s; display: flex; align-items: center; justify-content: center; gap: 6px;">
            <span>📄</span> View PDF
        </a>
        <a href="{scholar_url}" target="_blank" style="flex: 1; background: {bg_hover}; color: {accent}; text-decoration: none; font-size: 0.85rem; font-weight: 700; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid {border}; transition: opacity 0.2s; display: flex; align-items: center; justify-content: center; gap: 6px;">
            <span>🎓</span> Scholar
        </a>
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def render_idea_card(idea: Dict, theme: str = "Dark", index: int = 0):
    """
    Render an enhanced research idea card with ChatGPT/Gemini-style design.
    Includes gradient background, better sections, and visual appeal.
    """
    accent = "#EC4899"  # Pink for ideas
    text_color = "#F1F5F9" if theme != "Light" else "#18181B"
    muted = "#94A3B8" if theme != "Light" else "#52525B"
    border = f"{accent}20"
    bg_hover = f"{accent}08"
    
    title = _sanitize(idea.get('title', 'Untitled Idea'))
    description = _sanitize(idea.get('description', ''))
    raw_requirements = idea.get('requirements', [])
    complexity = idea.get('complexity', 'Medium')
    
    # Process requirements into tags
    if isinstance(raw_requirements, str):
        requirements = [r.strip() for r in raw_requirements.split(',')]
    else:
        requirements = [str(r) for r in raw_requirements]
    
    # Generate idea thumbnail (gradient with icon)
    gradient_colors = [
        ("135deg, #EC4899, #8B5CF6"),
        ("135deg, #F59E0B, #EF4444"),
        ("135deg, #10B981, #3B82F6"),
        ("135deg, #8B5CF6, #EC4899"),
        ("135deg, #6366F1, #8B5CF6")
    ]
    gradient = gradient_colors[index % len(gradient_colors)]
    
    # Requirements badges
    req_badges = "".join([
        f'<span style="background: {accent}15; color: {accent}; padding: 6px 12px; border-radius: 16px; font-size: 0.75rem; font-weight: 700; display: inline-flex; align-items: center; gap: 4px; margin-right: 6px; margin-bottom: 6px; border: 1px solid {accent}30;">🛠️ {_sanitize(r)}</span>'
        for r in requirements[:4]
    ])
    
    # Complexity indicator
    complexity_colors = {
        "Low": "#10B981",
        "Medium": "#F59E0B",
        "High": "#EF4444"
    }
    complexity_color = complexity_colors.get(complexity, "#F59E0B")
    
    html = f"""
<div class="premium-card" style="border-left: 4px solid {accent}; animation-delay: {index * 0.12}s; overflow: hidden; transition: transform 0.3s ease, box-shadow 0.3s ease; position: relative;">
    <div style="width: 100%; height: 120px; background: linear-gradient({gradient}); border-radius: 12px; margin-bottom: 16px; display: flex; align-items: center; justify-content: center; position: relative;">
        <div style="font-size: 3rem; opacity: 0.9;">💡</div>
        <div style="position: absolute; top: 12px; right: 12px; background: rgba(0,0,0,0.7); backdrop-filter: blur(10px); padding: 6px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; color: white; text-transform: uppercase;">
            RESEARCH IDEA
        </div>
        <div style="position: absolute; bottom: 12px; left: 12px; background: {complexity_color}; color: white; padding: 4px 10px; border-radius: 16px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase;">
            {complexity} COMPLEXITY
        </div>
    </div>
    
    <h4 style="margin: 0 0 12px 0; font-size: 1.15rem; font-weight: 800; color: {text_color}; line-height: 1.3; display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.3rem;">🚀</span> {title}
    </h4>
    
    <p style="color: {muted}; font-size: 0.9rem; margin-bottom: 20px; line-height: 1.7; opacity: 0.95;">{description}</p>
    
    <div style="background: {bg_hover}; padding: 16px; border-radius: 12px; border: 1px solid {border}; margin-bottom: 16px;">
        <div style="font-size: 0.75rem; font-weight: 800; color: {accent}; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; display: flex; align-items: center; gap: 6px;">
            <span>🔧</span> Prerequisites & Tools
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 6px;">{req_badges}</div>
    </div>
    
    <div style="display: flex; gap: 12px; align-items: center; padding-top: 16px; border-top: 1px solid {border};">
        <div style="flex: 1; display: flex; align-items: center; gap: 8px; font-size: 0.8rem; color: {muted};">
            <span style="font-size: 1.2rem;">🧠</span>
            <span style="font-weight: 600;">High Research Potential</span>
        </div>
        <div style="background: {accent}; color: white; padding: 8px 16px; border-radius: 8px; font-size: 0.75rem; font-weight: 800; cursor: pointer; transition: opacity 0.2s;">
            EXPLORE →
        </div>
    </div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def render_papers_grid(papers: List[Dict], theme: str = "Dark"):
    """Render papers in a 2-column grid with ChatGPT-style section header."""
    if not papers:
        st.info("No papers found for this query.")
        return
    
    accent = "#8B5CF6" if theme == "Dark" else "#6366F1"
    text_color = "#F1F5F9" if theme != "Light" else "#18181B"
    
    # Section header
    st.markdown(f"""
<div style="margin: 40px 0 24px 0;">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <div style="font-size: 2rem;">📚</div>
        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: {text_color}; background: linear-gradient(135deg, {accent}, #EC4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Research Papers
        </h2>
        <div style="background: {accent}15; color: {accent}; padding: 4px 12px; border-radius: 16px; font-size: 0.75rem; font-weight: 800;">
            {len(papers)} FOUND
        </div>
    </div>
    <p style="color: #94A3B8; font-size: 0.95rem; margin: 0;">
        Curated academic papers from leading research databases
    </p>
</div>
""", unsafe_allow_html=True)
    
    cols = st.columns(2)
    for idx, paper in enumerate(papers):
        with cols[idx % 2]:
            render_paper_card(paper, theme, idx)


def render_ideas_list(ideas: List[Dict], theme: str = "Dark"):
    """Render ideas in a single column list with ChatGPT-style section header."""
    if not ideas:
        st.info("No research ideas generated.")
        return
    
    accent = "#EC4899"
    text_color = "#F1F5F9" if theme != "Light" else "#18181B"
    
    # Section header
    st.markdown(f"""
<div style="margin: 48px 0 24px 0;">
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <div style="font-size: 2rem;">💡</div>
        <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: {text_color}; background: linear-gradient(135deg, {accent}, #F59E0B); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Research Ideas
        </h2>
        <div style="background: {accent}15; color: {accent}; padding: 4px 12px; border-radius: 16px; font-size: 0.75rem; font-weight: 800;">
            {len(ideas)} GENERATED
        </div>
    </div>
    <p style="color: #94A3B8; font-size: 0.95rem; margin: 0;">
        AI-generated novel research directions based on analyzed papers
    </p>
</div>
""", unsafe_allow_html=True)
    
    for idx, idea in enumerate(ideas):
        render_idea_card(idea, theme, idx)
