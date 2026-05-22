#!/usr/bin/env python3
import markdown
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch

# Paths
input_file = r"c:\Users\clarence\Downloads\AUTOMATA-COMPILER-main (1)\AUTOMATA-COMPILER-main\my GAL code\GAL_RESERVED_WORDS_EXPLANATION.md"
output_file = r"c:\Users\clarence\Downloads\AUTOMATA-COMPILER-main (1)\AUTOMATA-COMPILER-main\my GAL code\GAL_RESERVED_WORDS_EXPLANATION.pdf"

# Read markdown file
with open(input_file, 'r', encoding='utf-8') as f:
    md_text = f.read()

# Convert markdown to HTML
html_text = markdown.markdown(md_text)

# Create PDF document
doc = SimpleDocTemplate(output_file, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
story = []

# Get styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=18,
    textColor=colors.HexColor('#2C5F2D'),
    spaceAfter=12,
    keepWithNext=True
)
heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#4A7C59'),
    spaceAfter=10,
    keepWithNext=True,
    spaceBefore=6
)
body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['Normal'],
    fontSize=11,
    spaceAfter=8,
    leading=14
)
code_style = ParagraphStyle(
    'Code',
    parent=styles['Normal'],
    fontSize=9,
    fontName='Courier',
    textColor=colors.HexColor('#333333'),
    spaceAfter=6,
    leftIndent=20
)

# Parse HTML and add to story
lines = html_text.split('\n')
for line in lines:
    line = line.strip()
    if not line:
        story.append(Spacer(1, 0.1*inch))
    elif line.startswith('<h1>'):
        text = line.replace('<h1>', '').replace('</h1>', '')
        story.append(Paragraph(text, title_style))
        story.append(Spacer(1, 0.1*inch))
    elif line.startswith('<h2>'):
        text = line.replace('<h2>', '').replace('</h2>', '')
        story.append(Paragraph(text, heading_style))
    elif line.startswith('<h3>'):
        text = line.replace('<h3>', '').replace('</h3>', '')
        story.append(Paragraph(text, heading_style))
    elif line.startswith('<li>'):
        text = line.replace('<li>', '• ').replace('</li>', '')
        story.append(Paragraph(text, body_style))
    elif line.startswith('<p>'):
        text = line.replace('<p>', '').replace('</p>', '')
        if text:
            story.append(Paragraph(text, body_style))
    elif line.startswith('<code>'):
        text = line.replace('<code>', '').replace('</code>', '')
        story.append(Paragraph(f'<font face="Courier">{text}</font>', code_style))
    elif line.startswith('<pre>'):
        # Handle code blocks
        continue
    else:
        if line and not line.startswith('<'):
            story.append(Paragraph(line, body_style))

# Build PDF
try:
    doc.build(story)
    print(f"PDF created successfully: {output_file}")
except Exception as e:
    print(f"Error creating PDF: {e}")
