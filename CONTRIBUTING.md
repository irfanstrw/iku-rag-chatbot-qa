# Berkontribusi di repo QA

## Prinsip

- **Jangan menyalin kode aplikasi.** Impor dari submodule `app/`. Bila fungsi
  yang diuji berubah signature-nya, perbarui test, bukan menduplikasi logika.
- **Satu test = satu jaminan.** Beri nama test yang menjelaskan perilaku yang
  dijamin (`test_iku9_pos_pendapatan_asing_raise_valueerror`).
- **Deterministik.** Suite `unit`/`contract` tidak boleh butuh jaringan, GPU,
  atau API. Yang butuh itu masuk `integration` dan diberi
  `pytestmark = pytest.mark.integration`.

## Menambah test

1. Pilih suite: `tests/unit`, `tests/contract`, atau `tests/integration`.
2. Impor modul app apa adanya (`import iku_formulas`, `import tools`,
   `import prompt`) — `conftest.py` sudah menata `sys.path`.
3. Jalankan `pytest -m "unit or contract"` sebelum PR.

## Memutakhirkan submodule app/

Saat repo utama merilis versi baru yang ingin diuji:

```bash
cd app
git fetch origin
git checkout <tag-atau-commit>
cd ..
git add app
git commit -m "qa: bump submodule app ke <versi>"
```

CI akan menjalankan suite terhadap versi app yang di-pin itu.

## Memperbarui baseline regresi

`tests/data/golden_metrics.json` hanya dinaikkan (bukan diturunkan) dan lewat PR
terpisah yang melampirkan laporan `app/reports/evaluation/` sebagai bukti.

## Branch & PR

- Branch dari `develop`: `test/<area>` atau `fix/<area>`.
- PR ke `develop`; sertakan output `pytest` di deskripsi.
- Rilis: merge `develop` → `main`.
