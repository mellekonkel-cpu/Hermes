#!/usr/bin/env python3
"""Generate a Chinese-capable PDF from a UTF-8 text briefing file.
Assumes fpdf2 is already installed at PYTHONPATH location.
"""
import os, sys

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

def text_to_pdf(text_path, pdf_path):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("WQY", "", FONT_PATH, uni=True)

    with open(text_path, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    for line in lines:
        if line.startswith("=== "):
            pdf.set_font("WQY", "", 16)
            pdf.cell(0, 10, line, new_x="LMARGIN", new_y="NEXT")
        elif line.startswith("── "):
            pdf.set_font("WQY", "", 14)
            pdf.set_text_color(30, 60, 130)
            pdf.cell(0, 8, line, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
        elif line == "":
            pdf.ln(3)
        elif line and line[0].isdigit() and ". " in line[:5]:
            pdf.set_font("WQY", "", 13)
            pdf.cell(0, 8, line, new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("WQY", "", 12)
            pdf.multi_cell(0, 6.5, line)

    pdf.output(pdf_path)
    size = os.path.getsize(pdf_path)
    print(f"PDF generated: {pdf_path} ({size} bytes)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input.txt> <output.pdf>")
        sys.exit(1)
    text_to_pdf(sys.argv[1], sys.argv[2])
