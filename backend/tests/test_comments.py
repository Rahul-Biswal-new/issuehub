import pytest

# ── Helpers ────────────────────────────────────────────────────────────────────

def signup_and_header(client, name="User", email="user@example.com", password="password123"):
    resp = client.post("/api/auth/signup", json={"name": name, "email": email, "password": password})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_project(client, headers, name="Test Project", key="TST"):
    resp = client.post("/api/projects", json={"name": name, "key": key}, headers=headers)
    assert resp.status_code == 200, resp.json()
    return resp.json()


def create_issue(client, headers, project_id, title="A bug"):
    resp = client.post(
        f"/api/projects/{project_id}/issues",
        json={"title": title, "priority": "medium"},
        headers=headers
    )
    assert resp.status_code == 201, resp.json()
    return resp.json()


# ── Task 17: list_comments + create_comment ────────────────────────────────────

def test_create_comment_success(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj  = create_project(client, headers, key="CC1")
    issue = create_issue(client, headers, proj["id"])

    resp = client.post(
        f"/api/issues/{issue['id']}/comments",
        json={"body": "This is a bug comment."},
        headers=headers
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["body"] == "This is a bug comment."
    assert data["issue_id"] == issue["id"]
    assert "id" in data
    assert data["author"]["email"] == "alice@t.com"


def test_list_comments_returns_all(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj  = create_project(client, headers, key="LC1")
    issue = create_issue(client, headers, proj["id"])

    client.post(f"/api/issues/{issue['id']}/comments", json={"body": "First"},  headers=headers)
    client.post(f"/api/issues/{issue['id']}/comments", json={"body": "Second"}, headers=headers)
    client.post(f"/api/issues/{issue['id']}/comments", json={"body": "Third"},  headers=headers)

    resp = client.get(f"/api/issues/{issue['id']}/comments", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    # Comments should be ordered oldest-first
    assert data[0]["body"] == "First"
    assert data[2]["body"] == "Third"


def test_list_comments_empty(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj  = create_project(client, headers, key="LC2")
    issue = create_issue(client, headers, proj["id"])

    resp = client.get(f"/api/issues/{issue['id']}/comments", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_comment_on_nonexistent_issue(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    resp = client.post(
        "/api/issues/99999/comments",
        json={"body": "Ghost comment"},
        headers=headers
    )
    assert resp.status_code == 404


def test_list_comments_nonexistent_issue(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    resp = client.get("/api/issues/99999/comments", headers=headers)
    assert resp.status_code == 404


def test_multiple_authors_in_comment_thread(client):
    """Two members can both comment on the same issue."""
    h_main = signup_and_header(client, "Maintainer", "main@t.com")
    h_memb = signup_and_header(client, "Member",     "memb@t.com")

    proj  = create_project(client, h_main, key="MA1")
    client.post(
        f"/api/projects/{proj['id']}/members",
        json={"email": "memb@t.com", "role": "member"},
        headers=h_main
    )
    issue = create_issue(client, h_main, proj["id"])

    client.post(f"/api/issues/{issue['id']}/comments", json={"body": "Maintainer comment"}, headers=h_main)
    client.post(f"/api/issues/{issue['id']}/comments", json={"body": "Member comment"},     headers=h_memb)

    resp = client.get(f"/api/issues/{issue['id']}/comments", headers=h_main)
    data = resp.json()
    assert len(data) == 2
    authors = {c["author"]["email"] for c in data}
    assert "main@t.com" in authors
    assert "memb@t.com" in authors


# ── Task 18: non-member access denied ─────────────────────────────────────────

def test_list_comments_non_member_forbidden(client):
    """A user who is not a project member cannot read comments."""
    h_owner    = signup_and_header(client, "Owner",    "owner@t.com")
    h_outsider = signup_and_header(client, "Outsider", "out@t.com")

    proj  = create_project(client, h_owner, key="NM1")
    issue = create_issue(client, h_owner, proj["id"])

    resp = client.get(f"/api/issues/{issue['id']}/comments", headers=h_outsider)
    assert resp.status_code == 403


def test_create_comment_non_member_forbidden(client):
    """A user who is not a project member cannot post comments."""
    h_owner    = signup_and_header(client, "Owner",    "owner@t.com")
    h_outsider = signup_and_header(client, "Outsider", "out@t.com")

    proj  = create_project(client, h_owner, key="NM2")
    issue = create_issue(client, h_owner, proj["id"])

    resp = client.post(
        f"/api/issues/{issue['id']}/comments",
        json={"body": "Sneaky comment"},
        headers=h_outsider
    )
    assert resp.status_code == 403


def test_comment_unauthenticated_rejected(client):
    """No token at all → 401."""
    h_owner = signup_and_header(client, "Owner", "owner@t.com")
    proj    = create_project(client, h_owner, key="UN1")
    issue   = create_issue(client, h_owner, proj["id"])

    # Clear stored cookies so this request has no auth at all
    client.cookies.clear()
    resp = client.post(
        f"/api/issues/{issue['id']}/comments",
        json={"body": "No auth"},
        # No headers — no Bearer token either
    )
    assert resp.status_code == 401

