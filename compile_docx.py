import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def create_element(name):
    return OxmlElement(name)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def build_docx(md_path, docx_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = docx.Document()

    # Set page margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base normal style configuration
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    style.paragraph_format.line_spacing = 1.25
    style.paragraph_format.space_after = Pt(6)

    in_references = False
    in_mermaid = False

    for line in lines:
        raw_line = line.rstrip('\r\n')
        stripped = raw_line.strip()

        # Handle mermaid blocks
        if stripped.startswith('```mermaid'):
            in_mermaid = True
            continue
        elif in_mermaid and stripped.startswith('```'):
            in_mermaid = False
            continue
        elif in_mermaid:
            continue

        # Skip horizontal rules
        if stripped in ['---', '***', '___']:
            continue

        # Detect References section
        if stripped.startswith('## References'):
            in_references = True

        # Heading 1 (# ...)
        if stripped.startswith('# '):
            title_text = stripped[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(18)
            p.paragraph_format.space_after = Pt(12)
            run = p.add_run(title_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
            continue

        # Heading 2 (## ...)
        if stripped.startswith('## '):
            h2_text = stripped[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(h2_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x1a, 0x36, 0x5d) # Academic Navy
            continue

        # Heading 3 (### ...)
        if stripped.startswith('### '):
            h3_text = stripped[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(h3_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x2c, 0x52, 0x82)
            continue

        # Blockquote (> ...)
        if stripped.startswith('> '):
            quote_text = stripped[2:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.right_indent = Inches(0.5)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(quote_text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11)
            run.font.italic = True
            run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            continue

        # Bullet list (- ...)
        if stripped.startswith('- ') or stripped.startswith('* '):
            item_text = stripped[2:].strip()
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(3)
            if in_references:
                p.paragraph_format.left_indent = Inches(0.5)
                p.paragraph_format.first_line_indent = Inches(-0.5)
            add_formatted_runs(p, item_text)
            continue

        # Numbered list (1. ...)
        match_num = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if match_num:
            item_text = match_num.group(2)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_after = Pt(3)
            add_formatted_runs(p, item_text)
            continue

        # Empty lines
        if not stripped:
            continue

        # Regular paragraph
        p = doc.add_paragraph()
        if in_references:
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.first_line_indent = Inches(-0.5)
            p.paragraph_format.space_after = Pt(4)
        else:
            p.paragraph_format.space_after = Pt(6)
        add_formatted_runs(p, stripped)

    doc.save(docx_path)
    print(f"Successfully compiled: {docx_path}")

def add_formatted_runs(paragraph, text):
    # Regex parser for bold (**...**) and italic (*...*)
    tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*)', text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('**') and token.endswith('**') and len(token) >= 4:
            run = paragraph.add_run(token[2:-2])
            run.font.bold = True
            run.font.name = 'Times New Roman'
        elif token.startswith('*') and token.endswith('*') and len(token) >= 2:
            run = paragraph.add_run(token[1:-1])
            run.font.italic = True
            run.font.name = 'Times New Roman'
        else:
            run = paragraph.add_run(token)
            run.font.name = 'Times New Roman'

if __name__ == '__main__':
    base_dir = r"C:\Users\ismai\.gemini\antigravity\scratch\research\battlefield-bad-company-2"
    md_file = os.path.join(base_dir, "12_FULL_RESEARCH_PAPER.md")
    docx_file = os.path.join(base_dir, "manuscript_build.docx")
    build_docx(md_file, docx_file)
