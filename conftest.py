"""
conftest.py — bootstrap QA suite.

Menyisipkan modul kalkulator/generation dari submodule app/ ke sys.path supaya
test bisa `import iku_formulas`, `import tools`, `import prompt` persis seperti
kode aplikasi memakainya (lihat app/tests/conftest.py dan app/src/generation/tools.py).

Juga mendaftarkan auto-skip untuk suite 'integration' bila lingkungan GPU/LLM
(variabel IKU_APP_PYTHON) tidak di-set.
"""

import os
import sys
from pathlib import Path

import pytest

QA_ROOT = Path(__file__).resolve().parent
APP_ROOT = QA_ROOT / "app"

# Jalur modul yang diuji, sama dengan yang dipakai aplikasi.
for rel in ("src/calculator", "src/generation"):
    p = APP_ROOT / rel
    if p.is_dir():
        sys.path.insert(0, str(p))


def pytest_collection_modifyitems(config, items):
    """Skip semua test 'integration' kecuali IKU_APP_PYTHON di-set (venv app
    yang punya torch + chromadb + bge-m3)."""
    if os.environ.get("IKU_APP_PYTHON"):
        return
    skip = pytest.mark.skip(reason="integration: set IKU_APP_PYTHON ke python venv aplikasi untuk menjalankan")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def app_root() -> Path:
    if not (APP_ROOT / "src").is_dir():
        pytest.skip("submodule app/ belum di-init — jalankan: git submodule update --init --recursive")
    return APP_ROOT
