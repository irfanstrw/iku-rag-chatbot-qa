"""
Test penyusun konteks & prompt (app/src/generation/prompt.py).

Jaminan utama: nomor halaman TIDAK pernah masuk ke konteks LLM (halaman
ditambahkan kode dari metadata, bukan dikarang LLM). Konteks diberi nomor
[1]..[n] dan label sumber yang benar.
"""

import pytest

import prompt

pytestmark = pytest.mark.unit


def _chunk(**kw):
    base = {"source_file": "Buku IKU Diktisaintek Berdampak V1", "content": "isi chunk"}
    base.update(kw)
    return base


def test_konteks_diberi_nomor_urut():
    ctx = prompt.build_context([_chunk(content="A"), _chunk(content="B")])
    assert "[1]" in ctx and "[2]" in ctx
    assert ctx.index("[1]") < ctx.index("[2]")


def test_konteks_tidak_mengandung_nomor_halaman():
    # Metadata punya info halaman, tapi build_context tak boleh membocorkannya.
    ctx = prompt.build_context([_chunk(iku_id="3", bagian="Formula")])
    assert "hlm" not in ctx.lower()
    assert "halaman" not in ctx.lower()


def test_label_sumber_buku_vs_ppt():
    buku = prompt.build_context([_chunk(source_file="Buku IKU ...")])
    ppt = prompt.build_context([_chunk(source_file="PPT IKU ...")])
    assert "Buku IKU" in buku
    assert "PPT IKU" in ppt


def test_label_lampiran_kepmen():
    ctx = prompt.build_context([_chunk(doc_part="lampiran")])
    assert "Lampiran" in ctx


def test_catatan_sumber_disertakan():
    ctx = prompt.build_context([_chunk(source_notes=[{"note": "tabel halaman ini cacat"}])])
    assert "CATATAN SUMBER" in ctx
    assert "tabel halaman ini cacat" in ctx


def test_build_user_message_berisi_konteks_dan_pertanyaan():
    msg = prompt.build_user_message("Apa itu IKU 3?", [_chunk()])
    assert "KONTEKS:" in msg
    assert "PERTANYAAN:" in msg
    assert "Apa itu IKU 3?" in msg


def test_system_prompt_mewajibkan_tool_calling_dan_larang_pengetahuan_luar():
    sp = prompt.SYSTEM_PROMPT.lower()
    assert "hitung_iku" in sp          # wajib pakai alat untuk hitungan
    assert "konteks" in sp             # hanya jawab dari konteks
