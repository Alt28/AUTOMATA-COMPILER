#!/usr/bin/env python3
"""
Convert a defense-prep Markdown file into a clean PDF.

Improvements over the existing convert_to_pdf.py:
  - Preserves fenced code blocks (the original drops them entirely).
  - Renders inline code, bold, and italic with proper styling.
  - Renders tables.
  - Adds page numbers.

Usage:
    python convert_defense_to_pdf.py <input.md> [output.pdf]
"""
import os
import re
import sys
import html

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Preformatted, Table, TableStyle, KeepTogether,
)
from reportlab.lib.units import inch


# ────────────────────────────────────────────────────────────────────
#  Styles
# ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'GalTitle',
    parent=styles['Heading1'],
    fontSize=20,
    leading=24,
    textColor=colors.HexColor('#2C5F2D'),
    spaceAfter=14,
    spaceBefore=8,
    keepWithNext=True,
)
h2_style = ParagraphStyle(
    'GalH2',
    parent=styles['Heading2'],
    fontSize=15,
    leading=18,
    textColor=colors.HexColor('#3A6A3D'),
    spaceAfter=10,
    spaceBefore=14,
    keepWithNext=True,
)
h3_style = ParagraphStyle(
    'GalH3',
    parent=styles['Heading3'],
    fontSize=12,
    leading=15,
    textColor=colors.HexColor('#4A7C59'),
    spaceAfter=8,
    spaceBefore=10,
    keepWithNext=True,
)
body_style = ParagraphStyle(
    'GalBody',
    parent=styles['Normal'],
    fontSize=10.5,
    leading=14,
    spaceAfter=6,
)
bullet_style = ParagraphStyle(
    'GalBullet',
    parent=body_style,
    leftIndent=18,
    bulletIndent=6,
    spaceAfter=3,
)
code_style = ParagraphStyle(
    'GalCode',
    parent=styles['Code'],
    fontName='Courier',
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor('#1a1a1a'),
    backColor=colors.HexColor('#f4f6f4'),
    borderColor=colors.HexColor('#cfd8cf'),
    borderWidth=0.5,
    borderPadding=6,
    leftIndent=10,
    rightIndent=10,
    spaceAfter=10,
    spaceBefore=4,
)
quote_style = ParagraphStyle(
    'GalQuote',
    parent=body_style,
    leftIndent=18,
    rightIndent=10,
    textColor=colors.HexColor('#36513a'),
    fontName='Helvetica-Oblique',
    spaceAfter=8,
)


# ────────────────────────────────────────────────────────────────────
#  Inline-formatting helpers
# ────────────────────────────────────────────────────────────────────
INLINE_CODE_RE = re.compile(r'`([^`]+)`')
BOLD_RE = re.compile(r'\*\*([^*]+)\*\*')
# Italic: `*` must be at start of string or preceded by whitespace/opening punct,
# never by `)`, `]`, alphanumeric, or another `*`. Match is lazy so we don't
# bridge across stray `*` symbols in regex / glob patterns elsewhere on the line.
ITALIC_RE = re.compile(r'(?<![*\w\)\]])\*([^*\n]+?)\*(?!\w)')

# Sentinel placeholders that survive HTML escaping and won't appear in user prose
_CODE_OPEN = '\x00CODE\x01'
_CODE_CLOSE = '\x00/CODE\x01'


def render_inline(text: str) -> str:
    """Convert Markdown inline syntax to ReportLab's mini-HTML."""
    # 1. Pull out inline-code BEFORE escaping, replacing with sentinels so the
    #    `*` characters inside backticks can't trigger italic later.
    code_chunks = []

    def _stash(match):
        code_chunks.append(match.group(1))
        return f'{_CODE_OPEN}{len(code_chunks) - 1}{_CODE_CLOSE}'

    text = INLINE_CODE_RE.sub(_stash, text)

    # 2. Escape HTML special chars in the remaining prose
    text = html.escape(text)

    # 3. Apply emphasis markup on plain prose only
    text = BOLD_RE.sub(r'<b>\1</b>', text)
    text = ITALIC_RE.sub(r'<i>\1</i>', text)

    # 4. Re-insert the saved code chunks (HTML-escape their content too)
    def _restore(match):
        idx = int(match.group(1))
        body = html.escape(code_chunks[idx])
        return (f'<font face="Courier" backColor="#f0f0f0">{body}</font>')

    text = re.sub(rf'{re.escape(_CODE_OPEN)}(\d+){re.escape(_CODE_CLOSE)}',
                  _restore, text)
    return text


# ────────────────────────────────────────────────────────────────────
#  Block parser — token-driven walk over markdown lines
# ────────────────────────────────────────────────────────────────────
def parse_markdown_to_flowables(md_text: str):
    """Return a list of ReportLab flowables from a Markdown string."""
    lines = md_text.split('\n')
    story = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Fenced code block ─────────────────────────────────
        if stripped.startswith('```'):
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # consume closing ```
            code_text = '\n'.join(code_lines)
            story.append(Preformatted(code_text, code_style))
            continue

        # Horizontal rule ───────────────────────────────────
        if stripped in ('---', '***', '___'):
            story.append(Spacer(1, 0.05 * inch))
            story.append(Paragraph(
                '<para alignment="center">'
                '<font color="#888888">────────────────────────────</font>'
                '</para>',
                body_style,
            ))
            story.append(Spacer(1, 0.05 * inch))
            i += 1
            continue

        # Headings ──────────────────────────────────────────
        if stripped.startswith('# '):
            story.append(Paragraph(render_inline(stripped[2:]), title_style))
            i += 1
            continue
        if stripped.startswith('## '):
            story.append(Paragraph(render_inline(stripped[3:]), h2_style))
            i += 1
            continue
        if stripped.startswith('### '):
            story.append(Paragraph(render_inline(stripped[4:]), h3_style))
            i += 1
            continue

        # Block-quote ───────────────────────────────────────
        if stripped.startswith('> '):
            quote_lines = []
            while i < n and lines[i].lstrip().startswith('> '):
                quote_lines.append(lines[i].lstrip()[2:])
                i += 1
            story.append(Paragraph(render_inline(' '.join(quote_lines)),
                                   quote_style))
            continue

        # Bullet list ───────────────────────────────────────
        if stripped.startswith(('- ', '* ', '+ ')):
            bullets = []
            while i < n:
                s = lines[i].strip()
                if not (s.startswith('- ') or s.startswith('* ')
                        or s.startswith('+ ')):
                    break
                bullets.append(s[2:])
                i += 1
            for b in bullets:
                story.append(Paragraph(
                    f'• {render_inline(b)}',
                    bullet_style,
                ))
            continue

        # Numbered list (very simple — we render as bullets)
        if re.match(r'^\d+\. ', stripped):
            num_items = []
            while i < n and re.match(r'^\d+\. ', lines[i].strip()):
                num_items.append(re.sub(r'^\d+\. ', '', lines[i].strip()))
                i += 1
            for k, item in enumerate(num_items, 1):
                story.append(Paragraph(
                    f'{k}. {render_inline(item)}',
                    bullet_style,
                ))
            continue

        # Markdown table ────────────────────────────────────
        if '|' in stripped and i + 1 < n and re.match(
                r'^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$',
                lines[i + 1].strip()):
            table_rows = []
            # Header
            header = [c.strip() for c in stripped.strip('|').split('|')]
            table_rows.append(header)
            i += 2  # skip header + separator
            while i < n and '|' in lines[i] and lines[i].strip():
                row = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                # Pad short rows so reportlab doesn't crash
                while len(row) < len(header):
                    row.append('')
                table_rows.append(row[:len(header)])
                i += 1
            # Render each cell with inline formatting
            wrapped = [
                [Paragraph(render_inline(cell), body_style) for cell in r]
                for r in table_rows
            ]
            tbl = Table(wrapped, repeatRows=1, hAlign='LEFT')
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dde8de')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f3320')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#bcbcbc')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 0.08 * inch))
            continue

        # Blank line ────────────────────────────────────────
        if not stripped:
            story.append(Spacer(1, 0.06 * inch))
            i += 1
            continue

        # Plain paragraph (fold consecutive non-blank lines together)
        para_lines = [stripped]
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (not nxt
                    or nxt.startswith(('#', '```', '- ', '* ', '+ ', '> '))
                    or re.match(r'^\d+\. ', nxt)
                    or '|' in nxt and i + 1 < n and re.match(
                        r'^\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?$',
                        lines[i + 1].strip() if i + 1 < n else '')):
                break
            para_lines.append(nxt)
            i += 1
        text = ' '.join(para_lines)
        story.append(Paragraph(render_inline(text), body_style))

    return story


# ────────────────────────────────────────────────────────────────────
#  Page footer with page numbers
# ────────────────────────────────────────────────────────────────────
def _draw_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#7a7a7a'))
    canvas.drawCentredString(
        letter[0] / 2, 0.35 * inch,
        f'GAL Compiler Defense — page {doc.page}',
    )
    canvas.restoreState()


# ────────────────────────────────────────────────────────────────────
#  Main
# ────────────────────────────────────────────────────────────────────
def convert(input_path: str, output_path: str | None = None) -> str:
    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = base + '.pdf'

    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    flowables = parse_markdown_to_flowables(md_text)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        title=os.path.basename(input_path),
    )
    doc.build(
        flowables,
        onFirstPage=_draw_page_number,
        onLaterPages=_draw_page_number,
    )
    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python convert_defense_to_pdf.py <input.md> [output.pdf]')
        sys.exit(2)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else None
    out = convert(src, dst)
    print(f'PDF created: {out}')
