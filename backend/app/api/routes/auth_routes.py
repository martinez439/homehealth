from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.audit import write_audit_log
from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.db.database import get_db
from app.models.models import Caregiver, Client, User
from app.schemas.schemas import TokenResponse, UserLogin, UserRead, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_for(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token({"sub": str(user.id), "role": user.role}), user=user)


@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegister, request: Request, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    if payload.role not in {"admin", "caregiver", "family"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=payload.role,
        client_id=payload.client_id,
        caregiver_id=payload.caregiver_id,
    )
    db.add(user); db.flush()
    write_audit_log(db, action="user_registered", entity_type="user", entity_id=user.id, description=f"User registered with role {user.role}", user=user, request=request)
    db.commit(); db.refresh(user)
    return _token_for(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        write_audit_log(db, action="login_failure", entity_type="user", description=f"Failed login for {email}", request=request, actor_email=email)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    write_audit_log(db, action="login_success", entity_type="user", entity_id=user.id, description="User logged in", user=user, request=request)
    db.commit(); db.refresh(user)
    return _token_for(user)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"ok": True}


def seed_demo_users(db: Session):
    first_client = db.query(Client).order_by(Client.id.asc()).first()
    first_caregiver = db.query(Caregiver).order_by(Caregiver.id.asc()).first()
    demo_users = [
        ("admin@example.com", "Admin", "User", "admin", None, None),
        ("caregiver@example.com", "Caregiver", "User", "caregiver", None, first_caregiver.id if first_caregiver else None),
        ("family@example.com", "Family", "User", "family", first_client.id if first_client else None, None),
    ]
    for email, first, last, role, client_id, caregiver_id in demo_users:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.first_name = first; user.last_name = last; user.role = role; user.client_id = client_id; user.caregiver_id = caregiver_id; user.is_active = True
            continue
        db.add(User(email=email, password_hash=hash_password("password123"), first_name=first, last_name=last, role=role, client_id=client_id, caregiver_id=caregiver_id, is_active=True))


@router.post("/dev-seed-users")
def dev_seed_users(request: Request, db: Session = Depends(get_db)):
    seed_demo_users(db)
    write_audit_log(db, action="dev_seed_users", entity_type="user", description="Seeded local demo users", request=request)
    db.commit()
    return {"ok": True, "users": ["admin@example.com", "caregiver@example.com", "family@example.com"]}
