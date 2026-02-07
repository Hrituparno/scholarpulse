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
    Render a modern paper result card with premium motion.
    
    Args:
        paper: Paper dict with title, summary, authors, pdf_url, etc.
        theme: Color theme
        index: Card index for animation delay
    """
    accent = "#8B5CF6" if theme == "Dark" else "#6366F1" if theme == "Night" else "#7C3AED"
    text_color = "#F1F5F9" if theme != "Light" else "#18181B"
    muted = "#94A3B8" if theme != "Light" else "#52525B"
    border = f"{accent}20"
    
    title = _sanitize(paper.get('title', 'Untitled'))
    summary = _sanitize(paper.get('summary', 'No summary available.'))[:280]
    authors = [_sanitize(a) for a in paper.get('authors', [])]
    author_str = ', '.join(authors[:3]) + ('...' if len(authors) > 3 else '')
    pdf_url = paper.get('pdf_url', '#')
    scholar_url = paper.get('google_scholar_url', '#')
    objective = _sanitize(paper.get('objective', 'N/A'))
    method = _sanitize(paper.get('method', 'N/A'))
    
    # Generate styled tags
    method_pill = _get_paper_pill_html(method, accent)
    
    # CRITICAL: NO INDENTATION in the multiline string for st.markdown
    html = f"""
<div class="premium-card" style="animation-delay: {index * 0.1}s; display: flex; flex-direction: column;">
<h4 style="margin: 0 0 12px 0; font-size: 1.15rem; font-weight: 700; color: {text_color}; line-height: 1.3;">{title}</h4>
<div style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;">{method_pill}</div>
<p style="color: {muted}; font-size: 0.85rem; margin-bottom: 10px; line-height: 1.6;"><strong style="color: {text_color}; font-weight: 600;">Objective:</strong> {objective}</p>
<p style="color: {muted}; font-size: 0.85rem; margin-bottom: 16px; line-height: 1.6; opacity: 0.9;">{summary}...</p>
<div style="display: flex; justify-content: space-between; align-items: center; padding-top: 14px; border-top: 1px solid {border}; margin-top: auto;">
<span style="font-size: 0.75rem; color: {muted}; font-weight: 500;">👤 {author_str}</span>
<div style="display: flex; gap: 16px;">
<a href="{pdf_url}" target="_blank" style="color: {accent}; text-decoration: none; font-size: 0.82rem; font-weight: 600; transition: opacity 0.2s;">📄 PDF</a>
<a href="{scholar_url}" target="_blank" style="color: {accent}; text-decoration: none; font-size: 0.82rem; font-weight: 600; transition: opacity 0.2s;">🎓 Scholar</a>
</div>
</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)


def render_idea_card(idea: Dict, theme: str = "Dark", index: int = 0):
    """
    Render a research idea card with pink accent and motion.
    
    Args:
        idea: Idea dict with title, description, requirements
        theme: Color theme
        index: Card index
    """
    accent = "#EC4899"  # Pink for ideas
    text_color = "#F1F5F9" if theme != "Light" else "#18181B"
    muted = "#94A3B8" if theme != "Light" else "#52525B"
    
    title = _sanitize(idea.get('title', 'Untitled Idea'))
    description = _sanitize(idea.get('description', ''))
    raw_requirements = idea.get('requirements', [])
    
    # Process requirements into tags
    if isinstance(raw_requirements, str):
        requirements = [r.strip() for r in raw_requirements.split(',')]
    else:
        requirements = [str(r) for r in raw_requirements]
    
    req_tags_html = "".join([
        f'<span class="premium-tag" style="background: {accent}10; color: {accent}; border: 1px solid {accent}30; margin-right: 6px; margin-bottom: 4px; display: inline-block;">{_sanitize(r)}</span>'
        for r in requirements[:4]
    ])
    
    # CRITICAL: NO INDENTATION in the multiline string
    html = f"""
<div class="premium-card" style="border-left: 4px solid {accent}; animation-delay: {index * 0.15}s; height: 100%; display: flex; flex-direction: column;">
<h4 style="margin: 0 0 10px 0; font-size: 1.05rem; font-weight: 700; color: {text_color};">💡 {title}</h4>
<p style="color: {muted}; font-size: 0.85rem; margin-bottom: 12px; line-height: 1.6; flex-grow: 1; opacity: 0.9;">{description}</p>
<div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px;">{req_tags_html}</div>
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
