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
    Render an enhanced paper result card with visual hierarchy and key insights.
    """
    accent = "#8B5CF6" if theme == "Dark" else "#6366F1" if theme == "Night" else "#7C3AED"
    text_color = "#F1F5F9" if theme != "Light" else "#18181B"
    muted = "#94A3B8" if theme != "Light" else "#52525B"
    border = f"{accent}20"
    
    title = _sanitize(paper.get('title', 'Untitled'))
    summary = _sanitize(paper.get('summary', 'No summary available.'))
    authors = [_sanitize(a) for a in paper.get('authors', [])]
    author_str = authors[0] if authors else "Unknown"
    year = paper.get('year', '2024')
    source = _sanitize(paper.get('source', 'Scholar'))
    
    pdf_url = paper.get('pdf_url', '#')
    scholar_url = paper.get('google_scholar_url', '#')
    objective = _sanitize(paper.get('objective', 'N/A'))
    method = _sanitize(paper.get('method', 'N/A'))
    
    # Extract "Key Insights" from summary (split into sentences and take first 2)
    sentences = [s.strip() for s in re.split(r'[.!?]', summary) if len(s.strip()) > 10]
    insights = sentences[:3]
    insight_chips_html = "".join([f'<div class="insight-chip">{i[:40]}...</div>' for i in insights])
    
    # Generate metadata row
    metadata_html = f"""
<div class="card-metadata">
<span>👤 {author_str}</span>
<span>📅 {year}</span>
<span>🌐 {source}</span>
</div>
"""
    
    # CRITICAL: NO INDENTATION in the multiline string for st.markdown
    html = f"""
<div class="premium-card" style="animation-delay: {index * 0.1}s; display: flex; flex-direction: column;">
<h4 style="margin: 0 0 8px 0; font-size: 1.25rem; font-weight: 800; color: {text_color}; line-height: 1.2; letter-spacing: -0.02em;">{title}</h4>
{metadata_html}
<div style="display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;">{_get_paper_pill_html(method, accent)}</div>

<details style="cursor: pointer; margin-bottom: 16px;">
<summary style="font-size: 0.85rem; font-weight: 700; color: {accent}; margin-bottom: 8px; outline: none; list-style: none;">🔍 READ SUMMARY</summary>
<p style="color: {muted}; font-size: 0.9rem; margin-top: 8px; line-height: 1.6; opacity: 0.95;">{summary}</p>
</details>

<div class="insight-highlights">
<div class="insight-title">💡 KEY HIGHLIGHTS</div>
<div class="insight-chips">{insight_chips_html}</div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; padding-top: 16px; border-top: 1px solid {border}; margin-top: auto;">
<div style="display: flex; gap: 16px;">
<a href="{pdf_url}" target="_blank" style="color: {accent}; text-decoration: none; font-size: 0.85rem; font-weight: 700; display: flex; align-items: center; gap: 4px; transition: opacity 0.2s;">
<span style="font-size: 1rem;">📄</span> PDF
</a>
<a href="{scholar_url}" target="_blank" style="color: {accent}; text-decoration: none; font-size: 0.85rem; font-weight: 700; display: flex; align-items: center; gap: 4px; transition: opacity 0.2s;">
<span style="font-size: 1rem;">🎓</span> SCHOLAR
</a>
</div>
<div style="background: {accent}10; color: {accent}; padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 800; text-transform: uppercase;">
ACTIVE
</div>
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def render_idea_card(idea: Dict, theme: str = "Dark", index: int = 0):
    """
    Render an enhanced research idea card with pink accent and depth indicator.
    """
    accent = "#EC4899"  # Pink for ideas
    text_color = "#F1F5F9" if theme != "Light" else "#18181B"
    muted = "#94A3B8" if theme != "Light" else "#52525B"
    
    title = _sanitize(idea.get('title', 'Untitled Idea'))
    description = _sanitize(idea.get('description', ''))
    raw_requirements = idea.get('requirements', [])
    complexity = idea.get('complexity', 'Medium')
    
    # Process requirements into tags
    if isinstance(raw_requirements, str):
        requirements = [r.strip() for r in raw_requirements.split(',')]
    else:
        requirements = [str(r) for r in raw_requirements]
    
    req_tags_html = "".join([
        f'<span class="premium-tag" style="background: {accent}10; color: {accent}; border: 1px solid {accent}30; margin-right: 6px; margin-bottom: 4px; display: inline-block;">{_sanitize(r)}</span>'
        for r in requirements[:3]
    ])
    
    # CRITICAL: NO INDENTATION in the multiline string
    html = f"""
<div class="premium-card" style="border-left: 5px solid {accent}; animation-delay: {index * 0.15}s; height: 100%; display: flex; flex-direction: column;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
<h4 style="margin: 0; font-size: 1.15rem; font-weight: 800; color: {text_color}; line-height: 1.2;">💡 {title}</h4>
<div style="background: {accent}15; color: {accent}; padding: 2px 8px; border-radius: 6px; font-size: 0.65rem; font-weight: 800;">{complexity.upper()}</div>
</div>
<p style="color: {muted}; font-size: 0.9rem; margin-bottom: 16px; line-height: 1.6; flex-grow: 1; opacity: 0.95;">{description}</p>
<div class="insight-title" style="color: {accent}; margin-bottom: 8px;">🛠️ PREREQUISITES</div>
<div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px;">{req_tags_html}</div>
<div style="margin-top: 16px; display: flex; align-items: center; gap: 8px; font-size: 0.75rem; color: {muted}; font-weight: 600;">
<span style="font-size: 1rem;">🧠</span> Research Depth: High
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def render_papers_grid(papers: List[Dict], theme: str = "Dark"):
    """Render papers in a 2-column grid."""
    if not papers:
        st.info("No papers found for this query.")
        return
    
    cols = st.columns(2)
    for idx, paper in enumerate(papers):
        with cols[idx % 2]:
            render_paper_card(paper, theme, idx)


def render_ideas_list(ideas: List[Dict], theme: str = "Dark"):
    """Render ideas in a single column list."""
    if not ideas:
        st.info("No research ideas generated.")
        return
    
    for idx, idea in enumerate(ideas):
        render_idea_card(idea, theme, idx)
