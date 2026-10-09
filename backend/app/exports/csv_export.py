from __future__ import annotations

import csv
from io import StringIO
from typing import Iterable


def build_csv(rows: Iterable[dict], columns: list[tuple[str, str]]) -> bytes:
    """CSV UTF-8 com BOM e separador ';', amigável ao Excel pt-BR."""
    buf = StringIO(newline="")
    writer = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow([label for _, label in columns])
    for row in rows:
        out = []
        for key, _ in columns:
            value = row.get(key)
            if value is None:
                value = ""
            out.append(value)
        writer.writerow(out)
    return ("\ufeff" + buf.getvalue()).encode("utf-8")
