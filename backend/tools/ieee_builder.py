import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle, FrameBreak, Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

PAGE_W, PAGE_H = 595.2, 841.92
L_MARGIN = 50.4; R_EDGE = 547.4; T_MARGIN = 53.9; B_MARGIN = 78.2
COL_L_X0 = 50.4; COL_L_W = 231.8; COL_R_X0 = 315.6; COL_R_W = 231.8
FULL_W = R_EDGE - L_MARGIN
HDR_H = 326; COL_H = PAGE_H - T_MARGIN - HDR_H - B_MARGIN; COL_H_P2 = PAGE_H - T_MARGIN - B_MARGIN
INDENT = 21.6

def mk(name, **kw): return ParagraphStyle(name, **kw)
ST = {
    'title': mk('title', fontName='Times-Bold', fontSize=24, leading=29, alignment=TA_CENTER),
    'auth_name': mk('auth_name', fontName='Times-Bold', fontSize=9, leading=10, alignment=TA_CENTER),
    'auth_detail': mk('auth_detail', fontName='Times-Italic', fontSize=9, leading=10, alignment=TA_CENTER),
    'abstract': mk('abstract', fontName='Times-Roman', fontSize=9, leading=11, alignment=TA_JUSTIFY),
    'sec_head': mk('sec_head', fontName='Times-Roman', fontSize=10, leading=12, alignment=TA_CENTER, spaceBefore=6, spaceAfter=2),
    'body': mk('body', fontName='Times-Roman', fontSize=10, leading=12, alignment=TA_JUSTIFY, firstLineIndent=INDENT),
    'body_ni': mk('body_ni', fontName='Times-Roman', fontSize=10, leading=12, alignment=TA_JUSTIFY, firstLineIndent=0),
    'ref': mk('ref', fontName='Times-Roman', fontSize=9, leading=11, alignment=TA_JUSTIFY, leftIndent=12, firstLineIndent=-12, spaceAfter=2),
}

class HRule(Flowable):
    def __init__(self, w=FULL_W, t=0.75): super().__init__(); self.rw = w; self.t = t; self.width = w; self.height = t + 1
    def draw(self): self.canv.setLineWidth(self.t); self.canv.line(0, self.t / 2, self.rw, self.t / 2)

def author_cell(a): return [Paragraph(a.get('name', ''), ST['auth_name']), Paragraph(a.get('department', ''), ST['auth_detail'])]
def build_authors(authors):
    if not authors: return []
    t = Table([[author_cell(a) for a in authors]], colWidths=[FULL_W/len(authors)]*len(authors))
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('ALIGN',(0,0),(-1,-1),'CENTER')])); return [t]

def build_ieee_pdf(paper: dict) -> bytes:
    buf = io.BytesIO()
    def frame(x, y, w, h, fid): return Frame(x, y, w, h, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id=fid)
    doc = BaseDocTemplate(buf, pagesize=(PAGE_W, PAGE_H), leftMargin=L_MARGIN, rightMargin=PAGE_W-R_EDGE, topMargin=T_MARGIN, bottomMargin=B_MARGIN)
    doc.addPageTemplates([
        PageTemplate(id='first', frames=[frame(L_MARGIN, PAGE_H-T_MARGIN-HDR_H, FULL_W, HDR_H, 'hdr'), frame(COL_L_X0, B_MARGIN, COL_L_W, COL_H, 'p1l'), frame(COL_R_X0, B_MARGIN, COL_R_W, COL_H, 'p1r')]),
        PageTemplate(id='body', frames=[frame(COL_L_X0, B_MARGIN, COL_L_W, COL_H_P2, 'p2l'), frame(COL_R_X0, B_MARGIN, COL_R_W, COL_H_P2, 'p2r')]),
    ])
    story = []
    ROMAN = ['I','II','III','IV','V','VI','VII','VIII','IX','X']
    story.append(Paragraph(paper.get('title', 'Research Synthesis Report'), ST['title'])); story.append(Spacer(1, 10))
    story.extend(build_authors(paper.get('authors', []))); story.append(Spacer(1, 6)); story.append(HRule(FULL_W)); story.append(Spacer(1, 4))
    story.append(Paragraph(f'<i><b>Abstract</b></i>\u2014{paper.get("abstract","")}', ST['abstract'])); story.append(Spacer(1, 6)); story.append(HRule(FULL_W)); story.append(Spacer(1, 4)); story.append(FrameBreak())
    for idx, sec in enumerate(paper.get('sections', [])):
        story.append(Paragraph(f'{ROMAN[idx] if idx < len(ROMAN) else str(idx+1)}. {sec.get("heading","").upper()}', ST['sec_head']))
        for i, item in enumerate(sec.get('content', [])):
            if isinstance(item, str) and item.strip(): story.append(Paragraph(item.replace("<b style=\"color:crimson;\">", "<b>").replace("</b>", "</b>"), ST['body_ni'] if i==0 else ST['body']))
    refs = paper.get('references', [])
    if refs:
        story.append(Paragraph(f'{ROMAN[len(paper.get("sections", []))]}. REFERENCES', ST['sec_head']))
        for i, ref in enumerate(refs, 1): story.append(Paragraph(f'[{i}]\u2002{ref}', ST['ref']))
    doc.build(story); return buf.getvalue()
