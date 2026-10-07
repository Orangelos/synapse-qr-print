import subprocess
from datetime import datetime
import pytest
from synapse_qr_print.storage import make_pdf_path, print_file, save_pdf

SENT_AT = datetime(2026, 10, 7, 11, 20, 5)
EVENT_ID = "$abc/DEF+123:localhost"

def test_path_is_inside_day_folder(tmp_path):
    path = make_pdf_path(str(tmp_path), EVENT_ID, SENT_AT)
    assert path.parent == tmp_path / "2026-10-07"
    assert path.name.startswith("112005_")
    assert path.suffix == ".pdf"

def test_unsafe_characters_are_replaced(tmp_path):
    path = make_pdf_path(str(tmp_path), EVENT_ID, SENT_AT)
    for ch in "$/:+":
        assert ch not in path.name

def test_save_creates_folders_and_file(tmp_path):
    output_dir = tmp_path / "pdf"  # такой папки ещё нет
    path = save_pdf(b"%PDF-test", str(output_dir), EVENT_ID, SENT_AT)
    assert path.exists()
    assert path.read_bytes() == b"%PDF-test"

def test_print_calls_lp_with_printer_and_file(tmp_path, monkeypatch):
    calls = []
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)
    monkeypatch.setattr(subprocess, "run", fake_run)
    file = tmp_path / "msg.pdf"
    print_file(file, "PDF")
    assert calls == [["lp", "-d", "PDF", str(file)]]
    
def test_print_error_is_raised(tmp_path, monkeypatch):
    def fake_run(cmd, **kwargs):
        raise subprocess.CalledProcessError(1, cmd, stderr=b"lp: printer not found")
    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(subprocess.CalledProcessError):
        print_file(tmp_path / "msg.pdf", "NoSuchPrinter")