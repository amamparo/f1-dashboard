from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    must_change_password: bool


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    avatar: str
    role: str
    must_change_password: bool
    is_active: bool


class CreateUserRequest(BaseModel):
    username: str
    full_name: str
    role: Optional[str] = None


class UpdateUserRequest(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None


class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
