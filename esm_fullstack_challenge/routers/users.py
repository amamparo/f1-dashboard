import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, Response, status

from esm_fullstack_challenge.db import DB
from esm_fullstack_challenge.db.init_auth import AVATAR_BASE_URL
from esm_fullstack_challenge.dependencies import get_db, CommonQueryParams
from esm_fullstack_challenge.auth import (
    hash_password, get_user_by_id, require_admin,
    CreateUserRequest, UpdateUserRequest, UserResponse,
)

users_router = APIRouter()

USER_COLUMNS = "id, username, full_name, avatar, role, must_change_password, is_active"


def _generate_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _row_to_response(row: dict) -> dict:
    return {
        "id": row["id"],
        "username": row["username"],
        "full_name": row["full_name"],
        "avatar": row["avatar"],
        "role": row["role"],
        "must_change_password": bool(row["must_change_password"]),
        "is_active": bool(row["is_active"]),
    }


@users_router.get("")
def list_users(
    response: Response,
    cqp: CommonQueryParams = Depends(CommonQueryParams),
    db: DB = Depends(get_db),
):
    with db.get_connection() as conn:
        import sqlite3 as _sqlite3
        conn.row_factory = _sqlite3.Row

        # Build query with sorting and pagination
        order_clause = ""
        if cqp.order_by:
            col, direction = cqp.order_by[0]
            order_clause = f" ORDER BY {col} {direction}"

        limit_clause = ""
        if cqp.limit is not None:
            limit_clause = f" LIMIT {cqp.limit} OFFSET {cqp.offset}"

        rows = conn.execute(
            f"SELECT {USER_COLUMNS} FROM users WHERE is_active = 1{order_clause}{limit_clause}"
        ).fetchall()

        count = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1").fetchone()[0]

    data = [_row_to_response(dict(r)) for r in rows]

    response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
    response.headers['Content-Range'] = (
        f'users {cqp.offset}-{cqp.offset + len(data) - 1}/{count}'
    )
    return data


@users_router.get("/{user_id}")
def get_user(user_id: int, db: DB = Depends(get_db)):
    with db.get_connection() as conn:
        user = get_user_by_id(conn, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _row_to_response(user)


@users_router.post("", status_code=status.HTTP_201_CREATED)
def create_user(
    body: CreateUserRequest,
    admin: UserResponse = Depends(require_admin),
    db: DB = Depends(get_db),
):
    initial_password = _generate_password()
    avatar = f"{AVATAR_BASE_URL}?seed={body.username}"

    with db.get_connection() as conn:
        existing = conn.execute(
            "SELECT id, is_active FROM users WHERE username = ?", (body.username,)
        ).fetchone()
        if existing and existing[1]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )

        role = body.role if body.role in ("admin", "member") else "member"
        if existing:
            # Reactivate previously deleted user with fresh data
            conn.execute(
                "UPDATE users SET full_name = ?, hashed_password = ?, avatar = ?,"
                " role = ?, must_change_password = 1, is_active = 1 WHERE id = ?",
                (body.full_name, hash_password(initial_password), avatar, role, existing[0]),
            )
            user = get_user_by_id(conn, existing[0])
        else:
            conn.execute(
                "INSERT INTO users (username, full_name, hashed_password, avatar, role,"
                " must_change_password) VALUES (?, ?, ?, ?, ?, 1)",
                (body.username, body.full_name, hash_password(initial_password), avatar, role),
            )
            user = get_user_by_id(conn, conn.execute("SELECT last_insert_rowid()").fetchone()[0])

    result = _row_to_response(user)
    result["initial_password"] = initial_password
    return result


@users_router.put("/{user_id}")
def update_user(
    user_id: int,
    body: UpdateUserRequest,
    admin: UserResponse = Depends(require_admin),
    db: DB = Depends(get_db),
):
    with db.get_connection() as conn:
        user = get_user_by_id(conn, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        updates = {}
        if body.username is not None:
            updates["username"] = body.username
        if body.full_name is not None:
            updates["full_name"] = body.full_name
        if body.role in ("admin", "member"):
            updates["role"] = body.role

        if updates:
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            conn.execute(
                f"UPDATE users SET {set_clause} WHERE id = ?",
                (*updates.values(), user_id),
            )
            user = get_user_by_id(conn, user_id)

    return _row_to_response(user)


@users_router.delete("/{user_id}")
def delete_user(
    user_id: int,
    admin: UserResponse = Depends(require_admin),
    db: DB = Depends(get_db),
):
    with db.get_connection() as conn:
        user = get_user_by_id(conn, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        conn.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_id,))
    return {"id": user_id}
