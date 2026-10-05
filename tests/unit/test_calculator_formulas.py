"""
Unit test fungsi registry kalkulator (app/src/calculator/iku_formulas.py).

Menguji tiap fungsi secara langsung dengan kasus representatif + nilai yang
dihitung tangan dari rumus di Buku IKU. Tanpa GPU/API.
"""

import pytest

import iku_formulas as calc

pytestmark = pytest.mark.unit

TOL = 0.01


def approx(a, b):
    return abs(a - b) <= TOL


def test_registry_berisi_sepuluh_fungsi():
    assert set(calc.REGISTRY) == {
        "iku1_aee_prodi", "iku1_aee_pt", "iku2", "iku2_responden_minimum",
        "iku3", "iku6", "rasio", "iku9", "iku11b_predikat",
        "iku12_penghasilan_minimum",
    }


def test_iku1_aee_prodi_s1():
    out = calc.iku1_aee_prodi(jenjang="S1", lulus_tepat_waktu=40, total_mahasiswa=200)
    assert approx(out["hasil"]["aee_realisasi_pct"], 20.0)
    assert approx(out["hasil"]["tingkat_pencapaian_pct"], 80.0)


def test_iku1_aee_prodi_pengurang_pindah_do_tidak_dihitung():
    # Ketentuan c: pindah & DO dikeluarkan dari basis.
    out = calc.iku1_aee_prodi(jenjang="S1", lulus_tepat_waktu=45, total_mahasiswa=250,
                              pindah=10, drop_out=15)
    assert approx(out["hasil"]["aee_realisasi_pct"], 20.0)  # 45 / (250-25) = 20%


def test_iku1_aee_pt_rata_rata_pencapaian():
    out = calc.iku1_aee_pt({"D3": 30, "S1": 22.5, "S2": 40})
    assert approx(out["hasil"], 86.97)


def test_iku2_bobot_sederhana():
    out = calc.iku2(total_responden=400, kategori={"bekerja_<6bln_>1.2ump": 280, "belum": 120})
    assert approx(out["hasil"], 70.0)


def test_iku2_responden_minimum_slovin_dibulatkan_ke_atas():
    out = calc.iku2_responden_minimum(jumlah_lulusan=2000)
    assert out["hasil"] == 972
    assert out["satuan"] == "responden"


def test_iku3_kegiatan_dan_prestasi():
    out = calc.iku3(
        total_mahasiswa=1000,
        kegiatan=[{"jumlah": 100, "sks": 20}, {"jumlah": 150, "sks": 8}, {"jumlah": 50, "sks": 4}],
        prestasi=[{"jumlah": 5, "tingkat": "nasional", "peringkat": "juara1"},
                  {"jumlah": 10, "tingkat": "internasional", "peringkat": "finalis"}],
    )
    assert approx(out["hasil"], 21.5)
    assert out["catatan"]  # catatan ambiguitas 10 SKS harus ada


def test_iku6_dengan_bonus_kolaborasi():
    out = calc.iku6(total_publikasi=20, publikasi={"q1": 6, "prosiding": 10}, kolaborasi={"q1": 4})
    assert approx(out["hasil"], 67.5)
    assert "catatan" in out  # bonus kolaborasi memicu catatan tafsir


def test_rasio_iku5():
    out = calc.rasio("iku5", pembilang=30, penyebut=120)
    assert approx(out["hasil"], 25.0)


def test_iku9_hanya_pos_diakui_dihitung():
    out = calc.iku9(total_pendapatan=500,
                    rincian={"ukt": 300, "boptn": 80, "hibah_riset": 50,
                             "konsultasi": 40, "unit_bisnis": 20, "hasil_dana_abadi": 10})
    # diakui = 50+40+20+10 = 120 → 120/500 = 24%
    assert approx(out["hasil"], 24.0)


def test_iku11b_predikat_batas():
    assert calc.iku11b_predikat(90)["hasil"].startswith("AA")
    assert calc.iku11b_predikat(82)["hasil"].startswith("A")
    assert calc.iku11b_predikat(59)["hasil"].startswith("CC")


def test_iku12_penghasilan_minimum_kelipatan_ump():
    out = calc.iku12_penghasilan_minimum(ump=3_000_000, jabatan=["lektor", "profesor"])
    assert out["hasil"] == {"lektor": 9_000_000, "profesor": 18_000_000}


@pytest.mark.parametrize("sks,bobot", [(4, 0.4), (5, 0.4), (6, 0.6), (9, 0.6), (10, 1.0), (24, 1.0)])
def test_bobot_sks_batas(sks, bobot):
    assert calc.bobot_sks(sks) == bobot
