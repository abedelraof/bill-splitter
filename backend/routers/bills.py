import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_current_user
from backend.config import UPLOAD_DIR
from backend.database import get_db
from backend.services import claude_service, bill_calculator

router = APIRouter()


@router.post("/parse", response_model=schemas.ParseResponse)
async def parse_bill(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.claude_api_key:
        raise HTTPException(status_code=402, detail="No Claude API key set. Go to Settings to add your key.")

    content = await file.read()
    ext = (file.filename or "image.jpg").rsplit(".", 1)[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
        ext = "jpg"

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}.{ext}"
    image_path = os.path.join(UPLOAD_DIR, filename)
    with open(image_path, "wb") as f:
        f.write(content)

    try:
        result = claude_service.parse_bill_image(content, ext, current_user.claude_api_key)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"AI parsing failed: {str(e)}")

    return {
        "image_path": image_path,
        "items": result["items"],
        "extras": result["extras"],
    }


@router.post("/", response_model=schemas.BillCreateResponse, status_code=status.HTTP_201_CREATED)
def create_bill(
    payload: schemas.BillCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    extras = payload.extras

    bill = models.Bill(
        user_id=current_user.id,
        image_path=payload.image_path,
        vat_type=extras.vat.type if extras.vat else None,
        vat_value=extras.vat.value if extras.vat else None,
        service_type=extras.service_charge.type if extras.service_charge else None,
        service_value=extras.service_charge.value if extras.service_charge else None,
        discount_type=extras.discount.type if extras.discount else None,
        discount_value=extras.discount.value if extras.discount else None,
        status="finalized",
    )
    db.add(bill)
    db.flush()

    for idx, item_data in enumerate(payload.items):
        item = models.BillItem(
            bill_id=bill.id,
            description=item_data.description,
            amount=item_data.amount,
            is_manual=item_data.is_manual,
            sort_order=idx,
        )
        db.add(item)
        db.flush()

        for friend_id in item_data.friend_ids:
            friend = db.query(models.Friend).filter(
                models.Friend.id == friend_id,
                models.Friend.user_id == current_user.id,
            ).first()
            if friend:
                assignment = models.BillItemAssignment(bill_item_id=item.id, friend_id=friend_id)
                db.add(assignment)

    db.commit()
    return {"bill_id": bill.id}


@router.get("/{bill_id}/summary", response_model=schemas.BillSummaryResponse)
def get_summary(
    bill_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id, models.Bill.user_id == current_user.id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    friends = db.query(models.Friend).filter(models.Friend.user_id == current_user.id).all()
    return bill_calculator.calculate_summary(bill, friends)


@router.get("/", response_model=List[schemas.BillListItem])
def list_bills(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(models.Bill)
        .filter(models.Bill.user_id == current_user.id)
        .order_by(models.Bill.created_at.desc())
        .all()
    )


@router.delete("/{bill_id}")
def delete_bill(bill_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id, models.Bill.user_id == current_user.id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    db.delete(bill)
    db.commit()
    return {"ok": True}
