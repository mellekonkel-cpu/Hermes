#!/usr/bin/env python3
"""Generate a Chinese-capable PDF from a UTF-8 text briefing file.

Requires: fpdf2, fontTools (auto-installed via curl + setup.py if missing)
Requires: wqy-zenhei.ttc (at /usr/share/fonts/truetype/wqy/)

Usage:
    python3 gen_pdf.py <input.txt> <output.pdf>
"""

import os, sys, subprocess, tempfile, shutil

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
FPDF2_TGZ = "https://files.pythonhosted.org/packages/source/f/fpdf2/fpdf2-2.8.1.tar.gz"
FONTTOOLS_TGZ = "https://files.pythonhosted.org/packages/source/f/fonttools/fonttools-4.55.3.tar.gz"
USER_SITE = os.path.expanduser("~/.local/lib/python3.13/site-packages")


def ensure_deps():
    missing = []
    try:
        import fpdf
    except ImportError:
        missing.append("fpdf2")
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        missing.append("fontTools")
    if not missing:
        return
    tmp = tempfile.mkdtemp()
    try:
        for name, url in [("fontTools", FONTTOOLS_TGZ), ("fpdf2", FPDF2_TGZ)]:
            if name not in missing:
                continue
            tgz = os.path.join(tmp, f"{name}.tar.gz")
            subprocess.run(["curl", "-sL", "--max-time", "30", url, "-o", tgz], capture_output=True, timeout=35).check_returncode()
            subprocess.run(["tar", "xzf", tgz, "-C", tmp], capture_output=True, timeout=10).check_returncode()
            extracted = os.path.join(tmp, f"{name}-2.8.1" if name == "fpdf2" else "fonttools-4.55.3")
            subprocess.run([sys.executable, "setup.py", "install", "--user"], cwd=extracted, capture_output=True, timeout=60).check_returncode()
        for mod in list(sys.modules.keys()):
            if "fpdf" in mod or "fonttools" in mod:
                sys.modules.pop(mod, None)
        sys.path.insert(0, USER_SITE)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def text_to_pdf(text_path, pdf_path):
    ensure_deps()
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, USER_SITE)
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
        elif line.startswith("原文："):
            pdf.set_font("WQY", "", 8)
            pdf.set_text_color(100, 100, 100)
            # Truncate long URL lines to prevent overflow with CJK fonts
            url = line
            if len(url) > 95:
                url = url[:95] + "..."
            pdf.cell(0, 5, url, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
        elif line.startswith("📌"):
            pdf.set_font("WQY", "", 11)
            pdf.multi_cell(0, 6, line)
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
