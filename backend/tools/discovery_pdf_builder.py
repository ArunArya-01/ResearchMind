import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch

def clean_text(text, preserve_breaks=False):
    """Clean markdown text for ReportLab with proper XML handling

    Args:
        text: Text to clean
        preserve_breaks: If True, preserve line breaks (for multi-line content)
    """
    if not text:
        return ""

    # Remove markdown links but keep text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

    if not preserve_breaks:
        # Normalize whitespace for single-line content
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

    # Use placeholders for markdown formatting (before any escaping)
    text = re.sub(r'\*\*(.+?)\*\*', r'__BOLD_START__\1__BOLD_END__', text)
    text = re.sub(r'\*(.+?)\*', r'__ITALIC_START__\1__ITALIC_END__', text)

    # Escape special characters for XML in content
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')

    # Replace placeholders with actual ReportLab tags
    text = text.replace('__BOLD_START__', '<b>')
    text = text.replace('__BOLD_END__', '</b>')
    text = text.replace('__ITALIC_START__', '<i>')
    text = text.replace('__ITALIC_END__', '</i>')

    return text

def extract_sections_from_markdown(markdown_content):
    """Extract structured sections from discovery report markdown"""
    sections = {
        'title': 'Discovery Report',
        'problem_statement': '',
        'hypothesis': '',
        'research_hypotheses': [],
        'empirical_grounding': '',
        'debate_summary': '',
        'novelty_verification': '',
        'architectural_flow': '',
        'research_gaps': [],
    }

    lines = markdown_content.split('\n')
    current_section = None
    current_content = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('## '):
            if current_section:
                save_section(current_section, current_content, sections)
            current_section = stripped[3:].strip().lower()
            current_content = []
        elif stripped.startswith('# '):
            sections['title'] = stripped[2:].strip()
        elif current_section:
            current_content.append(line)

    if current_section:
        save_section(current_section, current_content, sections)

    return sections

def save_section(name, content_lines, sections):
    """Save extracted section content to sections dict"""
    content = '\n'.join(content_lines).strip()
    name_lower = name.lower()

    if 'problem' in name_lower:
        sections['problem_statement'] = content
    elif 'core hypothesis' in name_lower:
        sections['hypothesis'] = content
    elif 'research hypothes' in name_lower:
        sections['research_hypotheses'] = parse_list_items(content)
    elif 'empirical' in name_lower or 'data' in name_lower or 'grounding' in name_lower:
        sections['empirical_grounding'] = content
    elif 'debate' in name_lower or 'swarm' in name_lower:
        sections['debate_summary'] = content
    elif 'novelty' in name_lower:
        sections['novelty_verification'] = content
    elif 'architectural' in name_lower or 'flow' in name_lower:
        sections['architectural_flow'] = content
    elif 'gap' in name_lower:
        sections['research_gaps'] = parse_list_items(content)

def safe_paragraph(text: str, style, max_retries: int = 2):
    """Safely create a Paragraph, falling back to plain text if formatting fails"""
    for attempt in range(max_retries):
        try:
            return Paragraph(text, style)
        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt: strip all markup and try plain text
                plain_text = re.sub(r'<[^>]+>', '', text)
                try:
                    return Paragraph(plain_text, style)
                except:
                    # Fallback: return empty spacer instead of crashing
                    return Spacer(1, 0.1*inch)
            # On first attempt failure, try removing problematic characters
            text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII
    return Spacer(1, 0.1*inch)

def parse_list_items(content):
    """Parse bullet points from content"""
    items = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith('- ') or stripped.startswith('* ') or stripped.startswith('1. '):
            items.append(stripped[2:].strip() if stripped.startswith('- ') or stripped.startswith('* ') else stripped[3:].strip())
        elif stripped and not stripped.startswith('#'):
            items.append(stripped)
    return items

def build_discovery_pdf(markdown_content: str) -> bytes:
    """Build a well-formatted PDF from discovery report markdown"""
    if not markdown_content or len(markdown_content.strip()) == 0:
        raise ValueError("No content provided for PDF generation")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="Discovery Report"
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#d90429'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#d90429'),
        spaceBefore=20,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )

    box_style = ParagraphStyle(
        'BoxStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        rightIndent=20,
        spaceBefore=10,
        spaceAfter=10,
        backColor=colors.HexColor('#f5f5f5'),
        borderWidth=1,
        borderColor=colors.HexColor('#d90429'),
        padding=10
    )

    agent_style = ParagraphStyle(
        'AgentStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#d90429'),
        spaceBefore=12,
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )

    story = []
    sections = extract_sections_from_markdown(markdown_content)

    try:
        # Title
        title_text = clean_text(sections['title'])
        if title_text.strip():
            story.append(safe_paragraph(title_text, title_style))
            story.append(Spacer(1, 0.2*inch))

        # Problem Statement
        if sections['problem_statement']:
            story.append(safe_paragraph("PROBLEM STATEMENT", section_style))
            problem_text = clean_text(sections['problem_statement'])
            if problem_text.strip():
                story.append(safe_paragraph(problem_text, box_style))

        # Core Hypothesis
        if sections['hypothesis']:
            story.append(safe_paragraph("CORE HYPOTHESIS", section_style))
            hypothesis_text = clean_text(sections['hypothesis'])
            if hypothesis_text.strip():
                story.append(safe_paragraph(hypothesis_text, box_style))

        # Research Hypotheses
        if sections['research_hypotheses']:
            story.append(safe_paragraph("RESEARCH HYPOTHESES", section_style))
            for idx, hyp in enumerate(sections['research_hypotheses'], 1):
                if hyp and hyp.strip():
                    cleaned = clean_text(hyp)
                    if cleaned.strip():
                        story.append(safe_paragraph(f"<b>{idx}.</b> {cleaned}", body_style))

        # Empirical Grounding
        if sections['empirical_grounding']:
            story.append(safe_paragraph("EMPIRICAL GROUNDING", section_style))
            empirical_text = clean_text(sections['empirical_grounding'])
            if empirical_text.strip():
                story.append(safe_paragraph(empirical_text, body_style))

        # Debate Summary
        if sections['debate_summary']:
            story.append(safe_paragraph("SWARM DEBATE SUMMARY", section_style))
            debate_lines = sections['debate_summary'].split('\n')
            for line in debate_lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if 'Visionary' in stripped or 'Agent Alpha' in stripped:
                    if ':' in stripped:
                        content = stripped.split(':', 1)[1].strip()
                        cleaned = clean_text(content, preserve_breaks=False)
                        if cleaned.strip():
                            story.append(safe_paragraph("<b>Visionary Agent:</b>", agent_style))
                            story.append(safe_paragraph(cleaned, body_style))
                elif 'Skeptic' in stripped or 'Agent Beta' in stripped:
                    if ':' in stripped:
                        content = stripped.split(':', 1)[1].strip()
                        cleaned = clean_text(content, preserve_breaks=False)
                        if cleaned.strip():
                            story.append(safe_paragraph("<b>Skeptic Agent:</b>", agent_style))
                            story.append(safe_paragraph(cleaned, body_style))
                elif 'Resolution' in stripped:
                    content = stripped.replace('Resolution', '').replace('**', '').strip()
                    cleaned = clean_text(content, preserve_breaks=False)
                    if cleaned.strip():
                        story.append(safe_paragraph("<b>Resolution:</b>", agent_style))
                        story.append(safe_paragraph(cleaned, body_style))
                elif stripped:
                    cleaned = clean_text(stripped, preserve_breaks=False)
                    if cleaned.strip():
                        story.append(safe_paragraph(cleaned, body_style))

        # Novelty Verification
        if sections['novelty_verification']:
            story.append(safe_paragraph("NOVELTY VERIFICATION", section_style))
            novelty_text = clean_text(sections['novelty_verification'])
            if novelty_text.strip():
                story.append(safe_paragraph(novelty_text, body_style))

        # Architectural Flow
        if sections['architectural_flow']:
            story.append(safe_paragraph("ARCHITECTURAL FLOW", section_style))
            flow_lines = []
            for line in sections['architectural_flow'].split('\n'):
                stripped = line.strip()
                if stripped and not stripped.startswith('graph') and not stripped.startswith('mermaid') and not stripped.startswith('```'):
                    flow_lines.append(stripped)
            if flow_lines:
                flow_text = clean_text('\n'.join(flow_lines), preserve_breaks=True)
                if flow_text.strip():
                    story.append(safe_paragraph(flow_text, body_style))

        # Research Gaps
        if sections['research_gaps']:
            story.append(safe_paragraph("RESEARCH GAPS", section_style))
            for idx, gap in enumerate(sections['research_gaps'], 1):
                if gap and gap.strip():
                    cleaned = clean_text(gap)
                    if cleaned.strip():
                        story.append(safe_paragraph(f"• {cleaned}", body_style))

        if not story:
            # Ensure at least some content if parsing fails
            story.append(safe_paragraph("No content available", body_style))

        doc.build(story)
        pdf_bytes = buf.getvalue()

        if not pdf_bytes or len(pdf_bytes) == 0:
            raise ValueError("PDF buffer is empty after build")

        return pdf_bytes
    except Exception as e:
        print(f"Error building PDF story: {e}")
        raise
