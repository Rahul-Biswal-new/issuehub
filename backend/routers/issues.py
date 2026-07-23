from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from database import get_db
import models
import schemas
from dependencies import get_current_user

router = APIRouter(tags=["issues"])


def _get_member(db: Session, project_id: int, user_id: int):
    return (
        db.query(models.ProjectMember)
        .filter(
            models.ProjectMember.project_id == project_id,
            models.ProjectMember.user_id == user_id,
        )
        .first()
    )


# ── List / Create issues ──────────────────────────────────────────────────────

@router.get("/api/projects/{project_id}/issues", response_model=List[schemas.IssueOut])
def list_issues(
    project_id: int,
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee_id: Optional[int] = Query(None),
    sort: Optional[str] = Query("created_at"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not _get_member(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this project.")

    query = db.query(models.Issue).filter(models.Issue.project_id == project_id)

    if q:
        query = query.filter(models.Issue.title.ilike(f"%{q}%"))
    if status:
        query = query.filter(models.Issue.status == status)
    if priority:
        query = query.filter(models.Issue.priority == priority)
    if assignee_id:
        query = query.filter(models.Issue.assignee_id == assignee_id)

    issues = query.all()

    PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    STATUS_ORDER = {"open": 0, "in_progress": 1, "resolved": 2, "closed": 3}

    if sort == "priority":
        issues.sort(key=lambda i: PRIORITY_ORDER.get(i.priority, 99))
    elif sort == "status":
        issues.sort(key=lambda i: STATUS_ORDER.get(i.status, 99))
    else:
        issues.sort(key=lambda i: i.created_at, reverse=True)

    return issues


@router.post("/api/projects/{project_id}/issues", response_model=schemas.IssueOut, status_code=201)
def create_issue(
    project_id: int,
    issue_data: schemas.IssueCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not _get_member(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this project.")

    issue = models.Issue(
        project_id=project_id,
        title=issue_data.title,
        description=issue_data.description,
        priority=issue_data.priority or "medium",
        assignee_id=issue_data.assignee_id,
        reporter_id=current_user.id,
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    return issue


# ── Single issue ──────────────────────────────────────────────────────────────

@router.get("/api/issues/{issue_id}", response_model=schemas.IssueOut)
def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")
    if not _get_member(db, issue.project_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this project.")
    return issue


@router.patch("/api/issues/{issue_id}", response_model=schemas.IssueOut)
def update_issue(
    issue_id: int,
    update_data: schemas.IssueUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    membership = _get_member(db, issue.project_id, current_user.id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this project.")

    is_maintainer = membership.role == "maintainer"
    is_reporter = issue.reporter_id == current_user.id

    if (update_data.status is not None or update_data.assignee_id is not None) and not is_maintainer:
        raise HTTPException(status_code=403, detail="Only maintainers can change status or assignee.")

    if update_data.title is not None and not (is_maintainer or is_reporter):
        raise HTTPException(status_code=403, detail="Only maintainers or the reporter can edit this issue.")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(issue, field, value)

    issue.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(issue)
    return issue


@router.delete("/api/issues/{issue_id}", status_code=204)
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    membership = _get_member(db, issue.project_id, current_user.id)
    if not membership or (membership.role != "maintainer" and issue.reporter_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this issue.")

    db.delete(issue)
    db.commit()

