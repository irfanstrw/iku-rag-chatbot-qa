"""
Schema kontrak keluaran kalkulator IKU.

Setiap fungsi di app/src/calculator/iku_formulas.py mengembalikan dict dengan
kunci wajib hasil/satuan/langkah/sumber (lihat docstring modulnya). 'catatan'
opsional. Validator ini dipakai oleh tests/contract.
"""

from jsonschema import Draft202012Validator

CALC_RESULT_SCHEMA = {
    "type": "object",
    "required": ["hasil", "satuan", "langkah", "sumber"],
    "properties": {
        # 'hasil' bisa number, string (predikat), atau dict (nilai per jenjang/jabatan)
        "hasil": {"type": ["number", "string", "object"]},
        "satuan": {"type": "string", "minLength": 1},
        "langkah": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 1},
        },
        "sumber": {"type": "string", "minLength": 1},
        "catatan": {"type": "string"},
    },
    "additionalProperties": False,
}

_validator = Draft202012Validator(CALC_RESULT_SCHEMA)


def iter_errors(result: dict):
    """Yield pesan error schema (string) untuk sebuah keluaran kalkulator."""
    for err in sorted(_validator.iter_errors(result), key=lambda e: e.path):
        loc = "/".join(str(p) for p in err.path) or "<root>"
        yield f"{loc}: {err.message}"
