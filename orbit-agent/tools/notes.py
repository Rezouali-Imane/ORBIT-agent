import json
from pathlib import Path

from langchain_core.tools import tool


NOTES_PATH = Path(__file__).resolve().parents[1] / "data" / "notes.json"


@tool("save_note")
def save_note(title: str, content: str) -> str:
    """Save an approved project note to the local notes file."""
    NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        notes = json.loads(NOTES_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        notes = []

    if not isinstance(notes, list):
        raise ValueError(f"{NOTES_PATH} must contain a JSON list")

    notes.append({"title": title, "content": content})
    NOTES_PATH.write_text(
        json.dumps(notes, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return f"Saved note: {title}"