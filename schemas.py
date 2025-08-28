from pydantic import BaseModel, Field
from typing import Optional

class VerificationRequest(BaseModel):
    full_name: str = Field(..., examples=["Jane Doe"])
    purpose: str = Field(..., examples=["Vendor meeting"])
    floor: int = Field(..., ge=1, le=80, examples=[15])
    expected_minutes: int = Field(..., ge=5, le=720, examples=[60])

class VerificationResult(BaseModel):
    approved: bool
    reason: Optional[str] = None
    visit_id: str