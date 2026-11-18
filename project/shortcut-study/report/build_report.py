"""Build the shortcut-study final report PDF and figure from tracked main stats."""
from __future__ import annotations

import argparse
import html
import json
import os
import re
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/ece750-matplotlib")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STATS_DEFAULT = ROOT / "results" / "main" / "main-s0-tab-v0-20261118-stats.json"


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<link href="\2" color="#185b7c">\1</link>',
        text,
    )
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r"<font face='Courier' size='8'>\1</font>", text)
    return text


def make_figure(stats: dict, output: Path) -> None:
    info = stats["key_contrasts_among_completed"]["information_state_authorized"]
    labels = ["Complete info", "Incomplete info"]
    rates = [100 * info["complete"]["rate"], 100 * info["incomplete"]["rate"]]
    counts = [
        f"{info['complete']['authorized']}/{info['complete']['n']}",
        f"{info['incomplete']['authorized']}/{info['incomplete']['n']}",
    ]
    fig, ax = plt.subplots(figsize=(6.4, 2.4), constrained_layout=True)
    bars = ax.barh(labels[::-1], rates[::-1], color=["#7a8b96", "#185b7c"][::-1], height=0.55)
    for bar, count, rate in zip(bars, counts[::-1], rates[::-1]):
        ax.text(
            rate + 1.2,
            bar.get_y() + bar.get_height() / 2,
            f"{rate:.1f}% ({count})",
            va="center",
            fontsize=9,
            color="#202831",
        )
    ax.set_xlim(0, 45)
    ax.set_xlabel("Authorized success among completed cells (%)", fontsize=10)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", alpha=0.12)
    fig.savefig(output / "info-contrast.png", dpi=220)
    fig.savefig(output / "info-contrast.pdf")
    plt.close(fig)


def render_pdf(markdown: str, output: Path) -> int:
    fonts = Path(matplotlib.get_data_path()) / "fonts/ttf"
    for name, file in [
        ("Body", "DejaVuSerif.ttf"),
        ("BodyBold", "DejaVuSerif-Bold.ttf"),
        ("BodyItalic", "DejaVuSerif-Italic.ttf"),
        ("BodyBoldItalic", "DejaVuSerif-BoldItalic.ttf"),
        ("Heading", "DejaVuSans.ttf"),
        ("HeadingBold", "DejaVuSans-Bold.ttf"),
        ("Courier", "DejaVuSansMono.ttf"),
    ]:
        pdfmetrics.registerFont(TTFont(name, str(fonts / file)))
    pdfmetrics.registerFontFamily(
        "Body",
        normal="Body",
        bold="BodyBold",
        italic="BodyItalic",
        boldItalic="BodyBoldItalic",
    )
    base = ParagraphStyle(
        "body",
        fontName="Body",
        fontSize=10.2,
        leading=13.4,
        spaceAfter=7,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#202831"),
    )
    styles = {
        "p": base,
        "title": ParagraphStyle(
            "title", parent=base, fontName="HeadingBold", fontSize=18, leading=22, spaceAfter=6
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base, fontName="Heading", fontSize=11, leading=15, spaceAfter=8
        ),
        "section": ParagraphStyle(
            "section",
            parent=base,
            fontName="HeadingBold",
            fontSize=11.5,
            leading=15,
            spaceBefore=6,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "caption": ParagraphStyle("caption", parent=base, fontSize=8.6, leading=11.5, spaceAfter=7),
        "cell": ParagraphStyle("cell", parent=base, fontSize=8.4, leading=11, spaceAfter=0),
        "quote": ParagraphStyle(
            "quote",
            parent=base,
            fontSize=9.0,
            leading=12.0,
            textColor=colors.HexColor("#33404a"),
            leftIndent=8,
            rightIndent=8,
            spaceAfter=8,
        ),
        "code": ParagraphStyle(
            "code",
            parent=base,
            fontName="Courier",
            fontSize=7.8,
            leading=10.2,
            backColor=colors.HexColor("#f3f6f8"),
            spaceAfter=8,
        ),
    }
    story = []
    lines = markdown.splitlines()
    i = 0
    in_code = False
    code_buf: list[str] = []
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        i += 1
        if line.strip().startswith("```"):
            if in_code:
                story.append(Paragraph(inline("\n".join(code_buf)), styles["code"]))
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        if not line.strip():
            continue
        if line.strip() == "<!-- pagebreak -->":
            story.append(PageBreak())
            continue
        if line.startswith("> "):
            story.append(Paragraph(inline(line[2:]), styles["quote"]))
            continue
        if line.startswith("!["):
            story.append(Image(str(output / "info-contrast.png"), width=470, height=176))
            continue
        if line.startswith("|"):
            group = [line]
            while i < len(lines) and lines[i].strip().startswith("|"):
                group.append(lines[i].strip())
                i += 1
            cells = [
                [Paragraph(inline(v.strip()), styles["cell"]) for v in row.strip("|").split("|")]
                for row in group
                if not re.fullmatch(r"[|\s:-]+", row)
            ]
            ncols = len(cells[0])
            if ncols == 2:
                widths = [190, 314]
            elif ncols == 3:
                widths = [150, 177, 177]
            else:
                widths = [504 / ncols] * ncols
            tab = Table(cells, colWidths=widths, hAlign="LEFT")
            tab.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eaf1f5")),
                        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#7793a3")),
                        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#7793a3")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story.extend([tab, Spacer(1, 8)])
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), styles["title"]))
        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), styles["subtitle"]))
        elif line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), styles["section"]))
        else:
            text = line
            style = "caption" if text.startswith("Figure 1.") else "p"
            while i < len(lines) and lines[i].strip() and not lines[i].startswith(
                ("#", "|", ">", "!", "`", "<!--")
            ):
                text += " " + lines[i].strip()
                i += 1
            story.append(Paragraph(inline(text), styles[style]))

    def footer(canvas, doc):
        canvas.setFont("Heading", 8)
        canvas.setFillColor(colors.HexColor("#667683"))
        canvas.drawString(54, 28, "ECE 750T · Shortcut study extension · submission_authorized=false")
        canvas.drawRightString(558, 28, str(doc.page))

    pdf_path = output / "final-report.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=40,
        bottomMargin=43,
        title="Shortcut acquisition under declared reviewer visibility",
        author="Yehia Fahmy",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    pages = len(PdfReader(str(pdf_path)).pages)
    if pages < 5:
        raise ValueError(f"Expected at least 5 pages (4 core + refs/appendix), got {pages}")
    return pages


def build(stats_path: Path, markdown_path: Path, output: Path) -> None:
    stats = json.loads(stats_path.read_text())
    if stats.get("submission_authorized") is not False:
        raise ValueError("stats JSON must keep submission_authorized=false")
    output.mkdir(parents=True, exist_ok=True)
    markdown = markdown_path.read_text()
    make_figure(stats, output)
    pages = render_pdf(markdown, output)
    print(f"Built {pages}-page report at {output / 'final-report.pdf'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stats", type=Path, default=STATS_DEFAULT)
    parser.add_argument("--markdown", type=Path, default=HERE / "final-report.md")
    parser.add_argument("--out", type=Path, default=HERE)
    args = parser.parse_args()
    build(args.stats, args.markdown, args.out)
