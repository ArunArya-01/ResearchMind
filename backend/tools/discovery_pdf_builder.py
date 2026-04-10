import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch

def clean_text(text, preserve_breaks=False):
    """Clean markdown text for ReportLab with proper XML handling"""
    if not text:
        return ""

    # Remove markdown links but keep text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

    if not preserve_breaks:
        # Normalize whitespace for single-line content
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

    # Use placeholders for markdown formatting
    text = re.sub(r'\*\*(.+?)\*\*', r'__BOLD_START__\1__BOLD_END__', text)
    text = re.sub(r'\*(.+?)\*', r'__ITALIC_START__\1__ITALIC_END__', text)

    # Escape special characters for XML
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
                plain_text = re.sub(r'<[^>]+>', '', text)
                try:
                    return Paragraph(plain_text, style)
                except:
                    return Spacer(1, 0.1*inch)
            text = re.sub(r'[^\x00-\x7F]+', '', text)
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

def parse_mermaid_flow(mermaid_content):
    """Parse mermaid diagram content and convert to visual ASCII format with boxes"""
    lines = mermaid_content.split('\n')

    # Extract all node definitions
    nodes = {}
    connections = []

    for line in lines:
        line = line.strip()

        # Extract node definitions: A[Text] or A{Text}
        node_match = re.match(r'(\w+)[\[\{](.+?)[\]\}]', line)
        if node_match:
            node_id = node_match.group(1)
            node_text = node_match.group(2).strip()
            is_diamond = '{' in line
            nodes[node_id] = {'text': node_text, 'type': 'decision' if is_diamond else 'box'}

        # Extract connections: A-->B or A-->|label|B
        if '-->' in line:
            # Format: A-->B or A-->|label|B
            parts = re.split(r'-->[\|]?', line)
            if len(parts) >= 2:
                from_id = parts[0].strip()
                # Extract label if exists
                label = ''
                if '|' in line:
                    label_match = re.search(r'\|(.+?)\|', line)
                    if label_match:
                        label = label_match.group(1).strip()

                # Extract to_id
                to_match = re.search(r'-->[\|]?(\w+)', line)
                if to_match:
                    to_id = to_match.group(1)
                    connections.append((from_id, to_id, label))

    # Build visual flow representation
    result = []

    # Add all nodes first
    for node_id, node_info in nodes.items():
        text = node_info['text']
        if node_info['type'] == 'decision':
            # Diamond box for decisions
            result.append(f"◇ {text}")
        else:
            # Regular box
            result.append(f"□ {text}")

    # Add connections
    if connections:
        result.append("")
        result.append("Flow Steps:")
        for i, (from_id, to_id, label) in enumerate(connections, 1):
            from_text = nodes.get(from_id, {}).get('text', from_id)
            to_text = nodes.get(to_id, {}).get('text', to_id)

            if label:
                result.append(f"{i}. {from_text}")
                result.append(f"   ↓ [{label}]")
                result.append(f"   {to_text}")
            else:
                result.append(f"{i}. {from_text} → {to_text}")

    return result if result else [line.strip() for line in lines if line.strip() and not line.startswith('graph')]

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

    # Title Style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#d90429'),
        spaceAfter=12,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    # Section Header Style
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#d90429'),
        spaceBefore=16,
        spaceAfter=12,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderPadding=0
    )

    # Subsection Style
    subsection_style = ParagraphStyle(
        'SubsectionStyle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#555555'),
        spaceBefore=12,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )

    # Body Style
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=10
    )

    # Box Style for highlight content
    box_style = ParagraphStyle(
        'BoxStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        alignment=TA_JUSTIFY,
        leftIndent=15,
        rightIndent=15,
        spaceBefore=10,
        spaceAfter=10,
        backColor=colors.HexColor('#f5f5f5'),
        borderWidth=1,
        borderColor=colors.HexColor('#d90429'),
        borderPadding=10
    )

    # Hypothesis Style - numbered and indented
    hypothesis_style = ParagraphStyle(
        'HypothesisStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        leftIndent=20,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        backColor=colors.HexColor('#ffffff'),
        borderWidth=1,
        borderColor=colors.HexColor('#e0e0e0'),
        borderPadding=8
    )

    # Gap Style - with bullets
    gap_style = ParagraphStyle(
        'GapStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        leftIndent=25,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#333333')
    )

    # Debate Agent Style - with background
    debate_agent_style = ParagraphStyle(
        'DebateAgentStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceBefore=10,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#d90429')
    )

    # Visionary Agent box style
    visionary_box_style = ParagraphStyle(
        'VisionaryStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=12,
        rightIndent=12,
        spaceBefore=6,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        backColor=colors.HexColor('#e3f2fd'),
        borderColor=colors.HexColor('#1976d2'),
        borderWidth=1,
        borderPadding=10,
        textColor=colors.HexColor('#0d47a1')
    )

    # Skeptic Agent box style
    skeptic_box_style = ParagraphStyle(
        'SkepticStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=12,
        rightIndent=12,
        spaceBefore=6,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        backColor=colors.HexColor('#fff3e0'),
        borderColor=colors.HexColor('#f57c00'),
        borderWidth=1,
        borderPadding=10,
        textColor=colors.HexColor('#e65100')
    )

    # Resolution style
    resolution_style = ParagraphStyle(
        'ResolutionStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=12,
        rightIndent=12,
        spaceBefore=6,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        backColor=colors.HexColor('#e8f5e9'),
        borderColor=colors.HexColor('#388e3c'),
        borderWidth=2,
        borderPadding=10,
        textColor=colors.HexColor('#1b5e20'),
        fontName='Helvetica-Bold'
    )

    # Code/Flow Style
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        leftIndent=15,
        rightIndent=15,
        spaceBefore=8,
        spaceAfter=8,
        fontFamily='Courier',
        backColor=colors.HexColor('#f9f9f9'),
        borderWidth=1,
        borderColor=colors.HexColor('#cccccc'),
        borderPadding=10,
        textColor=colors.HexColor('#333333')
    )

    story = []
    sections = extract_sections_from_markdown(markdown_content)

    try:
        # ===== TITLE =====
        title_text = clean_text(sections['title'])
        if title_text.strip():
            story.append(safe_paragraph(title_text, title_style))
            story.append(Spacer(1, 0.25*inch))

        # ===== PROBLEM STATEMENT =====
        if sections['problem_statement']:
            story.append(safe_paragraph("PROBLEM STATEMENT", section_style))
            story.append(Spacer(1, 0.08*inch))
            problem_text = clean_text(sections['problem_statement'])
            if problem_text.strip():
                story.append(safe_paragraph(problem_text, box_style))
            story.append(Spacer(1, 0.15*inch))

        # ===== CORE HYPOTHESIS =====
        if sections['hypothesis']:
            story.append(safe_paragraph("CORE HYPOTHESIS", section_style))
            story.append(Spacer(1, 0.08*inch))
            hypothesis_text = clean_text(sections['hypothesis'])
            if hypothesis_text.strip():
                story.append(safe_paragraph(hypothesis_text, box_style))
            story.append(Spacer(1, 0.15*inch))

        # ===== RESEARCH HYPOTHESES - IMPROVED FORMAT =====
        if sections['research_hypotheses']:
            story.append(safe_paragraph("RESEARCH HYPOTHESES", section_style))
            story.append(Spacer(1, 0.08*inch))

            for idx, hyp in enumerate(sections['research_hypotheses'], 1):
                if hyp and hyp.strip():
                    cleaned = clean_text(hyp)
                    if cleaned.strip():
                        # Create numbered hypothesis with visual separation
                        hyp_text = f"<b>H{idx}:</b> {cleaned}"
                        story.append(safe_paragraph(hyp_text, hypothesis_style))
                        story.append(Spacer(1, 0.05*inch))

            story.append(Spacer(1, 0.1*inch))

        # ===== EMPIRICAL GROUNDING =====
        if sections['empirical_grounding']:
            story.append(safe_paragraph("EMPIRICAL GROUNDING", section_style))
            story.append(Spacer(1, 0.08*inch))
            empirical_text = clean_text(sections['empirical_grounding'])
            if empirical_text.strip():
                story.append(safe_paragraph(empirical_text, body_style))
            story.append(Spacer(1, 0.15*inch))

        # ===== DEBATE SUMMARY =====
        if sections['debate_summary']:
            story.append(safe_paragraph("SWARM DEBATE SUMMARY", section_style))
            story.append(Spacer(1, 0.08*inch))

            story.append(safe_paragraph(
                "<i>Collaborative Analysis Between Two AI Agents</i>",
                subsection_style
            ))
            story.append(Spacer(1, 0.08*inch))

            debate_lines = sections['debate_summary'].split('\n')
            current_agent = None

            for line in debate_lines:
                stripped = line.strip()
                if not stripped:
                    continue

                if 'Visionary' in stripped or 'Agent Alpha' in stripped:
                    current_agent = 'visionary'
                    if ':' in stripped:
                        content = stripped.split(':', 1)[1].strip()
                    else:
                        content = ''

                    # Add visionary header with background
                    header = "🚀 VISIONARY AGENT (Alpha) - Optimistic Innovator"
                    story.append(safe_paragraph(
                        f"<b>{header}</b>",
                        debate_agent_style
                    ))

                    if content:
                        cleaned = clean_text(content, preserve_breaks=False)
                        if cleaned.strip():
                            story.append(safe_paragraph(cleaned, visionary_box_style))
                    story.append(Spacer(1, 0.1*inch))

                elif 'Skeptic' in stripped or 'Agent Beta' in stripped:
                    current_agent = 'skeptic'
                    if ':' in stripped:
                        content = stripped.split(':', 1)[1].strip()
                    else:
                        content = ''

                    # Add skeptic header with background
                    header = "⚠️ SKEPTIC AGENT (Beta) - Critical Analyst"
                    story.append(safe_paragraph(
                        f"<b>{header}</b>",
                        debate_agent_style
                    ))

                    if content:
                        cleaned = clean_text(content, preserve_breaks=False)
                        if cleaned.strip():
                            story.append(safe_paragraph(cleaned, skeptic_box_style))
                    story.append(Spacer(1, 0.1*inch))

                elif 'Resolution' in stripped or 'Consensus' in stripped:
                    content = stripped.replace('Resolution', '').replace('Consensus', '').replace('**', '').strip()
                    if ':' in stripped:
                        content = stripped.split(':', 1)[1].strip()

                    # Add resolution header
                    header = "✓ RESOLUTION & CONSENSUS"
                    story.append(safe_paragraph(
                        f"<b>{header}</b>",
                        debate_agent_style
                    ))

                    if content:
                        cleaned = clean_text(content, preserve_breaks=False)
                        if cleaned.strip():
                            story.append(safe_paragraph(cleaned, resolution_style))
                    story.append(Spacer(1, 0.12*inch))

                elif stripped and not stripped.startswith('#'):
                    # Regular content line
                    if current_agent == 'visionary':
                        cleaned = clean_text(stripped, preserve_breaks=False)
                        if cleaned.strip():
                            story.append(safe_paragraph(cleaned, visionary_box_style))
                    elif current_agent == 'skeptic':
                        cleaned = clean_text(stripped, preserve_breaks=False)
                        if cleaned.strip():
                            story.append(safe_paragraph(cleaned, skeptic_box_style))
                    else:
                        cleaned = clean_text(stripped, preserve_breaks=False)
                        if cleaned.strip():
                            story.append(safe_paragraph(cleaned, body_style))

            story.append(Spacer(1, 0.15*inch))

        # ===== NOVELTY VERIFICATION =====
        if sections['novelty_verification']:
            story.append(safe_paragraph("NOVELTY VERIFICATION", section_style))
            story.append(Spacer(1, 0.08*inch))
            novelty_text = clean_text(sections['novelty_verification'])
            if novelty_text.strip():
                story.append(safe_paragraph(novelty_text, body_style))
            story.append(Spacer(1, 0.15*inch))

        # ===== ARCHITECTURAL FLOW - IMPROVED HANDLING =====
        if sections['architectural_flow']:
            story.append(safe_paragraph("ARCHITECTURAL FLOW", section_style))
            story.append(Spacer(1, 0.08*inch))

            flow_content = sections['architectural_flow']

            # Check if mermaid diagram
            if 'graph' in flow_content.lower() or '-->' in flow_content:
                story.append(safe_paragraph("<i>System Architecture & Process Flow</i>", subsection_style))
                story.append(Spacer(1, 0.1*inch))

                # Parse mermaid diagram
                flow_steps = parse_mermaid_flow(flow_content)

                # Display parsed flow with better formatting
                for step in flow_steps:
                    # Format arrows and connections nicely
                    if '↓' in step or '→' in step or '◇' in step or '□' in step:
                        story.append(safe_paragraph(step, code_style))
                    elif step.startswith('Flow Steps:'):
                        story.append(safe_paragraph("<b>" + step + "</b>", subsection_style))
                    else:
                        story.append(safe_paragraph(step, code_style))

                story.append(Spacer(1, 0.1*inch))
            else:
                # Regular text flow
                flow_lines = []
                for line in flow_content.split('\n'):
                    stripped = line.strip()
                    if stripped and not stripped.startswith('```'):
                        flow_lines.append(stripped)

                if flow_lines:
                    flow_text = clean_text('\n'.join(flow_lines), preserve_breaks=True)
                    if flow_text.strip():
                        story.append(safe_paragraph(flow_text, body_style))

            story.append(Spacer(1, 0.15*inch))

        # ===== RESEARCH GAPS - IMPROVED FORMAT =====
        if sections['research_gaps']:
            story.append(safe_paragraph("RESEARCH GAPS & LIMITATIONS", section_style))
            story.append(Spacer(1, 0.08*inch))

            story.append(safe_paragraph(
                "<i>Identified gaps and areas for future investigation:</i>",
                subsection_style
            ))
            story.append(Spacer(1, 0.05*inch))

            for idx, gap in enumerate(sections['research_gaps'], 1):
                if gap and gap.strip():
                    cleaned = clean_text(gap)
                    if cleaned.strip():
                        # Use numbered bullets for gaps
                        gap_text = f"<b>[{idx}]</b> {cleaned}"
                        story.append(safe_paragraph(gap_text, gap_style))
                        story.append(Spacer(1, 0.06*inch))

        if not story:
            story.append(safe_paragraph("No content available", body_style))

        doc.build(story)
        pdf_bytes = buf.getvalue()

        if not pdf_bytes or len(pdf_bytes) == 0:
            raise ValueError("PDF buffer is empty after build")

        return pdf_bytes

    except Exception as e:
        print(f"Error building PDF story: {e}")
        raise
