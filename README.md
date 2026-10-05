# QA — Chatbot RAG IKU Diktisaintek Berdampak

Repositori **Quality Assurance** untuk [`iku-rag-chatbot`](https://github.com/budisatrio32/iku-rag-chatbot).
Berisi *test automation* (pytest), *contract tests*, *regression gate* evaluasi
retrieval/kalkulator, dan pipeline CI yang menjalankan semuanya di setiap push/PR.

Repo ini **tidak menggandakan kode aplikasi**. Kode yang diuji diambil dari repo
utama sebagai **git submodule** di `app/`, persis seperti lingkungan nyata: QA
menguji artefak yang sama yang dirilis, bukan salinannya.

```text
iku-rag-chatbot-qa/
├── app/                        # git submodule → repo utama (kode yang diuji)
├── tests/
│   ├── unit/                   # tanpa GPU/API — jalan di CI
│   │   ├── test_calculator_formulas.py      # 10 fungsi registry kalkulator
│   │   ├── test_calculator_dataset.py       # 18 soal hitungan dari test set
│   │   ├── test_calculator_edge_cases.py    # pembagian nol, pos tak dikenal, dsb.
│   │   ├── test_tools_bridge.py             # jembatan tool-calling LLM → kalkulator
│   │   └── test_prompt_builder.py           # penyusunan konteks bernomor + sitasi
│   ├── contract/               # kontrak keluaran kalkulator (schema setiap dict)
│   │   └── test_calculator_contract.py
│   ├── integration/            # butuh GPU/model/API — ditandai, di-skip di CI default
│   │   ├── test_retrieval_regression.py     # gate metrik Hit@k / MRR
│   │   └── test_chat_smoke.py               # smoke test chatbot end-to-end
│   └── data/
│       └── golden_metrics.json              # ambang regresi (baseline yang disetujui)
├── qa_utils/
│   ├── __init__.py
│   ├── paths.py                # resolusi path app/ submodule, aman dari CWD
│   └── schema.py               # validator schema keluaran kalkulator
├── .github/workflows/qa.yml    # CI: lint + unit + contract (ubuntu, py 3.13)
├── conftest.py                 # bootstrap sys.path ke submodule
├── pytest.ini                  # marker: unit / contract / integration
├── requirements-qa.txt         # dependency pengujian (tanpa torch/GPU)
├── Makefile                    # make unit / make contract / make all
├── CONTRIBUTING.md
└── README.md
```

## Prasyarat

- Python 3.13 (sama dengan repo utama)
- Git (submodule)
- **Tidak butuh GPU/API** untuk suite `unit` + `contract` — itu yang dijalankan CI.

## Setup

```powershell
# 1. Clone BESERTA submodule (kode aplikasi masuk ke app/)
git clone --recurse-submodules https://github.com/<username>/iku-rag-chatbot-qa.git
cd iku-rag-chatbot-qa

# Jika sudah terlanjur clone tanpa --recurse-submodules:
git submodule update --init --recursive

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate

# 3. Dependency pengujian (ringan, tanpa torch)
pip install -r requirements-qa.txt
```

## Menjalankan test

```powershell
pytest                       # default: unit + contract (cepat, tanpa GPU/API)
pytest -m unit               # hanya unit test
pytest -m contract           # hanya contract test
pytest -m integration        # butuh GPU/model/API (lihat di bawah)
pytest --cov=app/src/calculator --cov-report=term-missing   # dengan coverage
```

Atau lewat Makefile:

```bash
make unit        # pytest -m "unit"
make contract    # pytest -m "contract"
make all         # unit + contract
make integration # butuh lingkungan lengkap
```

## Suite integration (butuh lingkungan lengkap)

Suite `integration` memanggil retriever bge-m3 dan/atau LLM, jadi **di-skip
otomatis** kecuali lingkungannya tersedia. Untuk menjalankannya:

```powershell
# a. Submodule app/ harus sudah di-setup penuh (venv app, vector DB dibangun)
#    Ikuti README repo utama bagian "Setup" sampai build_chroma.py --reset.
# b. Set path ke venv aplikasi yang punya torch + chromadb + bge-m3:
$env:IKU_APP_PYTHON = "C:\path\ke\iku-rag-chatbot\.venv\Scripts\python.exe"
# c. Untuk smoke test chatbot, isi juga API key LLM di app/.env
pytest -m integration
```

- `test_retrieval_regression.py` menjalankan `eval_retrieval.py` di app dan
  membandingkan Hit@1/Hit@5/MRR terhadap `tests/data/golden_metrics.json`. Test
  **gagal bila metrik turun** di bawah ambang — ini *regression gate*.
- `test_chat_smoke.py` menanyakan satu pertanyaan definisi dan satu soal
  hitungan ke `chat_cli.py`, memastikan jawaban mengandung rujukan `[n]` dan
  (untuk soal hitungan) hasil kalkulator yang benar.

## Apa yang diuji (ringkas)

| Suite | File | Yang dijamin |
|---|---|---|
| unit | `test_calculator_formulas.py` | Setiap fungsi registry menghitung benar untuk kasus representatif |
| unit | `test_calculator_dataset.py` | 18 soal hitungan test set (H01–H18) sesuai kunci jawaban |
| unit | `test_calculator_edge_cases.py` | Error ditangani: fungsi tak dikenal, pos pendapatan asing, batas SKS |
| unit | `test_tools_bridge.py` | `jalankan_alat` mengurai argumen JSON, meneruskan ke kalkulator, menolak alat asing tanpa crash |
| unit | `test_prompt_builder.py` | Konteks bernomor `[1]..[n]`, label sumber Buku/PPT/Lampiran, CATATAN SUMBER |
| contract | `test_calculator_contract.py` | Setiap keluaran kalkulator punya `hasil/satuan/langkah/sumber`, tipe benar, langkah tak kosong |
| integration | `test_retrieval_regression.py` | Hit@1 ≥ 75,9%, MRR@5 ≥ 0,82 (gate regresi) |
| integration | `test_chat_smoke.py` | Chatbot end-to-end: sitasi + hasil kalkulator |

## CI

`.github/workflows/qa.yml` berjalan di setiap push/PR ke `main`/`develop`:

1. Checkout **dengan submodule** (`submodules: recursive`).
2. Pasang `requirements-qa.txt` (ringan — tanpa torch).
3. `python -m compileall` kode app yang diuji (cek sintaks).
4. `pytest -m "unit or contract"` dengan coverage pada kalkulator.

Suite `integration` **tidak** dijalankan di CI (butuh GPU + API key); jalankan
manual atau di *self-hosted runner* ber-GPU.

## Memperbarui baseline regresi

Bila perubahan kode menaikkan metrik secara sah, perbarui
`tests/data/golden_metrics.json` lewat PR terpisah dengan menyertakan laporan
`reports/evaluation/` dari repo utama sebagai bukti. Jangan menurunkan ambang
hanya agar test lulus.
