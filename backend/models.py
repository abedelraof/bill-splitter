from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    claude_api_key = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    friends = relationship("Friend", back_populates="user", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="user", cascade="all, delete-orphan")


class Friend(Base):
    __tablename__ = "friends"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="friends")
    assignments = relationship("BillItemAssignment", back_populates="friend")


class Bill(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_path = Column(String(500), nullable=True)
    vat_type = Column(String(10), nullable=True)       # 'percent' or 'fixed'
    vat_value = Column(Float, nullable=True)
    service_type = Column(String(10), nullable=True)
    service_value = Column(Float, nullable=True)
    discount_type = Column(String(10), nullable=True)
    discount_value = Column(Float, nullable=True)
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bills")
    items = relationship("BillItem", back_populates="bill", cascade="all, delete-orphan")


class BillItem(Base):
    __tablename__ = "bill_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    is_manual = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    bill = relationship("Bill", back_populates="items")
    assignments = relationship("BillItemAssignment", back_populates="item", cascade="all, delete-orphan")


class BillItemAssignment(Base):
    __tablename__ = "bill_item_assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    bill_item_id = Column(Integer, ForeignKey("bill_items.id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("friends.id"), nullable=False)
    __table_args__ = (UniqueConstraint("bill_item_id", "friend_id"),)

    item = relationship("BillItem", back_populates="assignments")
    friend = relationship("Friend", back_populates="assignments")
