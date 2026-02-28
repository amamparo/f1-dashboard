"""Tests for JWT authentication and user management."""


def test_login_success(client):
    response = client.post("/auth/login", json={
        "username": "janedoe",
        "password": "password",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["must_change_password"] is False


def test_login_wrong_password(client):
    response = client.post("/auth/login", json={
        "username": "janedoe",
        "password": "wrong",
    })
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post("/auth/login", json={
        "username": "nobody",
        "password": "password",
    })
    assert response.status_code == 401


def test_get_current_user(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "janedoe"
    assert data["full_name"] == "Jane Doe"
    assert data["role"] == "admin"
    assert "hashed_password" not in data
    assert "avatar" in data


def test_protected_route_without_token(client):
    response = client.get("/drivers")
    assert response.status_code == 401


def test_protected_route_with_token(client, auth_headers):
    response = client.get("/drivers", headers=auth_headers)
    assert response.status_code == 200


def test_protected_route_with_invalid_token(client):
    response = client.get("/drivers", headers={
        "Authorization": "Bearer invalid-token"
    })
    assert response.status_code == 401


def test_public_routes_remain_accessible(client):
    assert client.get("/").status_code == 200
    assert client.get("/ping").status_code == 200


def test_change_password(client, auth_headers):
    response = client.put("/auth/me/password", headers=auth_headers, json={
        "current_password": "password",
        "new_password": "newpassword123",
    })
    assert response.status_code == 200

    # Login with new password
    response = client.post("/auth/login", json={
        "username": "janedoe",
        "password": "newpassword123",
    })
    assert response.status_code == 200

    # Restore original password
    token = response.json()["access_token"]
    client.put(
        "/auth/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "newpassword123", "new_password": "password"},
    )


def test_change_password_wrong_current(client, auth_headers):
    response = client.put("/auth/me/password", headers=auth_headers, json={
        "current_password": "wrongpassword",
        "new_password": "newpassword123",
    })
    assert response.status_code == 400


def test_update_own_profile(client, auth_headers):
    response = client.put("/auth/me/profile", headers=auth_headers, json={
        "full_name": "Jane Updated",
    })
    assert response.status_code == 200
    assert response.json()["full_name"] == "Jane Updated"

    # Restore
    client.put("/auth/me/profile", headers=auth_headers, json={
        "full_name": "Jane Doe",
    })


def test_member_can_update_own_profile(client, auth_headers):
    # Create a member
    resp = client.post("/users", headers=auth_headers, json={
        "username": "profilemember",
        "full_name": "Profile Member",
        "role": "member",
    })
    assert resp.status_code == 201
    pw = resp.json()["initial_password"]

    # Login as member
    login_resp = client.post("/auth/login", json={
        "username": "profilemember",
        "password": pw,
    })
    member_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

    # Member can update their own profile
    response = client.put("/auth/me/profile", headers=member_headers, json={
        "full_name": "Updated Member",
    })
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Member"


def test_list_users(client, auth_headers):
    response = client.get("/users", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2
    assert "Content-Range" in response.headers


def test_create_user(client, auth_headers):
    response = client.post("/users", headers=auth_headers, json={
        "username": "testuser",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["must_change_password"] is True
    assert "initial_password" in data
    assert "avatar" in data

    # New user can login and must change password
    login_resp = client.post("/auth/login", json={
        "username": "testuser",
        "password": data["initial_password"],
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["must_change_password"] is True


def test_create_duplicate_user(client, auth_headers):
    response = client.post("/users", headers=auth_headers, json={
        "username": "janedoe",
        "full_name": "Duplicate",
    })
    assert response.status_code == 409


def test_update_user(client, auth_headers):
    # Get a user ID first
    users = client.get("/users", headers=auth_headers).json()
    user_id = users[0]["id"]

    original_name = users[0]["full_name"]
    response = client.put(f"/users/{user_id}", headers=auth_headers, json={
        "full_name": "Updated Name",
    })
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"

    # Restore
    client.put(f"/users/{user_id}", headers=auth_headers, json={
        "full_name": original_name,
    })


def test_delete_user(client, auth_headers):
    # Create a user to delete
    create_resp = client.post("/users", headers=auth_headers, json={
        "username": "todelete",
        "full_name": "To Delete",
    })
    user_id = create_resp.json()["id"]

    response = client.delete(f"/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200

    # User should be deactivated, login should fail
    login_resp = client.post("/auth/login", json={
        "username": "todelete",
        "password": create_resp.json()["initial_password"],
    })
    assert login_resp.status_code == 401


def test_recreate_deleted_user(client, auth_headers):
    # Create, delete, then recreate the same username
    resp = client.post("/users", headers=auth_headers, json={
        "username": "recyclable",
        "full_name": "First Version",
    })
    assert resp.status_code == 201
    user_id = resp.json()["id"]

    client.delete(f"/users/{user_id}", headers=auth_headers)

    resp2 = client.post("/users", headers=auth_headers, json={
        "username": "recyclable",
        "full_name": "Second Version",
    })
    assert resp2.status_code == 201
    assert resp2.json()["full_name"] == "Second Version"
    assert resp2.json()["is_active"] is True
    assert "initial_password" in resp2.json()


def test_member_cannot_create_user(client, auth_headers):
    # Create a member user first
    resp = client.post("/users", headers=auth_headers, json={
        "username": "memberuser",
        "full_name": "Member User",
        "role": "member",
    })
    assert resp.status_code == 201
    initial_pw = resp.json()["initial_password"]

    # Login as the member
    login_resp = client.post("/auth/login", json={
        "username": "memberuser",
        "password": initial_pw,
    })
    member_token = login_resp.json()["access_token"]
    member_headers = {"Authorization": f"Bearer {member_token}"}

    # Verify role
    me_resp = client.get("/auth/me", headers=member_headers)
    assert me_resp.json()["role"] == "member"

    # Member can access data routes
    assert client.get("/drivers", headers=member_headers).status_code == 200

    # Member can list users
    assert client.get("/users", headers=member_headers).status_code == 200

    # Member cannot create user
    response = client.post("/users", headers=member_headers, json={
        "username": "blocked",
        "full_name": "Blocked User",
    })
    assert response.status_code == 403

    # Member cannot update user
    users = client.get("/users", headers=member_headers).json()
    user_id = users[0]["id"]
    response = client.put(
        f"/users/{user_id}", headers=member_headers,
        json={"full_name": "Hacked"},
    )
    assert response.status_code == 403

    # Member cannot delete user
    response = client.delete(
        f"/users/{user_id}", headers=member_headers,
    )
    assert response.status_code == 403
