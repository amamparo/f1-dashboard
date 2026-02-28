from fastapi import APIRouter, Depends, HTTPException, status

from esm_fullstack_challenge.db import DB
from esm_fullstack_challenge.dependencies import get_db
from esm_fullstack_challenge.auth import (
    authenticate_user, create_access_token, get_current_user,
    verify_password, hash_password,
    Token, LoginRequest, UserResponse, ChangePasswordRequest,
    UpdateProfileRequest,
)

auth_router = APIRouter()


@auth_router.post("/login", response_model=Token)
def login(form_data: LoginRequest, db: DB = Depends(get_db)):
    with db.get_connection() as conn:
        user = authenticate_user(conn, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "must_change_password": bool(user["must_change_password"]),
    }


@auth_router.get("/me", response_model=UserResponse)
def read_current_user(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@auth_router.put("/me/profile")
def update_profile(
    body: UpdateProfileRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: DB = Depends(get_db),
):
    updates = {}
    if body.username is not None:
        updates["username"] = body.username
    if body.full_name is not None:
        updates["full_name"] = body.full_name

    if not updates:
        return current_user

    with db.get_connection() as conn:
        if "username" in updates:
            existing = conn.execute(
                "SELECT id FROM users WHERE username = ? AND id != ? AND is_active = 1",
                (updates["username"], current_user.id),
            ).fetchone()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already taken",
                )
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(
            f"UPDATE users SET {set_clause} WHERE id = ?",
            (*updates.values(), current_user.id),
        )
        import sqlite3 as _sqlite3
        conn.row_factory = _sqlite3.Row
        row = conn.execute(
            "SELECT id, username, full_name, avatar, role,"
            " must_change_password, is_active FROM users WHERE id = ?",
            (current_user.id,),
        ).fetchone()
    return dict(row)


@auth_router.put("/me/password")
def change_password(
    body: ChangePasswordRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: DB = Depends(get_db),
):
    with db.get_connection() as conn:
        conn.row_factory = None
        row = conn.execute(
            "SELECT hashed_password FROM users WHERE id = ?",
            (current_user.id,),
        ).fetchone()
        if not row or not verify_password(body.current_password, row[0]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        conn.execute(
            "UPDATE users SET hashed_password = ?, must_change_password = 0 WHERE id = ?",
            (hash_password(body.new_password), current_user.id),
        )
    return {"detail": "Password updated successfully"}
