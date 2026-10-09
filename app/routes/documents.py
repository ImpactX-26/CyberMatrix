from pathlib import Path
import re
import uuid

from fastapi import APIRouter, File, UploadFile, HTTPException

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def extract_text(path: Path, filename: str) -> str:
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    if suffix == ".pdf":
        if PdfReader is None:
            raise HTTPException(
                status_code=500,
                detail="PDF reader is not installed.",
            )

        reader = PdfReader(str(path))

        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages)

    return ""


def find_lines(text: str, terms):
    lines = text.splitlines()
    matches = []

    for index, line in enumerate(lines):
        lowered = line.lower()

        if any(term.lower() in lowered for term in terms):
            matches.append(
                {
                    "line_number": index + 1,
                    "text": line.strip(),
                }
            )

    return matches


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename supplied.",
        )

    allowed = {
        ".pdf",
        ".txt",
        ".jpg",
        ".jpeg",
        ".png",
    }

    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed:
        raise HTTPException(
            status_code=400,
            detail="Unsupported document type.",
        )

    document_id = str(uuid.uuid4())

    safe_name = (
        f"{document_id}{suffix}"
    )

    path = UPLOAD_DIR / safe_name

    content = await file.read()

    path.write_bytes(content)

    text = ""

    if suffix in {".pdf", ".txt"}:
        text = extract_text(
            path,
            file.filename,
        )

    survey_matches = find_lines(
        text,
        [
            "survey",
            "survey number",
            "sy.no",
            "sy no",
        ],
    )

    owner_matches = find_lines(
        text,
        [
            "owner",
            "seller",
            "buyer",
            "purchaser",
            "vendor",
        ],
    )

    mortgage_matches = find_lines(
        text,
        [
            "mortgage",
            "mortgagee",
            "loan",
            "encumbrance",
            "charge",
        ],
    )

    return {
        "document_id": document_id,
        "filename": file.filename,
        "document_type": (
            "registration"
            if "reg" in file.filename.lower()
            else "mortgage"
            if "mortgage" in file.filename.lower()
            else "document"
        ),
        "text_extracted": bool(text.strip()),
        "text_length": len(text),
        "evidence": {
            "survey": survey_matches[:10],
            "ownership": owner_matches[:15],
            "mortgage": mortgage_matches[:15],
        },
        "message": (
            "Document analyzed successfully."
            if text.strip()
            else
            "Document uploaded. Text extraction is not available for this image format."
        ),
    }

