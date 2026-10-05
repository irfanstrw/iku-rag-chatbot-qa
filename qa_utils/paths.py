"""Resolusi path ke submodule app/, aman dari direktori kerja mana pun."""

from pathlib import Path

QA_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = QA_ROOT / "app"

# Dataset soal hitungan yang di-commit di repo utama (dipakai juga oleh unit test).
CALC_DATASET = APP_ROOT / "data" / "evaluation" / "test_inputs_hitung.json"
GOLDEN_METRICS = QA_ROOT / "tests" / "data" / "golden_metrics.json"
