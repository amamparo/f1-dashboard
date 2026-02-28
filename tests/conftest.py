import os
import shutil
import sqlite3

import pytest
from fastapi.testclient import TestClient

from esm_fullstack_challenge.db import DB
from esm_fullstack_challenge.db.init_auth import init_users_table
from esm_fullstack_challenge.dependencies.db import get_db
from esm_fullstack_challenge.main import app

TEST_DB = "test_data.db"


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Copy production DB and add users table for tests."""
    shutil.copy("data.db", TEST_DB)
    conn = sqlite3.connect(TEST_DB)
    init_users_table(conn)
    conn.close()
    yield
    os.remove(TEST_DB)


def _get_test_db():
    db = DB(TEST_DB)
    yield db


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Get valid auth headers by logging in as janedoe (admin)."""
    response = client.post("/auth/login", json={
        "username": "janedoe",
        "password": "password",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
