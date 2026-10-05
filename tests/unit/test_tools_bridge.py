"""
Test jembatan tool-calling (app/src/generation/tools.py).

`jalankan_alat` adalah titik tempat LLM memanggil kalkulator. Kontraknya:
- alat asing → dict {"error": ...}, bukan exception
- argumen_json rusak → dict {"error": ...}
- argumen benar → diteruskan ke kalkulator, hasil dict berisi 'hasil'
- argumen_json boleh string JSON ganda (string berisi JSON)
"""

import json

import pytest

import tools

pytestmark = pytest.mark.unit


def _args(fungsi, argumen):
    """Bentuk argumen_teks seperti yang dikirim LLM: {'fungsi':..., 'argumen_json': {...}}."""
    return json.dumps({"fungsi": fungsi, "argumen_json": argumen})


def test_alat_asing_dikembalikan_sebagai_error_bukan_crash():
    out = tools.jalankan_alat("alat_hantu", "{}")
    assert "error" in out
    assert "hitung_iku" in out["error"]


def test_argumen_json_rusak_dikembalikan_sebagai_error():
    out = tools.jalankan_alat("hitung_iku", "{bukan json}")
    assert "error" in out


def test_fungsi_tak_dikenal_dikembalikan_sebagai_error():
    out = tools.jalankan_alat("hitung_iku", _args("fungsi_ngawur", {}))
    assert "error" in out


def test_panggilan_valid_diteruskan_ke_kalkulator():
    out = tools.jalankan_alat(
        "hitung_iku",
        _args("iku1_aee_prodi", {"jenjang": "S1", "lulus_tepat_waktu": 40, "total_mahasiswa": 200}),
    )
    assert "error" not in out
    assert out["hasil"]["aee_realisasi_pct"] == pytest.approx(20.0, abs=0.01)


def test_argumen_json_sebagai_string_ganda():
    # Beberapa penyedia mengirim argumen_json sebagai string JSON, bukan objek.
    out = tools.jalankan_alat(
        "hitung_iku",
        json.dumps({"fungsi": "rasio",
                    "argumen_json": json.dumps({"kode": "iku5", "pembilang": 30, "penyebut": 120})}),
    )
    assert out["hasil"] == pytest.approx(25.0, abs=0.01)


def test_tool_spec_enum_sinkron_dengan_registry():
    import iku_formulas as calc
    enum = tools.TOOL_HITUNG_IKU["function"]["parameters"]["properties"]["fungsi"]["enum"]
    assert set(enum) == set(calc.REGISTRY)


def test_panduan_argumen_menyebut_setiap_fungsi():
    panduan = tools.panduan_argumen()
    import iku_formulas as calc
    for nama in calc.REGISTRY:
        assert nama in panduan, f"fungsi {nama} tidak terdokumentasi di panduan_argumen()"
