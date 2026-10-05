"""
Smoke test chatbot end-to-end (integration — butuh GPU/model + API key LLM).

Menjalankan chat_cli.py di app lewat IKU_APP_PYTHON, mengirim satu pertanyaan
definisi dan satu soal hitungan via stdin, lalu memeriksa:
- jawaban memuat rujukan [n]
- soal hitungan memunculkan hasil kalkulator yang benar (21,5% untuk IKU 3)

Di-skip otomatis bila IKU_APP_PYTHON tidak di-set.
"""

import os
import re
import subprocess

import pytest

pytestmark = pytest.mark.integration

PERTANYAAN_DEFINISI = "Apa itu IKU 3?"
PERTANYAAN_HITUNG = (
    "Sebuah PT punya 1000 mahasiswa. 100 magang 20 SKS, 150 pertukaran 8 SKS, "
    "50 riset 4 SKS, 5 juara 1 nasional, 10 finalis internasional. Berapa capaian IKU 3?"
)


@pytest.fixture(scope="module")
def chat_output(app_root):
    py = os.environ["IKU_APP_PYTHON"]
    stdin = f"{PERTANYAAN_DEFINISI}\n{PERTANYAAN_HITUNG}\n\n"  # Enter kosong = keluar
    proc = subprocess.run(
        [py, "src/generation/chat_cli.py", "--detail"],
        cwd=str(app_root), input=stdin, capture_output=True, text=True, timeout=600,
    )
    if proc.returncode != 0:
        pytest.fail(f"chat_cli.py gagal (rc={proc.returncode}):\n{proc.stderr[-2000:]}")
    return proc.stdout


def test_jawaban_mengandung_rujukan(chat_output):
    assert re.search(r"\[\d+\]", chat_output), "jawaban tidak memuat rujukan [n]"


def test_soal_hitungan_memakai_kalkulator_dengan_hasil_benar(chat_output):
    # Hasil IKU 3 untuk input di atas = 21,5% (lihat test set H07).
    assert ("21,5" in chat_output) or ("21.5" in chat_output), (
        "hasil kalkulator 21,5% tidak muncul — soal hitungan mungkin dijawab tanpa alat"
    )
