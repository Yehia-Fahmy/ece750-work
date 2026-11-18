"""Build a simple PDF slide deck from slides.md (no pptx dependency)."""
from __future__ import annotations

import argparse
import html
import os
import re
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/ece750-matplotlib")
import matplotlib
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer

HERE = Path(__file__).resolve().parent
PAGE = landscape(letter)


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r"<font face='Courier' size='14'>\1</font>", text)
    return text


def parse_slides(markdown: str) -> list[dict]:
    chunks = [c.strip() for c in re.split(r"\n---\n", markdown)]
    slides = []
    for chunk in chunks:
        lines = [ln.rstrip() for ln in chunk.splitlines() if ln.strip()]
        if not lines:
            continue
        title = lines[0][2:].strip() if lines[0].startswith("# ") else lines[0]
        body = []
        for ln in lines[1:]:
            if ln.startswith("# "):
                body.append(ln[2:].strip())
            elif ln.startswith("- "):
                body.append(ln[2:].strip())
            else:
                body.append(ln)
        slides.append({"title": title, "body": body})
    return slides


def build(markdown_path: Path, output: Path) -> int:
    fonts = Path(matplotlib.get_data_path()) / "fonts/ttf"
    for name, file in [
        ("Heading", "DejaVuSans.ttf"),
        ("HeadingBold", "DejaVuSans-Bold.ttf"),
        ("Body", "DejaVuSerif.ttf"),
        ("BodyBold", "DejaVuSerif.ttf"),
        ("Courier", "DejaVuSansMono.ttf"),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(fonts / file)))

    title_style = ParagraphStyle(
        "slide_title",
        fontName="HeadingBold",
        fontSize=28,
        leading=34,
        textColor=colors.HexColor("#132029"),
        alignment=TA_LEFT,
        spaceAfter=18,
    )
    body_style = ParagraphStyle(
        "slide_body",
        fontName="Body",
        fontSize=18,
        leading=26,
        textColor=colors.HexColor("#24313a"),
        alignment=TA_LEFT,
        spaceAfter=10,
    )
    footer_style = ParagraphStyle(
        "slide_footer",
        fontName="Heading",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#667683"),
        alignment=TA_CENTER,
    )

    slides = parse_slides(markdown_path.read_text())
    output.mkdir(parents=True, exist_ok=True)
    pdf_path = output / "slides.pdf"

    doc = BaseDocTemplate(
        str(pdf_path),
        pagesize=PAGE,
        title="Shortcut study — final slides",
        author="Yehia Fahmy",
    )
    frame = Frame(54, 48, PAGE[0] - 108, PAGE[1] - 96, id="normal")
    doc.addPageTemplates([PageTemplate(id="slide", frames=[frame])])

    story = []
    for idx, slide in enumerate(slides, start=1):
        story.append(Paragraph(inline(slide["title"]), title_style))
        story.append(Spacer(1, 10))
        for line in slide["body"]:
            story.append(Paragraph(inline(f"• {line}"), body_style))
        story.append(Spacer(1, 18))
        story.append(
            Paragraph(
                inline(
                    f"ECE 750T · Yehia Fahmy · slide {idx}/{len(slides)} · submission_authorized=false"
                ),
                footer_style,
            )
        )
        if idx != len(slides):
            story.append(PageBreak())

    doc.build(story)
    pages = len(PdfReader(str(pdf_path)).pages)
    if pages != len(slides):
        raise ValueError(f"Expected {len(slides)} slides, got {pages} pages")
    print(f"Built {pages}-page deck at {pdf_path}")
    return pages


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--markdown", type=Path, default=HERE / "slides.md")
    parser.add_argument("--out", type=Path, default=HERE)
    args = parser.parse_args()
    build(args.markdown, args.out)
