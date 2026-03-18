from __future__ import annotations

import json
from pathlib import Path


def load_catalog(path: str) -> list[dict[str, object]]:
    data = Path(path).read_text(encoding="utf-8")
    items = json.loads(data)
    if not isinstance(items, list):
        raise ValueError("Catalog must be a JSON array")
    return sorted(items, key=lambda item: str(item.get("item_id", "")))
