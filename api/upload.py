from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

from tools.ingest import DOCS_DIR, MAX_FILE_SIZE, SUPPORTED_SUFFIXES, ingest_file


app = FastAPI(title="ORBIT document upload")
UPLOAD_PAGE = Path(__file__).with_name("upload.html")


@app.get("/upload", response_class=HTMLResponse)
def upload_page() -> str:
    return UPLOAD_PAGE.read_text(encoding="utf-8")


@app.post("/upload")
def upload_document(file: UploadFile = File(...)) -> dict[str, str]:
    filename = Path(file.filename or "").name
    if Path(filename).suffix.lower() not in SUPPORTED_SUFFIXES:
        return {"result": "Unsupported file type. Only .pdf, .md, and .txt files are accepted."}

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    destination = DOCS_DIR / filename
    size = 0
    with destination.open("wb") as output:
        while block := file.file.read(1024 * 1024):
            size += len(block)
            if size > MAX_FILE_SIZE:
                destination.unlink(missing_ok=True)
                return {"result": "File is too large. The maximum allowed size is 20 MB."}
            output.write(block)

    return {"result": ingest_file(destination)}
