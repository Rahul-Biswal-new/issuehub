from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
from dependencies import get_current_user, get_member

router = APIRouter(tags=["comments"])


@router.get("/api/issues/{issue_id}/comments", response_model=List[schemas.CommentOut])
def list_comments(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")
    if not get_member(db, issue.project_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this project.")

    return (
        db.query(models.Comment)
        .filter(models.Comment.issue_id == issue_id)
        .order_by(models.Comment.created_at)
        .all()
    )


@router.post("/api/issues/{issue_id}/comments", response_model=schemas.CommentOut, status_code=201)
def create_comment(
    issue_id: int,
    comment_data: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    issue = db.query(models.Issue).filter(models.Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")
    if not get_member(db, issue.project_id, current_user.id):
        raise HTTPException(status_code=403, detail="Not a member of this project.")

    comment = models.Comment(
        issue_id=issue_id,
        author_id=current_user.id,
        body=comment_data.body,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

