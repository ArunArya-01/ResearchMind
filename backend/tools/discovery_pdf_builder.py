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
    KeepTogether,
)


# ---------------------------------------------------------------------------
# Text / Markdown helpers
# ---------------------------------------------------------------------------

def strip_markdown_fences(text: str, keep_mermaid: bool = False) -> str:
    """Remove fenced code blocks, optionally preserving mermaid body content."""
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


# Allowed ReportLab inline tags (everything else must be escaped).
_ALLOWED_OPEN  = re.compile(r"<(b|i|u|br\s*/?)>",  re.IGNORECASE)
_ALLOWED_CLOSE = re.compile(r"</(b|i|u)>",          re.IGNORECASE)


def clean_text(text: str) -> str:
    """
    Convert lightweight Markdown to safe ReportLab paragraph markup.

    Strategy
    --------
    1. Strip code fences and normalise whitespace.
    2. Remove links, ATX headings, block-quote markers.
    3. Protect bold/italic spans with unique placeholders BEFORE html.escape().
    4. Escape everything else (so stray < > & become &lt; &gt; &amp;).
    5. Restore the placeholders as proper <b>/<i> tags.

    This guarantees that no raw HTML tags from the original markdown can
    survive into the ReportLab XML parser.
    """
    if not text:
        return ""

    text = strip_markdown_fences(text, keep_mermaid=False)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove markdown links — keep display text
    text = re.sub(r"\[(.+?)\]\(.*?\)", r"\1", text)

    # Remove ATX headings markers and blockquotes
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^>+\s?",     "", text, flags=re.MULTILINE)

    # Normalise whitespace (preserve newlines)
    text = text.replace("\t", "  ")
    text = re.sub(r"[^\S\n]+", " ", text)
    text = "".join(ch for ch in text if ch == "\n" or ch.isprintable())

    # --- Protect bold / italic BEFORE escaping ---
    placeholders = [
        (re.compile(r"\*\*\*(.+?)\*\*\*", re.DOTALL), "\x00BI\x01", "\x00/BI\x01"),   # bold-italic
        (re.compile(r"\*\*(.+?)\*\*",      re.DOTALL), "\x00B\x01",  "\x00/B\x01"),    # bold
        (re.compile(r"(?<!\*)\*(.+?)\*(?!\*)", re.DOTALL), "\x00I\x01", "\x00/I\x01"), # italic
        (re.compile(r"__(.+?)__",           re.DOTALL), "\x00B\x01",  "\x00/B\x01"),   # bold __
        (re.compile(r"_(.+?)_",             re.DOTALL), "\x00I\x01",  "\x00/I\x01"),   # italic _
    ]
    # Apply in order, working on single-line chunks to avoid greedy multiline issues
    for pattern, open_ph, close_ph in placeholders:
        text = pattern.sub(lambda m, o=open_ph, c=close_ph: f"{o}{m.group(1)}{c}", text)

    # Remove any remaining inline backtick code (strip backticks, keep content)
    text = re.sub(r"`(.+?)`", r"\1", text)

    # Escape ALL remaining < > & characters so they become safe XML entities
    text = escape(text, quote=False)

    # Restore bold / italic placeholders as ReportLab XML tags
    tag_map = {
        "\x00BI\x01":  "<b><i>",
        "\x00/BI\x01": "</i></b>",
        "\x00B\x01":   "<b>",
        "\x00/B\x01":  "</b>",
        "\x00I\x01":   "<i>",
        "\x00/I\x01":  "</i>",
    }
    for ph, tag in tag_map.items():
        text = text.replace(ph, tag)

    return text.strip()


def safe_paragraph(text: str, style, fallback: str = "") -> object:
    """Create a Paragraph safely, stripping tags on parser errors."""
    candidate = (text or "").strip() or fallback.strip()
    if not candidate:
        return Spacer(1, 0.01 * inch)

    attempts = [
        candidate,
        re.sub(r"<[^>]+>", "", candidate),          # strip all tags
        escape(re.sub(r"<[^>]+>", "", candidate)),   # escape then strip
        "Content unavailable",
    ]
    for attempt in attempts:
        try:
            p = Paragraph(attempt, style)
            return p
        except Exception:
            continue

    return Spacer(1, 0.01 * inch)


# ---------------------------------------------------------------------------
# Markdown section extraction
# ---------------------------------------------------------------------------

def extract_sections_from_markdown(markdown_content: str) -> dict:
    sections = {
        "title":               "Discovery Report",
        "problem_statement":   "",
        "hypothesis":          "",
        "research_hypotheses": [],
        "debate_summary":      "",
        "novelty_verification":"",
        "research_gaps":       [],
    }

    lines = markdown_content.splitlines()
    current_section = None
    current_content = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            sections["title"] = stripped[2:].strip() or sections["title"]
            continue

        if stripped.startswith("## "):
            if current_section:
                _save_section(current_section, current_content, sections)
            current_section = stripped[3:].strip()
            current_content = []
            continue

        if current_section is not None:
            current_content.append(line)

    if current_section:
        _save_section(current_section, current_content, sections)

    return sections


def _save_section(name: str, content_lines: list, sections: dict) -> None:
    content = "\n".join(content_lines).strip()
    nl = name.lower()

    if "problem" in nl:
        sections["problem_statement"] = content
    elif "core hypothesis" in nl:
        sections["hypothesis"] = content
    elif "research hypothes" in nl:
        sections["research_hypotheses"] = _parse_list_items(content)
    elif any(k in nl for k in ("debate", "swarm")):
        sections["debate_summary"] = content
    elif "novelty" in nl:
        sections["novelty_verification"] = content
    elif "gap" in nl:
        sections["research_gaps"] = _parse_list_items(content)


def _parse_list_items(content: str) -> list:
    items = []
    for line in strip_markdown_fences(content).splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r"^[-*•]\s+(.+)$", s) or re.match(r"^\d+[.)]\s+(.+)$", s)
        items.append(m.group(1).strip() if m else s)
    return items


def _split_blocks(content: str) -> list:
    """Return [(kind, text)] where kind is 'paragraph', 'bullet', or 'numbered'."""
    blocks = []
    current_lines = []

    def flush():
        para = " ".join(p.strip() for p in current_lines if p.strip()).strip()
        if para:
            blocks.append(("paragraph", para))
        current_lines.clear()

    for raw in strip_markdown_fences(content).splitlines():
        s = raw.strip()
        if not s:
            flush()
            continue
        bm = re.match(r"^[-*•]\s+(.+)$", s)
        nm = re.match(r"^(\d+)[.)]\s+(.+)$", s)
        if bm:
            flush()
            blocks.append(("bullet", bm.group(1).strip()))
        elif nm:
            flush()
            blocks.append(("numbered", nm.group(2).strip()))
        else:
            current_lines.append(s)

    flush()
    return blocks


# ---------------------------------------------------------------------------
# Mermaid / debate helpers
# ---------------------------------------------------------------------------

def _parse_mermaid_flow(mermaid_content: str) -> list:
    content = strip_markdown_fences(mermaid_content, keep_mermaid=True)
    lines   = [l.strip() for l in content.splitlines() if l.strip()]
    nodes   = {}
    edges   = []

    for line in lines:
        if line.startswith("graph "):
            continue
        for nid, box, dec, rnd in re.findall(r"(\w+)(?:\[(.*?)\]|\{(.*?)\}|\((.*?)\))", line):
            label = (box or dec or rnd).strip()
            label = re.sub(r"<br\s*/?>", " / ", label, flags=re.IGNORECASE)
            if label:
                nodes[nid] = label

        em = re.match(r"(\w+)\s*-->\s*(\w+)$", line)
        lm = re.match(r"(\w+)\s*-->\|(.+?)\|\s*(\w+)$", line)
        if lm:
            edges.append((lm.group(1), lm.group(3), lm.group(2).strip()))
        elif em:
            edges.append((em.group(1), em.group(2), ""))

    if not edges and not nodes:
        return [l for l in lines if not l.lower().startswith("mermaid")]

    result = []
    for i, (src, tgt, lbl) in enumerate(edges, 1):
        conn = f" [{lbl}] " if lbl else " → "
        result.append(f"{i}. {nodes.get(src, src)}{conn}{nodes.get(tgt, tgt)}")

    if not result:
        result = [f"• {v}" for v in nodes.values()]

    return result


def _parse_debate_blocks(content: str) -> list:
    blocks  = []
    current = None

    def flush():
        nonlocal current
        if current and current["items"]:
            blocks.append(current)
        current = None

    for line in strip_markdown_fences(content).splitlines():
        s = line.strip()
        if not s:
            continue
        heading = s.strip("*").strip()
        hl      = heading.lower()
        payload = heading.split(":", 1)[1].strip() if ":" in heading else ""

        if "visionary" in hl or "agent alpha" in hl:
            flush()
            current = {"kind": "visionary", "title": "Visionary Perspective", "items": []}
            if payload:
                current["items"].append(payload)
        elif "skeptic" in hl or "agent beta" in hl:
            flush()
            current = {"kind": "skeptic", "title": "Skeptical Perspective", "items": []}
            if payload:
                current["items"].append(payload)
        elif "resolution" in hl or "consensus" in hl:
            flush()
            current = {"kind": "resolution", "title": "Resolution", "items": []}
            if payload:
                current["items"].append(payload)
        else:
            if current is None:
                current = {"kind": "body", "title": "", "items": []}
            current["items"].append(s)

    flush()
    return blocks


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------

def _make_card(
    text: str,
    para_style,
    bg_color,
    border_color,
    col_width: float = 6.8,
) -> Table:
    """Wrap content in a single-column table (card) block."""
    p = safe_paragraph(clean_text(text), para_style, fallback="Content unavailable")
    tbl = Table([[p]], colWidths=[col_width * inch])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg_color),
        ("BOX",           (0, 0), (-1, -1), 0.75, border_color),
        ("ROUNDEDCORNERS",(0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return tbl


def _add_rich_blocks(story: list, content: str, body_style, bullet_style) -> None:
    for kind, value in _split_blocks(content):
        cleaned = clean_text(value)
        if not cleaned:
            continue
        if kind == "bullet":
            story.append(safe_paragraph(f"• {cleaned}", bullet_style))
        elif kind == "numbered":
            story.append(safe_paragraph(cleaned, bullet_style))
        else:
            story.append(safe_paragraph(cleaned, body_style))
        story.append(Spacer(1, 0.05 * inch))


def _add_numbered_cards(story: list, items: list, card_style, label_prefix: str) -> None:
    for idx, item in enumerate(items, 1):
        cleaned = clean_text(item)
        if not cleaned:
            continue
        card = _make_card(
            f"<b>{label_prefix} {idx}.</b>  {cleaned}",
            card_style,
            colors.white,
            colors.HexColor("#d8dee9"),
        )
        story.append(KeepTogether([card, Spacer(1, 0.10 * inch)]))


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

def _draw_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(colors.HexColor("#9ca3af"))
    canvas.drawString(doc.leftMargin, 0.40 * inch, "ResearchMind Discovery Report")
    canvas.drawRightString(
        letter[0] - doc.rightMargin, 0.40 * inch, f"Page {doc.page}"
    )
    canvas.setStrokeColor(colors.HexColor("#e5e7eb"))
    canvas.setLineWidth(0.5)
    canvas.line(
        doc.leftMargin, 0.55 * inch,
        letter[0] - doc.rightMargin, 0.55 * inch,
    )
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def build_discovery_pdf(markdown_content: str) -> bytes:
    """Build a clean, properly formatted PDF from discovery report markdown."""
    if not markdown_content or not markdown_content.strip():
        raise ValueError("No content provided for PDF generation")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.80 * inch,
        rightMargin=0.80 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        title="Discovery Report",
        author="ResearchMind",
    )

    # ------------------------------------------------------------------
    # Styles
    # ------------------------------------------------------------------
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "RMTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "RMSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "RMSection",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#b91c1c"),
        spaceBefore=14,
        spaceAfter=6,
        alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        "RMBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#1f2937"),
    )
    bullet_style = ParagraphStyle(
        "RMBullet",
        parent=body_style,
        leftIndent=16,
        firstLineIndent=0,
        alignment=TA_LEFT,
    )
    card_text_style = ParagraphStyle(
        "RMCardText",
        parent=body_style,
        alignment=TA_LEFT,
        leading=15,
    )
    callout_style = ParagraphStyle(
        "RMCallout",
        parent=body_style,
        alignment=TA_LEFT,
    )
    debate_header_style = ParagraphStyle(
        "RMDebateHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=4,
        spaceAfter=4,
    )
    flow_style = ParagraphStyle(
        "RMFlow",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=9.5,
        leading=13,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#111827"),
    )

    # ------------------------------------------------------------------
    # Build story
    # ------------------------------------------------------------------
    sections = extract_sections_from_markdown(markdown_content)
    story    = []

    # --- Header ---
    title_text = clean_text(sections["title"]) or "Discovery Report"
    story.append(safe_paragraph(title_text, title_style, fallback="Discovery Report"))
    story.append(safe_paragraph("Generated by ResearchMind", subtitle_style))
    story.append(
        HRFlowable(
            width="100%", thickness=1,
            color=colors.HexColor("#e2e8f0"),
            spaceBefore=2, spaceAfter=18,
        )
    )

    # --- Problem Statement ---
    if sections["problem_statement"]:
        story.append(safe_paragraph("Problem Statement", section_style))
        story.append(
            _make_card(
                sections["problem_statement"], callout_style,
                colors.HexColor("#f8fafc"), colors.HexColor("#cbd5e1"),
            )
        )
        story.append(Spacer(1, 0.16 * inch))

    # --- Core Hypothesis ---
    if sections["hypothesis"]:
        story.append(safe_paragraph("Core Hypothesis", section_style))
        story.append(
            _make_card(
                sections["hypothesis"], callout_style,
                colors.HexColor("#fff7ed"), colors.HexColor("#fdba74"),
            )
        )
        story.append(Spacer(1, 0.16 * inch))

    # --- Research Hypotheses ---
    if sections["research_hypotheses"]:
        story.append(safe_paragraph("Research Hypotheses", section_style))
        _add_numbered_cards(story, sections["research_hypotheses"], card_text_style, "Hypothesis")
        story.append(Spacer(1, 0.12 * inch))

    # --- Swarm Debate Summary ---
    if sections["debate_summary"]:
        story.append(safe_paragraph("Swarm Debate Summary", section_style))
        debate_colors_map = {
            "visionary": (colors.HexColor("#eff6ff"), colors.HexColor("#93c5fd")),
            "skeptic":   (colors.HexColor("#fff7ed"), colors.HexColor("#fdba74")),
            "resolution":(colors.HexColor("#f0fdf4"), colors.HexColor("#86efac")),
            "body":      (colors.HexColor("#f8fafc"), colors.HexColor("#cbd5e1")),
        }
        for block in _parse_debate_blocks(sections["debate_summary"]):
            if block["title"]:
                story.append(safe_paragraph(block["title"], debate_header_style))
            bg, border = debate_colors_map.get(block["kind"], debate_colors_map["body"])
            card = _make_card("\n\n".join(block["items"]), callout_style, bg, border)
            story.append(KeepTogether([card, Spacer(1, 0.10 * inch)]))
        story.append(Spacer(1, 0.04 * inch))

    # --- Novelty Verification ---
    if sections["novelty_verification"]:
        story.append(safe_paragraph("Novelty Verification", section_style))
        _add_rich_blocks(story, sections["novelty_verification"], body_style, bullet_style)
        story.append(Spacer(1, 0.12 * inch))

    # --- Research Gaps ---
    if sections["research_gaps"]:
        story.append(safe_paragraph("Research Gaps and Limitations", section_style))
        _add_numbered_cards(story, sections["research_gaps"], card_text_style, "Gap")

    # Fallback if nothing was parsed
    if len(story) <= 3:
        story.append(
            safe_paragraph(
                "No structured content was found in the supplied markdown.",
                body_style,
            )
        )

    doc.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    pdf_bytes = buffer.getvalue()
    if not pdf_bytes:
        raise ValueError("PDF buffer is empty after build")
    return pdf_bytes