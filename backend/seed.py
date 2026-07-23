"""
Run: python seed.py
Creates demo data: 3 users, 2 projects, 15 issues, a few comments.
"""
from database import SessionLocal, engine, Base
import models
from auth_utils import get_password_hash

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── clear existing demo data ──────────────────────────────────────────────────
for table in [models.Comment, models.Issue, models.ProjectMember, models.Project, models.User]:
    db.query(table).delete()
db.commit()

# ── users ─────────────────────────────────────────────────────────────────────
alice = models.User(name="Alice Admin", email="alice@demo.com", password_hash=get_password_hash("password123"))
bob   = models.User(name="Bob Dev",   email="bob@demo.com",   password_hash=get_password_hash("password123"))
carol = models.User(name="Carol QA",  email="carol@demo.com", password_hash=get_password_hash("password123"))
db.add_all([alice, bob, carol])
db.commit()

# ── projects ──────────────────────────────────────────────────────────────────
proj1 = models.Project(name="Frontend Revamp", key="FE", description="Overhaul the customer-facing UI.")
proj2 = models.Project(name="API Platform",   key="API", description="Backend API improvements and fixes.")
db.add_all([proj1, proj2])
db.commit()

# ── memberships ───────────────────────────────────────────────────────────────
db.add_all([
    models.ProjectMember(project_id=proj1.id, user_id=alice.id, role="maintainer"),
    models.ProjectMember(project_id=proj1.id, user_id=bob.id,   role="member"),
    models.ProjectMember(project_id=proj2.id, user_id=alice.id, role="maintainer"),
    models.ProjectMember(project_id=proj2.id, user_id=carol.id, role="member"),
    models.ProjectMember(project_id=proj2.id, user_id=bob.id,   role="member"),
])
db.commit()

# ── issues ────────────────────────────────────────────────────────────────────
fe_issues = [
    ("Navbar overlaps content on mobile", "high", "open", bob.id, alice.id),
    ("Dark mode toggle not persisting", "medium", "in_progress", bob.id, bob.id),
    ("Button hover state missing", "low", "open", bob.id, None),
    ("Font loading causes FOUT", "medium", "resolved", alice.id, bob.id),
    ("Hero image not loading on Safari", "critical", "open", alice.id, bob.id),
    ("404 page lacks branding", "low", "closed", bob.id, None),
    ("Form validation messages overlap", "high", "in_progress", alice.id, bob.id),
    ("Footer links broken on IE11", "low", "closed", bob.id, None),
]

api_issues = [
    ("JWT expiry not handled gracefully", "critical", "open", carol.id, alice.id),
    ("Rate limiting missing on /auth endpoints", "high", "open", carol.id, alice.id),
    ("Pagination broken for large datasets", "medium", "in_progress", carol.id, bob.id),
    ("CORS wildcard in production", "high", "resolved", alice.id, alice.id),
    ("DB connection pool exhaustion", "critical", "open", carol.id, alice.id),
    ("Missing index on issues.status", "medium", "open", bob.id, None),
    ("Soft-delete not implemented", "low", "open", carol.id, None),
]

created_issues = []
for title, priority, status, reporter_id, assignee_id in fe_issues:
    i = models.Issue(project_id=proj1.id, title=title, priority=priority,
                     status=status, reporter_id=reporter_id, assignee_id=assignee_id)
    db.add(i)
    created_issues.append(i)

for title, priority, status, reporter_id, assignee_id in api_issues:
    i = models.Issue(project_id=proj2.id, title=title, priority=priority,
                     status=status, reporter_id=reporter_id, assignee_id=assignee_id)
    db.add(i)
    created_issues.append(i)

db.commit()

# ── comments ─────────────────────────────────────────────────────────────────
first_issue = created_issues[0]
db.add_all([
    models.Comment(issue_id=first_issue.id, author_id=alice.id, body="Reproduced on Chrome 120. Affects the hamburger menu too."),
    models.Comment(issue_id=first_issue.id, author_id=bob.id,   body="Working on a fix — should be a z-index issue."),
    models.Comment(issue_id=first_issue.id, author_id=alice.id, body="Please also test on Firefox mobile."),
])
second_issue = created_issues[8]  # JWT expiry
db.add_all([
    models.Comment(issue_id=second_issue.id, author_id=carol.id, body="Users get a blank screen instead of a redirect to /login."),
    models.Comment(issue_id=second_issue.id, author_id=alice.id, body="Confirmed. We need to intercept 401s in the API layer."),
])
db.commit()

print("Seed complete!")
print(f"   Users:    alice@demo.com / bob@demo.com / carol@demo.com  (password: password123)")
print(f"   Projects: {proj1.name} ({proj1.key}), {proj2.name} ({proj2.key})")
print(f"   Issues:   {len(created_issues)}")

