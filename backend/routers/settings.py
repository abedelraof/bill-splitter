from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_current_user
from backend.database import get_db

router = APIRouter()


@router.get("/", response_model=schemas.SettingsResponse)
def get_settings(current_user: models.User = Depends(get_current_user)):
    key = current_user.claude_api_key
    preview = None
    if key:
        preview = key[:8] + "..." + key[-4:] if len(key) > 12 else key[:4] + "..."
    return {"has_claude_key": bool(key), "claude_key_preview": preview}


@router.put("/claude-key")
def update_claude_key(payload: schemas.ClaudeKeyUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    key = payload.claude_api_key.strip()
    if not key.startswith("sk-"):
        raise HTTPException(status_code=400, detail="API key must start with 'sk-'")
    current_user.claude_api_key = key
    db.commit()
    return {"ok": True}
