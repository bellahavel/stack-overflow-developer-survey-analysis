from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
INPUT_OUTPUTS = [
    (
        ROOT / "docs" / "milestone_3_narrative_draft.md",
        ROOT / "docs" / "Milestone_3_Narrative_Draft.pdf",
    ),
    (
        ROOT / "docs" / "final_narrative.md",
        ROOT / "docs" / "Final_Narrative.pdf",
    ),
]


def clean_inline_markdown(text: str) -> str:
    return text.replace("**", "").replace("`", "")


def build_story(lines: list[str]):
    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        spaceAfter=8,
    )

    story = []
    paragraph_buffer: list[str] = []

    def flush_paragraph():
        if paragraph_buffer:
            paragraph = " ".join(paragraph_buffer).strip()
            if paragraph:
                story.append(Paragraph(clean_inline_markdown(paragraph), body_style))
                story.append(Spacer(1, 0.08 * inch))
            paragraph_buffer.clear()

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            continue

        if line.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(clean_inline_markdown(line[2:]), title_style))
            story.append(Spacer(1, 0.15 * inch))
        elif line.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(clean_inline_markdown(line[3:]), heading_style))
            story.append(Spacer(1, 0.08 * inch))
        else:
            paragraph_buffer.append(line)

    flush_paragraph()
    return story


def write_pdf(md_path: Path, pdf_path: Path):
    lines = md_path.read_text().splitlines()
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.8 * inch,
        leftMargin=0.8 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )
    doc.build(build_story(lines))
    print(f"Wrote {pdf_path}")


def main():
    for md_path, pdf_path in INPUT_OUTPUTS:
        if md_path.exists():
            write_pdf(md_path, pdf_path)


if __name__ == "__main__":
    main()
