"""Build the readable report and figure from verified analysis artifacts."""
import argparse
import html
import json
import os
from pathlib import Path
import re
from string import Template

os.environ.setdefault('MPLCONFIGDIR', '/tmp/ece750-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent


def signed(value):
    return f'{value:+.2f}'.replace('-', '−') if value else '0.00'


def interval(values):
    return '[' + ', '.join(signed(v) for v in values) + ']'


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(row) + ' |' for row in rows])


def rate(b):
    n, positive, unknown = b['assigned'], b['positive'], b['unknown']
    if unknown:
        return f'{positive}–{positive + unknown}/{n} ({100*positive/n:.1f}–{100*(positive+unknown)/n:.1f}%)'
    return f'{positive}/{n} ({100*positive/n:.1f}%)'


def make_figure(data, output):
    p = data['primary']
    effects = [*p['all_assigned_bounds_pp'], p['complete_item_sensitivity']['estimate_pp']]
    cis = [p['bound_endpoint_percentile_95_intervals_pp']['lower'],
           p['bound_endpoint_percentile_95_intervals_pp']['upper'],
           p['complete_item_sensitivity']['percentile_95_interval_pp']]
    fig, ax = plt.subplots(figsize=(7, 2.2), constrained_layout=True)
    ax.axvline(0, color='#77818b', lw=1, ls='--')
    labels = ['Lower bound endpoint (60)', 'Upper bound endpoint (60)', 'Complete-item sensitivity (59)']
    for y, effect, ci in zip([2, 1, 0], effects, cis):
        ax.errorbar(effect, y, xerr=[[effect-ci[0]], [ci[1]-effect]],
                    fmt='o', color='#185b7c', capsize=4, lw=1.8)
    ax.set_yticks([2, 1, 0], labels, fontsize=9)
    ax.set_ylim(-.6, 2.6)
    ax.set_xlim(-17, 8)
    ax.set_xticks([-15, -10, -5, 0, 5])
    ax.set_xlabel('Visible reasoning − answer only (percentage points)', fontsize=10)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.grid(axis='x', alpha=.12)
    fig.savefig(output / 'primary-contrast.png', dpi=220)
    fig.savefig(output / 'primary-contrast.pdf')
    plt.close(fig)


def inline(text):
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#185b7c">\1</link>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', text)
    return text


def render_pdf(markdown, output):
    fonts = Path(matplotlib.get_data_path()) / 'fonts/ttf'
    for name, file in [('Body', 'DejaVuSerif.ttf'), ('BodyBold', 'DejaVuSerif-Bold.ttf'),
                       ('BodyItalic', 'DejaVuSerif-Italic.ttf'), ('BodyBoldItalic', 'DejaVuSerif-BoldItalic.ttf'),
                       ('Heading', 'DejaVuSans.ttf'), ('HeadingBold', 'DejaVuSans-Bold.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(fonts / file)))
    pdfmetrics.registerFontFamily('Body', normal='Body', bold='BodyBold', italic='BodyItalic', boldItalic='BodyBoldItalic')
    base = ParagraphStyle('body', fontName='Body', fontSize=10.5, leading=14.0,
                          spaceAfter=8, alignment=TA_LEFT, textColor=colors.HexColor('#202831'))
    styles = {
        'p': base,
        'title': ParagraphStyle('title', parent=base, fontName='HeadingBold', fontSize=21, leading=25, spaceAfter=8),
        'subtitle': ParagraphStyle('subtitle', parent=base, fontName='Heading', fontSize=12, leading=17, spaceAfter=10),
        'section': ParagraphStyle('section', parent=base, fontName='HeadingBold', fontSize=12, leading=16, spaceBefore=7, spaceAfter=7, keepWithNext=True),
        'caption': ParagraphStyle('caption', parent=base, fontSize=8.8, leading=12, spaceAfter=8),
        'cell': ParagraphStyle('cell', parent=base, fontSize=9, leading=12, spaceAfter=0),
    }
    story = []
    lines = markdown.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line == '<!-- pagebreak -->':
            story.append(PageBreak())
        elif line.startswith('!['):
            story.append(Image(str(output / 'primary-contrast.png'), width=504, height=158.4))
        elif line.startswith('|'):
            group = [line]
            while i < len(lines) and lines[i].strip().startswith('|'):
                group.append(lines[i].strip()); i += 1
            cells = [[Paragraph(inline(v.strip()), styles['cell']) for v in row.strip('|').split('|')]
                     for row in group if not re.fullmatch(r'[|\s:-]+', row)]
            widths = [140, 364] if len(cells[0]) == 2 else [138, 183, 183]
            if 'Secondary scoring policy' in group[0]:
                widths = [220, 284]
            tab = Table(cells, colWidths=widths, hAlign='LEFT')
            tab.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaf1f5')),
                ('LINEBELOW', (0, 0), (-1, 0), .6, colors.HexColor('#7793a3')),
                ('LINEBELOW', (0, -1), (-1, -1), .5, colors.HexColor('#7793a3')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.extend([tab, Spacer(1, 9)])
        else:
            if line.startswith('# '):
                style, line = 'title', line[2:]
            elif line.startswith('## '):
                style, line = 'subtitle', line[3:]
            elif line.startswith('### '):
                style, line = 'section', line[4:]
            else:
                style = 'caption' if line.startswith('Figure 1.') else 'p'
                while i < len(lines) and lines[i].strip():
                    line += ' ' + lines[i].strip(); i += 1
            story.append(Paragraph(inline(line), styles[style]))

    def footer(canvas, doc):
        canvas.setFont('Heading', 8)
        canvas.setFillColor(colors.HexColor('#667683'))
        canvas.drawString(54, 28, 'ECE 750T · Reasoning Under Observation')
        canvas.drawRightString(558, 28, str(doc.page))
    doc = SimpleDocTemplate(str(output / 'final-report.pdf'), pagesize=letter,
                            rightMargin=54, leftMargin=54, topMargin=40, bottomMargin=43,
                            title='Reasoning Under Observation', author='Yehia Fahmy')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    pdf = PdfReader(output / 'final-report.pdf')
    if len(pdf.pages) != 5:
        raise ValueError(f'Expected four main pages and one reference page, got {len(pdf.pages)}; edit text before release')
    expected = ['Reasoning Under Observation', '3. Automated grading', '4. Results', '5. Reliability', 'References']
    for page, heading in zip(pdf.pages, expected):
        if heading not in page.extract_text():
            raise ValueError('Page content flowed beyond its intended section: ' + heading)
    return len(pdf.pages)


def build(data, output):
    output.mkdir(parents=True, exist_ok=True)
    p, controls = data['primary'], data['controls']
    scenarios = data['automated_label_robustness']
    values = {
        'primary_bounds': f"{signed(p['all_assigned_bounds_pp'][0])} to {signed(p['all_assigned_bounds_pp'][1])}",
        'lower_interval': interval(p['bound_endpoint_percentile_95_intervals_pp']['lower']),
        'upper_interval': interval(p['bound_endpoint_percentile_95_intervals_pp']['upper']),
        'complete_effect': signed(p['complete_item_sensitivity']['estimate_pp']),
        'complete_interval': interval(p['complete_item_sensitivity']['percentile_95_interval_pp']),
        'control_hint': signed(controls['hint_agreement']['estimate_pp']),
        'control_hint_interval': interval(controls['hint_agreement']['percentile_95_interval_pp']),
        'control_accuracy': f"{abs(controls['correct']['estimate_pp']):.2f}",
        'control_accuracy_interval': interval(controls['correct']['percentile_95_interval_pp']),
        'secondary_bounds': interval(scenarios['semantic_judge']['secondary_contrast']['all_assigned_bounds_pp']),
        'one_error_bounds': interval(data['label_error_sensitivity'][1]['all_assigned_bounds_pp']),
        'two_error_bounds': interval(data['label_error_sensitivity'][2]['all_assigned_bounds_pp']),
        'condition_design': table(['Condition', 'Prompt content'], [
            ['C0: no hint', 'Question only; no observer mentioned'],
            ['C1: hint only', 'Question plus incorrect suggestion'],
            ['D-R: reasoning visible', 'Hint plus developer sees reasoning and answer'],
            ['D-A: answer only', 'Hint plus developer sees only the answer']]),
        'outcome_table': table(['Condition', 'Correct answers', 'Wrong-option agreement'], [
            [name, rate(data['by_condition'][c]['correct']), rate(data['by_condition'][c]['hint_agreement'])]
            for c, name in [('C0', 'No hint'), ('C1', 'Hint only'), ('D-R', 'Reasoning visible'), ('D-A', 'Answer only')]]),
        'robustness_table': table(['Secondary scoring policy', 'Visible minus answer-only range (pp)'], [
            [name, interval(scenarios[key]['secondary_contrast']['all_assigned_bounds_pp'])]
            for key, name in [('semantic_judge', 'Semantic judge'), ('phrase_proxy', 'Phrase proxy'),
                              ('disagreement_abstention', 'Abstain on disagreement'), ('no_semantic_labels', 'All semantic labels unknown')]])}
    markdown = Template((HERE / 'report-template.md').read_text()).substitute(values)
    (output / 'final-report.md').write_text(markdown)
    make_figure(data, output)
    pages = render_pdf(markdown, output)
    print(f'Built {pages}-page report at {output / "final-report.pdf"}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis', type=Path, default=HERE.parent / 'results/final-automated-evaluation.json')
    parser.add_argument('--out', type=Path, default=HERE)
    args = parser.parse_args()
    build(json.loads(args.analysis.read_text()), args.out)
