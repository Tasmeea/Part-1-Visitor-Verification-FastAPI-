from datetime import datetime
from pathlib import Path
import json
import uuid

SDB_ROOT = Path("/data/sdb")  # date-partitioned “SDB” (simple data bucket)

def ensure_daily_folder() -> Path:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    folder = SDB_ROOT / today
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def save_visit_record(meta: dict, image_bytes: bytes, image_ext: str = "jpg") -> dict:
    folder = ensure_daily_folder()
    visit_id = str(uuid.uuid4())
    img_path = folder / f"{visit_id}.{image_ext}"
    with open(img_path, "wb") as f:
        f.write(image_bytes)

    meta_out = {**meta, "visit_id": visit_id, "image_path": str(img_path)}
    with open(folder / f"{visit_id}.json", "w") as f:
        json.dump(meta_out, f, indent=2)
    return meta_out