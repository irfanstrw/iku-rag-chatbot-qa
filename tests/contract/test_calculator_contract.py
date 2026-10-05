"""
Contract test: SETIAP keluaran kalkulator harus memenuhi schema
hasil/satuan/langkah/sumber (qa_utils/schema.py). Dijalankan atas 18 soal
dataset + beberapa panggilan tambahan untuk menutup fungsi yang tak ada di dataset.
"""

import json

import pytest

import iku_formulas as calc
from qa_utils.schema import iter_errors
from qa_utils.paths import CALC_DATASET

pytestmark = pytest.mark.contract

_dataset_cases = (
    json.loads(CALC_DATASET.read_text(encoding="utf-8"))["cases"]
    if CALC_DATASET.is_file() else []
)

# Panggilan tambahan untuk fungsi/cabang yang tidak ada di dataset H01-H18.
_extra = [
    ("E-iku9", "iku9", {"total_pendapatan": 500,
                        "rincian": {"ukt": 300, "hibah_riset": 200}}),
    ("E-iku6-kolab", "iku6", {"total_publikasi": 20,
                              "publikasi": {"q1": 6}, "kolaborasi": {"q1": 4}}),
]


def _all_cases():
    for c in _dataset_cases:
        yield c["id"], c["fungsi"], c["argumen"]
    yield from _extra


ALL = list(_all_cases())


@pytest.mark.parametrize("cid,fungsi,argumen", ALL, ids=[c[0] for c in ALL])
def test_keluaran_memenuhi_schema(cid, fungsi, argumen):
    out = calc.hitung(fungsi, **argumen)
    errors = list(iter_errors(out))
    assert not errors, f"{cid} ({fungsi}) melanggar schema: {errors}"


@pytest.mark.parametrize("cid,fungsi,argumen", ALL, ids=[c[0] for c in ALL])
def test_sumber_menyebut_buku_dan_halaman(cid, fungsi, argumen):
    out = calc.hitung(fungsi, **argumen)
    assert "Buku IKU" in out["sumber"], f"{cid}: sumber tidak merujuk Buku IKU"
    assert "hlm" in out["sumber"].lower(), f"{cid}: sumber tidak menyebut halaman"
