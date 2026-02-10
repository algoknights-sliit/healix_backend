
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserBase

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_nic(db: Session, nic: str):
    return db.query(User).filter(User.nic == nic).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    # In a real app, hash the password here!
    # For now, we store it as is (or pretend to hash it)
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = User(
        email=user.email, 
        full_name=user.full_name, 
        nic=user.nic,
        hashed_password=fake_hashed_password,
        is_active=user.is_active,
        user_type=user.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_in: UserBase):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user