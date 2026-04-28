from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import models
from app.deps import get_current_user, get_db
from app.schemas import AuthOrganizationResponse, AuthTokenResponse, AuthUserResponse, UserLogin, UserRegister, UserResponse
from app.services.auth import create_access_token, hash_password, normalize_email, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_user_response(user: models.User) -> AuthUserResponse:
    organizations = [
        AuthOrganizationResponse(
            id=membership.organization.id,
            name=membership.organization.name,
            created_at=membership.organization.created_at,
            role=membership.role,
        )
        for membership in sorted(user.memberships, key=lambda item: item.organization.name.lower())
    ]
    return AuthUserResponse(user=UserResponse.model_validate(user), organizations=organizations)


def _token_response(user: models.User) -> AuthTokenResponse:
    response = _auth_user_response(user)
    return AuthTokenResponse(
        access_token=create_access_token(user.id),
        user=response.user,
        organizations=response.organizations,
    )


def _load_user_with_memberships(db: Session, email: str) -> models.User | None:
    return db.scalar(
        select(models.User)
        .where(models.User.email == email)
        .options(selectinload(models.User.memberships).selectinload(models.OrganizationMembership.organization))
    )


@router.post("/register", response_model=AuthTokenResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)) -> AuthTokenResponse:
    email = normalize_email(payload.email)
    existing = db.scalar(select(models.User).where(models.User.email == email))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = models.User(
        email=email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip() if payload.full_name else None,
    )
    db.add(user)
    db.flush()

    if payload.organization_name:
        organization = models.Organization(name=payload.organization_name)
        db.add(organization)
        db.flush()
        db.add(
            models.OrganizationMembership(
                user_id=user.id,
                organization_id=organization.id,
                role="owner",
            )
        )

    db.commit()
    loaded_user = _load_user_with_memberships(db, email)
    if loaded_user is None:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="User registration failed")
    return _token_response(loaded_user)


@router.post("/login", response_model=AuthTokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> AuthTokenResponse:
    email = normalize_email(payload.email)
    user = _load_user_with_memberships(db, email)
    if user is None or user.disabled_at is not None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return _token_response(user)


@router.get("/me", response_model=AuthUserResponse)
def me(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)) -> AuthUserResponse:
    user = db.scalar(
        select(models.User)
        .where(models.User.id == current_user.id)
        .options(selectinload(models.User.memberships).selectinload(models.OrganizationMembership.organization))
    )
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return _auth_user_response(user)
