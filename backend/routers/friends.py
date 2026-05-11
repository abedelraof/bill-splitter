from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_current_user
from backend.database import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.FriendOut])
def list_friends(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Friend).filter(models.Friend.user_id == current_user.id).order_by(models.Friend.id).all()


@router.post("/", response_model=schemas.FriendOut, status_code=status.HTTP_201_CREATED)
def create_friend(payload: schemas.FriendCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be blank")
    friend = models.Friend(user_id=current_user.id, name=payload.name.strip())
    db.add(friend)
    db.commit()
    db.refresh(friend)
    return friend


@router.put("/{friend_id}", response_model=schemas.FriendOut)
def update_friend(friend_id: int, payload: schemas.FriendUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    friend = db.query(models.Friend).filter(models.Friend.id == friend_id, models.Friend.user_id == current_user.id).first()
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be blank")
    friend.name = payload.name.strip()
    db.commit()
    db.refresh(friend)
    return friend


@router.delete("/{friend_id}")
def delete_friend(friend_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    friend = db.query(models.Friend).filter(models.Friend.id == friend_id, models.Friend.user_id == current_user.id).first()
    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")
    db.delete(friend)
    db.commit()
    return {"ok": True}
