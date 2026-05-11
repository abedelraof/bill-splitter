from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


# Auth
class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MeResponse(BaseModel):
    id: int
    email: str
    has_claude_key: bool


# Friends
class FriendCreate(BaseModel):
    name: str

class FriendUpdate(BaseModel):
    name: str

class FriendOut(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}


# Bills
class ExtraInfo(BaseModel):
    type: str   # 'percent' or 'fixed'
    value: float

class ExtrasPayload(BaseModel):
    vat: Optional[ExtraInfo] = None
    service_charge: Optional[ExtraInfo] = None
    discount: Optional[ExtraInfo] = None

class ParsedItem(BaseModel):
    description: str
    amount: float

class ParseResponse(BaseModel):
    image_path: Optional[str]
    items: List[ParsedItem]
    extras: ExtrasPayload

class BillItemCreate(BaseModel):
    description: str
    amount: float
    is_manual: bool = False
    friend_ids: List[int] = []

class BillCreate(BaseModel):
    image_path: Optional[str] = None
    items: List[BillItemCreate]
    extras: ExtrasPayload

class BillCreateResponse(BaseModel):
    bill_id: int

class BillListItem(BaseModel):
    id: int
    created_at: datetime
    status: str
    model_config = {"from_attributes": True}


# Summary
class FriendSummary(BaseModel):
    friend_id: int
    name: str
    items_subtotal: float
    extras_share: float
    total: float

class BillSummaryResponse(BaseModel):
    bill_id: int
    subtotal: float
    vat_amount: float
    service_amount: float
    discount_amount: float
    grand_total: float
    friends: List[FriendSummary]
    unassigned_subtotal: float


# Settings
class SettingsResponse(BaseModel):
    has_claude_key: bool
    claude_key_preview: Optional[str]

class ClaudeKeyUpdate(BaseModel):
    claude_api_key: str
