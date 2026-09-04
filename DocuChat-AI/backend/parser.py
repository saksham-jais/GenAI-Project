from dataclasses import dataclass
import fitz
import re


@dataclass
class DocumentBlock:
    text: str
    page: int
    kind: str
    heading: str | None = None


def parse_pdf(path: str) -> tuple[list[DocumentBlock], dict[str, str | int]]:
    blocks: list[DocumentBlock] = []
    pdf = fitz.open(path)
    metadata = {
        "title": pdf.metadata.get("title") or "Untitled document",
        "author": pdf.metadata.get("author") or "Unknown author",
        "pages": len(pdf),
    }
    current_heading: str | None = None

    for page_number, page in enumerate(pdf, start=1):
        text = page.get_text("text").strip()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        table_lines: list[str] = []
        prose_lines: list[str] = []
        for line in lines:
            is_table_row = "\t" in line or bool(re.search(r"\s{3,}", line))
            if is_table_row:
                table_lines.append(line)
            elif table_lines:
                blocks.append(DocumentBlock("\n".join(table_lines), page_number, "table", current_heading))
                table_lines = []
                prose_lines.append(line)
            else:
                prose_lines.append(line)
        if table_lines:
            blocks.append(DocumentBlock("\n".join(table_lines), page_number, "table", current_heading))

        prose = "\n".join(prose_lines).strip()
        if prose:
            paragraphs = re.split(r"\n{2,}", prose)
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                if len(paragraph) < 100 and (paragraph.isupper() or paragraph.endswith(":") or re.match(r"^(\d+[.)]|[A-Z][.)])\s", paragraph)):
                    current_heading = paragraph
                    kind = "heading"
                else:
                    kind = "text"
                blocks.append(DocumentBlock(paragraph, page_number, kind, current_heading))
    pdf.close()
    return blocks, metadata