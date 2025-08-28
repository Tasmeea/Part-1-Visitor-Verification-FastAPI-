from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from .schemas import VerificationRequest, VerificationResult
from .storage import save_visit_record
import os, requests

router = APIRouter()
ROBOT_NOTIFY_URL = os.getenv("ROBOT_NOTIFY_URL", "http://robots:8002/api/visitor")
ROBOT_TOKEN = os.getenv("ROBOT_TOKEN", "changeme")

def simple_policy(purpose: str, floor: int, minutes: int) -> tuple[bool, str | None]:
    # Replace with real checks: face-match, blacklist, booking lookup, etc.
    if minutes > 240:
        return False, "Visit duration exceeds max policy (240 min)."
    if floor < 1 or floor > 40:
        return False, "Requested floor out of allowed range for visitors."
    return True, None

@router.post("/api/verify", response_model=VerificationResult)
async def verify(
    full_name: str = Form(...),
    purpose: str = Form(...),
    floor: int = Form(...),
    expected_minutes: int = Form(...),
    face: UploadFile = File(...)
):
    # Validate & approve/deny
    approved, reason = simple_policy(purpose, int(floor), int(expected_minutes))
    # Persist to SDB
    meta = {
        "full_name": full_name,
        "purpose": purpose,
        "floor": int(floor),
        "expected_minutes": int(expected_minutes),
        "approved": approved,
    }
    image_ext = (face.filename.split(".")[-1] or "jpg").lower()
    record = save_visit_record(meta, await face.read(), image_ext)

    # Notify robots if approved
    if approved:
        payload = {
            "visit_id": record["visit_id"],
            "full_name": full_name,
            "allowed_floor": int(floor),
            "expires_in_minutes": int(expected_minutes),
            "image_path": record["image_path"],  # for traceability; robots usually won’t fetch this
        }
        try:
            headers = {"Authorization": f"Bearer {ROBOT_TOKEN}"}
            requests.post(ROBOT_NOTIFY_URL, json=payload, timeout=5, headers=headers)
        except Exception as e:
            # Non-fatal: keep verification success even if notify fails; Jenkins/robots can retry.
            print(f"[WARN] Robot notify failed: {e}")

    return VerificationResult(
        approved=approved,
        reason=reason,
        visit_id=record["visit_id"]
    )