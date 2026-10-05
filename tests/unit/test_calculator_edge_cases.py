"""
Edge case & penanganan error kalkulator — memastikan input buruk ditangani
sesuai kontrak, bukan menghasilkan diam-diam salah.
"""

import pytest

import iku_formulas as calc

pytestmark = pytest.mark.unit


def test_hitung_fungsi_tak_dikenal_raise_keyerror():
    with pytest.raises(KeyError):
        calc.hitung("fungsi_yang_tidak_ada")


def test_iku9_pos_pendapatan_asing_raise_valueerror():
    # Pos yang tidak ada di daftar diakui/tidak-diakui harus ditolak, bukan diabaikan.
    with pytest.raises(ValueError):
        calc.iku9(total_pendapatan=100, rincian={"pos_ngawur": 50})


def test_iku1_jenjang_tak_dikenal_raise_keyerror():
    with pytest.raises(KeyError):
        calc.iku1_aee_prodi(jenjang="X9", lulus_tepat_waktu=10, total_mahasiswa=100)


def test_iku3_prestasi_kombinasi_tak_dikenal_raise_keyerror():
    with pytest.raises(KeyError):
        calc.iku3(total_mahasiswa=100,
                  prestasi=[{"jumlah": 1, "tingkat": "galaksi", "peringkat": "juara1"}])


def test_iku2_responden_minimum_galat_kustom():
    # Galat lebih besar → sampel lebih kecil.
    kecil = calc.iku2_responden_minimum(jumlah_lulusan=2000, galat=0.05)["hasil"]
    besar = calc.iku2_responden_minimum(jumlah_lulusan=2000, galat=0.023)["hasil"]
    assert kecil < besar


def test_fmt_gaya_indonesia():
    # 1.234,5 — titik ribuan, koma desimal.
    assert calc._fmt(1234.5) == "1.234,5"
    assert calc._fmt(1000000) == "1.000.000"
