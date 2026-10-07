import re
import subprocess
from datetime import datetime
from pathlib import Path

PRINT_TIMEOUT = 60

def make_pdf_path(output_dir: str, event_id: str, sent_at: datetime) -> Path:
    safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", event_id)
    day_dir = Path(output_dir) / sent_at.strftime("%Y-%m-%d")
    return day_dir / f"{sent_at:%H%M%S}_{safe_id}.pdf"

def save_pdf(pdf_bytes: bytes, output_dir: str, event_id: str, sent_at: datetime) -> Path:
    path = make_pdf_path(output_dir, event_id, sent_at)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pdf_bytes)
    return path

def print_file(path: Path, printer_name: str) -> None:
    subprocess.run(
        ["lp", "-d", printer_name, str(path)],
        check=True,
        capture_output=True,
        timeout=PRINT_TIMEOUT,
    )