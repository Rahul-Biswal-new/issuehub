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


def create_issue(client, headers, project_id, title="A bug", priority="medium", assignee_id=None):
    body = {"title": title, "priority": priority}
    if assignee_id is not None:
        body["assignee_id"] = assignee_id
    resp = client.post(f"/api/projects/{project_id}/issues", json=body, headers=headers)
    assert resp.status_code == 201, resp.json()
    return resp.json()


# ── Task 11: create_issue + list_issues (basic) ────────────────────────────────

def test_create_issue_success(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj = create_project(client, headers, key="CI1")
    issue = create_issue(client, headers, proj["id"], title="Login broken")

    assert issue["title"] == "Login broken"
    assert issue["status"] == "open"
    assert issue["priority"] == "medium"
    assert issue["project_id"] == proj["id"]
    assert "id" in issue


def test_create_issue_non_member_forbidden(client):
    h1 = signup_and_header(client, "Alice", "alice@t.com")
    h2 = signup_and_header(client, "Bob",   "bob@t.com")
    proj = create_project(client, h1, key="CI2")

    resp = client.post(
        f"/api/projects/{proj['id']}/issues",
        json={"title": "Sneaky issue"},
        headers=h2
    )
    assert resp.status_code == 403


def test_list_issues_basic(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj = create_project(client, headers, key="LI1")
    create_issue(client, headers, proj["id"], title="Bug 1")
    create_issue(client, headers, proj["id"], title="Bug 2")

    resp = client.get(f"/api/projects/{proj['id']}/issues", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    titles = {i["title"] for i in data}
    assert "Bug 1" in titles and "Bug 2" in titles


# ── Task 12: filter by status ──────────────────────────────────────────────────

def test_list_issues_filter_by_status(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj = create_project(client, headers, key="FS1")

    i1 = create_issue(client, headers, proj["id"], title="Open issue")
    # patch i1 to in_progress
    client.patch(f"/api/issues/{i1['id']}", json={"status": "in_progress"}, headers=headers)
    create_issue(client, headers, proj["id"], title="Another open issue")

    # filter open
    resp = client.get(f"/api/projects/{proj['id']}/issues?status=open", headers=headers)
    assert resp.status_code == 200
    results = resp.json()
    assert all(i["status"] == "open" for i in results)
    assert len(results) == 1

    # filter in_progress
    resp2 = client.get(f"/api/projects/{proj['id']}/issues?status=in_progress", headers=headers)
    assert resp2.status_code == 200
    assert len(resp2.json()) == 1
    assert resp2.json()[0]["status"] == "in_progress"


# ── Task 13: filter by priority ───────────────────────────────────────────────

def test_list_issues_filter_by_priority(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj = create_project(client, headers, key="FP1")

    create_issue(client, headers, proj["id"], title="Critical bug", priority="critical")
    create_issue(client, headers, proj["id"], title="Low bug",      priority="low")
    create_issue(client, headers, proj["id"], title="Low bug 2",    priority="low")

    resp = client.get(f"/api/projects/{proj['id']}/issues?priority=low", headers=headers)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 2
    assert all(i["priority"] == "low" for i in results)

    resp2 = client.get(f"/api/projects/{proj['id']}/issues?priority=critical", headers=headers)
    assert len(resp2.json()) == 1


# ── Task 14: get_issue + update_issue (maintainer) ────────────────────────────

def test_get_issue(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj  = create_project(client, headers, key="GI1")
    issue = create_issue(client, headers, proj["id"], title="Fetch me")

    resp = client.get(f"/api/issues/{issue['id']}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == issue["id"]
    assert data["title"] == "Fetch me"


def test_get_issue_not_found(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    resp = client.get("/api/issues/99999", headers=headers)
    assert resp.status_code == 404


def test_update_issue_maintainer_can_change_status(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj  = create_project(client, headers, key="UI1")
    issue = create_issue(client, headers, proj["id"], title="To resolve")

    resp = client.patch(
        f"/api/issues/{issue['id']}",
        json={"status": "resolved"},
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "resolved"


def test_update_issue_maintainer_can_change_priority(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj  = create_project(client, headers, key="UI2")
    issue = create_issue(client, headers, proj["id"], title="Priority shift")

    resp = client.patch(
        f"/api/issues/{issue['id']}",
        json={"priority": "critical"},
        headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["priority"] == "critical"


# ── Task 15: update_issue permission (non-maintainer) ─────────────────────────

def test_update_issue_member_cannot_change_status(client):
    """A plain member (not maintainer, not reporter) cannot change status."""
    h_main = signup_and_header(client, "Maintainer", "main@t.com")
    h_memb = signup_and_header(client, "Member",     "memb@t.com")

    proj  = create_project(client, h_main, key="NM1")
    # Add member to project
    client.post(
        f"/api/projects/{proj['id']}/members",
        json={"email": "memb@t.com", "role": "member"},
        headers=h_main
    )
    issue = create_issue(client, h_main, proj["id"], title="Status-locked bug")

    resp = client.patch(
        f"/api/issues/{issue['id']}",
        json={"status": "closed"},
        headers=h_memb
    )
    assert resp.status_code == 403


def test_update_issue_reporter_can_edit_title(client):
    """The reporter (a plain member) can still edit title/description."""
    h_main = signup_and_header(client, "Maintainer", "main@t.com")
    h_rep  = signup_and_header(client, "Reporter",   "rep@t.com")

    proj = create_project(client, h_main, key="RE1")
    client.post(
        f"/api/projects/{proj['id']}/members",
        json={"email": "rep@t.com", "role": "member"},
        headers=h_main
    )
    issue = create_issue(client, h_rep, proj["id"], title="Original title")

    resp = client.patch(
        f"/api/issues/{issue['id']}",
        json={"title": "Updated title"},
        headers=h_rep
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated title"


def test_update_issue_invalid_status_rejected(client):
    """Invalid status value should return 422."""
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj  = create_project(client, headers, key="IV1")
    issue = create_issue(client, headers, proj["id"], title="Validate me")

    resp = client.patch(
        f"/api/issues/{issue['id']}",
        json={"status": "banana"},
        headers=headers
    )
    assert resp.status_code == 422


# ── Task 16: delete_issue ──────────────────────────────────────────────────────

def test_delete_issue_reporter_can_delete(client):
    h_main = signup_and_header(client, "Maintainer", "main@t.com")
    h_rep  = signup_and_header(client, "Reporter",   "rep@t.com")

    proj = create_project(client, h_main, key="DL1")
    client.post(
        f"/api/projects/{proj['id']}/members",
        json={"email": "rep@t.com", "role": "member"},
        headers=h_main
    )
    issue = create_issue(client, h_rep, proj["id"], title="Delete me")

    resp = client.delete(f"/api/issues/{issue['id']}", headers=h_rep)
    assert resp.status_code == 204

    # Confirm gone
    check = client.get(f"/api/issues/{issue['id']}", headers=h_main)
    assert check.status_code == 404


def test_delete_issue_maintainer_can_delete(client):
    headers = signup_and_header(client, "Alice", "alice@t.com")
    proj  = create_project(client, headers, key="DL2")
    issue = create_issue(client, headers, proj["id"], title="Remove me")

    resp = client.delete(f"/api/issues/{issue['id']}", headers=headers)
    assert resp.status_code == 204


def test_delete_issue_unauthorized_member_blocked(client):
    """A plain member who is NOT the reporter cannot delete."""
    h_main  = signup_and_header(client, "Maintainer", "main@t.com")
    h_other = signup_and_header(client, "Other",      "other@t.com")

    proj  = create_project(client, h_main, key="DL3")
    client.post(
        f"/api/projects/{proj['id']}/members",
        json={"email": "other@t.com", "role": "member"},
        headers=h_main
    )
    issue = create_issue(client, h_main, proj["id"], title="Not yours")

    resp = client.delete(f"/api/issues/{issue['id']}", headers=h_other)
    assert resp.status_code == 403
