import io
import re
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def strip_markdown_fences(text: str, keep_mermaid: bool = False) -> str:
    """Remove fenced code blocks while optionally preserving mermaid body content."""
    if not text:
        return ""

    lines = text.splitlines()
    cleaned = []
    in_fence = False
    fence_lang = ""
    fence_buffer = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_fence:
                in_fence = True
                fence_lang = stripped[3:].strip().lower()
                fence_buffer = []
            else:
                if keep_mermaid and fence_lang == "mermaid":
                    cleaned.extend(fence_buffer)
                in_fence = False
                fence_lang = ""
                fence_buffer = []
            continue

        if in_fence:
            fence_buffer.append(line)
        else:
            cleaned.append(line)

    if in_fence and keep_mermaid and fence_lang == "mermaid":
        cleaned.extend(fence_buffer)

    return "\n".join(cleaned)


def clean_text(text: str) -> str:
    """Convert lightweight markdown into safe ReportLab paragraph markup."""
    if not text:
        return ""

    text = strip_markdown_fences(text, keep_mermaid=False)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", text)
    text = re.sub(r"^[>#]+\s*", "", text, flags=re.MULTILINE)
    text = text.replace("\t", " ")
    text = re.sub(r"[^\S\n]+", " ", text)
    text = "".join(ch for ch in text if ch == "\n" or ch.isprintable())

    placeholders = {
        "__BOLD_OPEN__": "<b>",
        "__BOLD_CLOSE__": "</b>",
        "__ITALIC_OPEN__": "<i>",
        "__ITALIC_CLOSE__": "</i>",
    }
    text = re.sub(r"\*\*(.+?)\*\*", r"__BOLD_OPEN__\1__BOLD_CLOSE__", text)
    text = re.sub(r"(?<!\*)\*(.+?)\*(?!\*)", r"__ITALIC_OPEN__\1__ITALIC_CLOSE__", text)
    text = escape(text, quote=False)
    for placeholder, replacement in placeholders.items():
        text = text.replace(placeholder, replacement)

    text = text.replace("&nbsp;", " ")
    return text.strip()


def extract_sections_from_markdown(markdown_content: str):
    """Extract structured sections from discovery report markdown."""
    sections = {
        "title": "Discovery Report",
        "problem_statement": "",
        "hypothesis": "",
        "research_hypotheses": [],
        "empirical_grounding": "",
        "debate_summary": "",
        "novelty_verification": "",
        "architectural_flow": "",
        "research_gaps": [],
    }

    lines = markdown_content.splitlines()
    current_section = None
    current_content = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            sections["title"] = stripped[2:].strip() or sections["title"]
            continue

        if stripped.startswith("## "):
            if current_section:
                save_section(current_section, current_content, sections)
            current_section = stripped[3:].strip().lower()
            current_content = []
            continue

        if current_section:
            current_content.append(line)

    if current_section:
        save_section(current_section, current_content, sections)

    return sections


def save_section(name, content_lines, sections):
    """Save extracted section content to sections dict."""
    content = "\n".join(content_lines).strip()
    name_lower = name.lower()

    if "problem" in name_lower:
        sections["problem_statement"] = content
    elif "core hypothesis" in name_lower:
        sections["hypothesis"] = content
    elif "research hypothes" in name_lower:
        sections["research_hypotheses"] = parse_list_items(content)
    elif "empirical" in name_lower or "data" in name_lower or "grounding" in name_lower:
        sections["empirical_grounding"] = content
    elif "debate" in name_lower or "swarm" in name_lower:
        sections["debate_summary"] = content
    elif "novelty" in name_lower:
        sections["novelty_verification"] = content
    elif "architectural" in name_lower or "flow" in name_lower:
        sections["architectural_flow"] = content
    elif "gap" in name_lower:
        sections["research_gaps"] = parse_list_items(content)


def safe_paragraph(text: str, style, fallback: str = ""):
    """Create a Paragraph safely, falling back to plain text on parser errors."""
    candidate = (text or "").strip()
    if not candidate and fallback:
        candidate = fallback

    if not candidate:
        return Spacer(1, 0.01 * inch)

    for current in (candidate, re.sub(r"<[^>]+>", "", candidate), clean_text(candidate)):
        try:
            return Paragraph(current, style)
        except Exception:
            continue

    return Paragraph("Content unavailable", style)


def parse_list_items(content: str):
    """Parse bullet and numbered items from markdown-ish content."""
    items = []
    for line in strip_markdown_fences(content).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
        number_match = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if bullet_match:
            items.append(bullet_match.group(1).strip())
        elif number_match:
            items.append(number_match.group(1).strip())
        else:
            items.append(stripped)
    return items


def split_blocks(content: str):
    """Split content into paragraph and list blocks for cleaner PDF layout."""
    blocks = []
    current_lines = []

    def flush_paragraph():
        nonlocal current_lines
        if current_lines:
            paragraph = " ".join(part.strip() for part in current_lines if part.strip()).strip()
            if paragraph:
                blocks.append(("paragraph", paragraph))
            current_lines = []

    for raw_line in strip_markdown_fences(content).splitlines():
        stripped = raw_line.strip()
        if not stripped:
            flush_paragraph()
            continue

        bullet_match = re.match(r"^[-*]\s+(.+)$", stripped)
        number_match = re.match(r"^(\d+)[.)]\s+(.+)$", stripped)
        if bullet_match:
            flush_paragraph()
            blocks.append(("bullet", bullet_match.group(1).strip()))
        elif number_match:
            flush_paragraph()
            blocks.append(("numbered", number_match.group(2).strip()))
        else:
            current_lines.append(stripped)

    flush_paragraph()
    return blocks


def parse_mermaid_flow(mermaid_content: str):
    """Convert simple mermaid content into readable ASCII flow steps."""
    content = strip_markdown_fences(mermaid_content, keep_mermaid=True)
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    nodes = {}
    edges = []

    for line in lines:
        if line.startswith("graph "):
            continue

        node_defs = re.findall(r"(\w+)(?:\[(.*?)\]|\{(.*?)\}|\((.*?)\))", line)
        for node_id, box_text, decision_text, round_text in node_defs:
            label = box_text or decision_text or round_text
            label = re.sub(r"<br\s*/?>", " / ", label, flags=re.IGNORECASE).strip()
            if label:
                nodes[node_id] = label

        edge_match = re.match(r"(\w+)\s*-->\s*(\w+)$", line)
        labeled_edge_match = re.match(r"(\w+)\s*-->\|(.+?)\|\s*(\w+)$", line)
        if labeled_edge_match:
            edges.append(
                (
                    labeled_edge_match.group(1).strip(),
                    labeled_edge_match.group(3).strip(),
                    labeled_edge_match.group(2).strip(),
                )
            )
        elif edge_match:
            edges.append(
                (
                    edge_match.group(1).strip(),
                    edge_match.group(2).strip(),
                    "",
                )
            )

    if not edges and not nodes:
        return [line for line in lines if not line.lower().startswith("mermaid")]

    result = []
    for index, (source, target, label) in enumerate(edges, start=1):
        source_label = nodes.get(source, source)
        target_label = nodes.get(target, target)
        connector = f" [{label}] " if label else " -> "
        result.append(f"{index}. {source_label}{connector}{target_label}")

    if not result:
        result.extend(f"- {label}" for label in nodes.values())

    return result


def parse_debate_blocks(content: str):
    """Group debate content into agent-specific sections."""
    blocks = []
    current = None

    def flush():
        nonlocal current
        if current and current["items"]:
            blocks.append(current)
        current = None

    for line in strip_markdown_fences(content).splitlines():
        stripped = line.strip()
        if not stripped:
            continue

        heading = stripped.strip("*").strip()
        lowered = heading.lower()

        if "visionary" in lowered or "agent alpha" in lowered:
            flush()
            current = {"kind": "visionary", "title": "Visionary Perspective", "items": []}
            payload = heading.split(":", 1)[1].strip() if ":" in heading else ""
            if payload:
                current["items"].append(payload)
        elif "skeptic" in lowered or "agent beta" in lowered:
            flush()
            current = {"kind": "skeptic", "title": "Skeptical Perspective", "items": []}
            payload = heading.split(":", 1)[1].strip() if ":" in heading else ""
            if payload:
                current["items"].append(payload)
        elif "resolution" in lowered or "consensus" in lowered:
            flush()
            current = {"kind": "resolution", "title": "Resolution", "items": []}
            payload = heading.split(":", 1)[1].strip() if ":" in heading else ""
            if payload:
                current["items"].append(payload)
        else:
            if current is None:
                current = {"kind": "body", "title": "", "items": []}
            current["items"].append(stripped)

    flush()
    return blocks


def make_card(text: str, paragraph_style, background_color, border_color):
    """Wrap content in a one-column table to create a reliable report card block."""
    paragraph = safe_paragraph(clean_text(text), paragraph_style, fallback="Content unavailable")
    table = Table([[paragraph]], colWidths=[6.8 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background_color),
                ("BOX", (0, 0), (-1, -1), 1, border_color),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return table


def add_rich_text_blocks(story, content: str, body_style, bullet_style):
    """Render paragraph and list blocks with consistent spacing."""
    for kind, value in split_blocks(content):
        cleaned = clean_text(value)
        if not cleaned:
            continue

        if kind == "bullet":
            story.append(safe_paragraph(f"- {cleaned}", bullet_style))
        elif kind == "numbered":
            story.append(safe_paragraph(cleaned, bullet_style))
        else:
            story.append(safe_paragraph(cleaned, body_style))
        story.append(Spacer(1, 0.05 * inch))


def add_numbered_cards(story, items, card_style, label_prefix: str):
    for idx, item in enumerate(items, start=1):
        cleaned = clean_text(item)
        if not cleaned:
            continue
        story.append(make_card(f"<b>{label_prefix} {idx}.</b> {cleaned}", card_style, colors.white, colors.HexColor("#d8dee9")))
        story.append(Spacer(1, 0.10 * inch))


def draw_page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(doc.leftMargin, 0.45 * inch, "ResearchMind Discovery Report")
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_discovery_pdf(markdown_content: str) -> bytes:
    """Build a clean, valid PDF from discovery report markdown."""
    if not markdown_content or not markdown_content.strip():
        raise ValueError("No content provided for PDF generation")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Discovery Report",
        author="ResearchMind",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DiscoveryTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DiscoverySubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=14,
    )
    section_style = ParagraphStyle(
        "DiscoverySection",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#b91c1c"),
        spaceBefore=10,
        spaceAfter=6,
        alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        "DiscoveryBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=0,
    )
    bullet_style = ParagraphStyle(
        "DiscoveryBullet",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-8,
        alignment=TA_LEFT,
    )
    card_text_style = ParagraphStyle(
        "DiscoveryCardText",
        parent=body_style,
        alignment=TA_LEFT,
        leading=14,
    )
    callout_style = ParagraphStyle(
        "DiscoveryCallout",
        parent=body_style,
        alignment=TA_LEFT,
    )
    debate_header_style = ParagraphStyle(
        "DiscoveryDebateHeader",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=2,
        spaceAfter=5,
    )
    flow_style = ParagraphStyle(
        "DiscoveryFlow",
        parent=body_style,
        fontName="Courier",
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#111827"),
    )

    sections = extract_sections_from_markdown(markdown_content)
    story = []

    title_text = clean_text(sections["title"]) or "Discovery Report"
    story.append(safe_paragraph(title_text, title_style, fallback="Discovery Report"))
    story.append(safe_paragraph("Generated from structured discovery markdown", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceBefore=0, spaceAfter=14))

    if sections["problem_statement"]:
        story.append(safe_paragraph("Problem Statement", section_style))
        story.append(make_card(sections["problem_statement"], callout_style, colors.HexColor("#f8fafc"), colors.HexColor("#cbd5e1")))
        story.append(Spacer(1, 0.14 * inch))

    if sections["hypothesis"]:
        story.append(safe_paragraph("Core Hypothesis", section_style))
        story.append(make_card(sections["hypothesis"], callout_style, colors.HexColor("#fff7ed"), colors.HexColor("#fdba74")))
        story.append(Spacer(1, 0.14 * inch))

    if sections["research_hypotheses"]:
        story.append(safe_paragraph("Research Hypotheses", section_style))
        add_numbered_cards(story, sections["research_hypotheses"], card_text_style, "Hypothesis")
        story.append(Spacer(1, 0.08 * inch))

    if sections["empirical_grounding"]:
        story.append(safe_paragraph("Empirical Grounding", section_style))
        add_rich_text_blocks(story, sections["empirical_grounding"], body_style, bullet_style)
        story.append(Spacer(1, 0.10 * inch))

    if sections["debate_summary"]:
        story.append(safe_paragraph("Swarm Debate Summary", section_style))
        debate_blocks = parse_debate_blocks(sections["debate_summary"])
        debate_colors = {
            "visionary": (colors.HexColor("#eff6ff"), colors.HexColor("#93c5fd")),
            "skeptic": (colors.HexColor("#fff7ed"), colors.HexColor("#fdba74")),
            "resolution": (colors.HexColor("#f0fdf4"), colors.HexColor("#86efac")),
            "body": (colors.HexColor("#f8fafc"), colors.HexColor("#cbd5e1")),
        }
        for block in debate_blocks:
            if block["title"]:
                story.append(safe_paragraph(block["title"], debate_header_style))
            bg_color, border_color = debate_colors.get(block["kind"], debate_colors["body"])
            story.append(make_card("\n\n".join(block["items"]), callout_style, bg_color, border_color))
            story.append(Spacer(1, 0.10 * inch))
        story.append(Spacer(1, 0.05 * inch))

    if sections["novelty_verification"]:
        story.append(safe_paragraph("Novelty Verification", section_style))
        add_rich_text_blocks(story, sections["novelty_verification"], body_style, bullet_style)
        story.append(Spacer(1, 0.10 * inch))

    if sections["architectural_flow"]:
        story.append(safe_paragraph("Architectural Flow", section_style))
        flow_lines = parse_mermaid_flow(sections["architectural_flow"])
        for line in flow_lines:
            cleaned = clean_text(line)
            if cleaned:
                story.append(make_card(cleaned, flow_style, colors.HexColor("#f8fafc"), colors.HexColor("#cbd5e1")))
                story.append(Spacer(1, 0.08 * inch))
        story.append(Spacer(1, 0.06 * inch))

    if sections["research_gaps"]:
        story.append(safe_paragraph("Research Gaps and Limitations", section_style))
        add_numbered_cards(story, sections["research_gaps"], card_text_style, "Gap")

    if len(story) <= 3:
        story.append(safe_paragraph("No structured content was found in the supplied markdown.", body_style))

    doc.build(story, onFirstPage=draw_page_footer, onLaterPages=draw_page_footer)
    pdf_bytes = buffer.getvalue()
    if not pdf_bytes:
        raise ValueError("PDF buffer is empty after build")
    return pdf_bytes
