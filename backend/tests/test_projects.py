import pytest

# Helper to create user and login to get JWT header
def get_auth_header(client, name="Test User", email="test@example.com"):
    signup_payload = {
        "name": name,
        "email": email,
        "password": "password123"
    }
    resp = client.post("/api/auth/signup", json=signup_payload)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_project_success(client):
    headers = get_auth_header(client)
    
    project_payload = {
        "name": "IssueHub Project",
        "key": "IHUB",
        "description": "Sleek bug tracker project"
    }
    
    response = client.post("/api/projects", json=project_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "IssueHub Project"
    assert data["key"] == "IHUB"
    assert "id" in data

def test_create_project_duplicate_key(client):
    headers = get_auth_header(client)
    
    project_payload = {
        "name": "First Project",
        "key": "IHUB",
        "description": "First"
    }
    client.post("/api/projects", json=project_payload, headers=headers)
    
    # Try creating with duplicate key
    response = client.post("/api/projects", json=project_payload, headers=headers)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "PROJECT_KEY_ALREADY_EXISTS"

def test_list_projects_membership(client):
    # Setup two users
    headers1 = get_auth_header(client, "User One", "user1@example.com")
    headers2 = get_auth_header(client, "User Two", "user2@example.com")
    
    # User 1 creates project
    proj_payload1 = {"name": "Proj One", "key": "ONE"}
    client.post("/api/projects", json=proj_payload1, headers=headers1)
    
    # User 2 creates project
    proj_payload2 = {"name": "Proj Two", "key": "TWO"}
    client.post("/api/projects", json=proj_payload2, headers=headers2)
    
    # User 1 lists projects: should only see Proj One
    resp1 = client.get("/api/projects", headers=headers1)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert len(data1) == 1
    assert data1[0]["key"] == "ONE"
    
    # User 2 lists projects: should only see Proj Two
    resp2 = client.get("/api/projects", headers=headers2)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2) == 1
    assert data2[0]["key"] == "TWO"

def test_add_project_member_success(client):
    headers1 = get_auth_header(client, "User One", "user1@example.com")
    headers2 = get_auth_header(client, "User Two", "user2@example.com") # will register user2 in DB
    
    # User 1 creates project
    proj_payload = {"name": "Test Project", "key": "TEST"}
    proj_resp = client.post("/api/projects", json=proj_payload, headers=headers1)
    project_id = proj_resp.json()["id"]
    
    # User 1 (maintainer) adds User 2 as member
    member_payload = {
        "email": "user2@example.com",
        "role": "member"
    }
    response = client.post(f"/api/projects/{project_id}/members", json=member_payload, headers=headers1)
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == project_id
    assert data["role"] == "member"
    assert data["user"]["email"] == "user2@example.com"
    
    # User 2 can now list this project (only 1 — user2 didn't create any)
    list_resp = client.get("/api/projects", headers=headers2)
    assert len(list_resp.json()) == 1

def test_add_member_unauthorized_role(client):
    # Register two users
    headers_maintainer = get_auth_header(client, "Maintainer", "m@example.com")
    headers_other = get_auth_header(client, "Other User", "o@example.com")
    headers_member = get_auth_header(client, "Member User", "memb@example.com") # registe memb
    
    # Maintainer creates project
    proj_payload = {"name": "Secret Project", "key": "SEC"}
    proj_resp = client.post("/api/projects", json=proj_payload, headers=headers_maintainer)
    project_id = proj_resp.json()["id"]
    
    # Maintainer invites member as "member" role
    client.post(f"/api/projects/{project_id}/members", json={"email": "memb@example.com", "role": "member"}, headers=headers_maintainer)
    
    # Non-maintainer (member) tries to invite "Other User"
    member_payload = {"email": "o@example.com", "role": "member"}
    response = client.post(f"/api/projects/{project_id}/members", json=member_payload, headers=headers_member)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
