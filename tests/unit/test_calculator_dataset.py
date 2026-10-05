"""
Test berbasis dataset: 18 soal hitungan (H01-H18) dari
app/data/evaluation/test_inputs_hitung.json dibandingkan dengan kunci jawaban.

Ini QA-mirror dari app/tests/test_iku_formulas.py, tetapi membaca dataset lewat
submodule sehingga selalu sinkron dengan test set yang dipakai evaluasi nyata.
"""

import json

import pytest

import iku_formulas as calc
from qa_utils.paths import CALC_DATASET

pytestmark = pytest.mark.unit

TOL = 0.01

if not CALC_DATASET.is_file():
    pytest.skip(f"dataset submodule tidak ada: {CALC_DATASET} — init submodule app/",
                allow_module_level=True)

CASES = json.loads(CALC_DATASET.read_text(encoding="utf-8"))["cases"]


def same(actual, expected) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(same(actual.get(k), v) for k, v in expected.items())
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(actual - expected) <= TOL
    return actual == expected


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_hasil_sesuai_kunci(case):
    out = calc.hitung(case["fungsi"], **case["argumen"])
    assert same(out["hasil"], case["harapan"]), (
        f"{case['id']}: hasil {out['hasil']!r} != kunci {case['harapan']!r}"
    )


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_keluaran_punya_langkah_dan_sumber(case):
    out = calc.hitung(case["fungsi"], **case["argumen"])
    assert out["langkah"], f"{case['id']}: langkah perhitungan kosong"
    assert out["sumber"], f"{case['id']}: sumber sitasi kosong"


def test_dataset_lengkap_18_soal():
    assert len(CASES) == 18
    assert {c["id"] for c in CASES} == {f"H{n:02d}" for n in range(1, 19)}


def test_semua_fungsi_dataset_terdaftar():
    assert {c["fungsi"] for c in CASES} <= set(calc.REGISTRY)
