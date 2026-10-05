"""
Regression gate retrieval (integration — butuh GPU/model + vector DB app).

Menjalankan eval_retrieval.py di submodule app memakai interpreter venv aplikasi
(IKU_APP_PYTHON), membaca laporan JSON terbaru di app/reports/evaluation/, lalu
membandingkan metrik dengan tests/data/golden_metrics.json. GAGAL bila metrik
turun di bawah ambang.

Di-skip otomatis bila IKU_APP_PYTHON tidak di-set (lihat conftest.py).
"""

import glob
import json
import os
import subprocess

import pytest

from qa_utils.paths import APP_ROOT, GOLDEN_METRICS

pytestmark = pytest.mark.integration

GOLDEN = json.loads(GOLDEN_METRICS.read_text(encoding="utf-8"))


def _latest_eval_json():
    pattern = str(APP_ROOT / "reports" / "evaluation" / "retrieval_eval_*.json")
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None


@pytest.fixture(scope="module")
def eval_report(app_root):
    py = os.environ["IKU_APP_PYTHON"]
    # Jalankan evaluasi retrieval di lingkungan app.
    subprocess.run(
        [py, "src/evaluation/eval_retrieval.py"],
        cwd=str(app_root), check=True, timeout=1800,
    )
    path = _latest_eval_json()
    if not path:
        pytest.fail("tidak ada laporan retrieval_eval_*.json dihasilkan")
    return json.loads(open(path, encoding="utf-8").read())


def test_hit_at_1_tidak_turun(eval_report):
    actual = _metric(eval_report, "hit_at_1", "hit@1")
    assert actual >= GOLDEN["thresholds"]["hit_at_1_pct"], (
        f"Hit@1 turun: {actual} < {GOLDEN['thresholds']['hit_at_1_pct']}"
    )


def test_mrr_at_5_tidak_turun(eval_report):
    actual = _metric(eval_report, "mrr_at_5", "mrr@5", "mrr")
    assert actual >= GOLDEN["thresholds"]["mrr_at_5"], (
        f"MRR@5 turun: {actual} < {GOLDEN['thresholds']['mrr_at_5']}"
    )


def _metric(report, *keys):
    """Ambil metrik dari laporan dengan toleransi nama kunci (skema laporan app
    bisa berbeda; sesuaikan di sini bila perlu)."""
    flat = report.get("metrics", report)
    for k in keys:
        if k in flat:
            return float(flat[k])
    pytest.skip(f"metrik {keys} tidak ditemukan di laporan; sesuaikan _metric() dengan skema app")
