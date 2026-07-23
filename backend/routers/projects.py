from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
from dependencies import get_current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("", response_model=schemas.ProjectOut)
def create_project(
    project_data: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if project key is already taken
    existing_key = db.query(models.Project).filter(models.Project.key == project_data.key.upper()).first()
    if existing_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "PROJECT_KEY_ALREADY_EXISTS",
                    "message": f"A project with key '{project_data.key.upper()}' already exists."
                }
            }
        )
        
    # Create the project
    new_project = models.Project(
        name=project_data.name,
        key=project_data.key.upper(),
        description=project_data.description
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Creator automatically becomes maintainer
    membership = models.ProjectMember(
        project_id=new_project.id,
        user_id=current_user.id,
        role="maintainer"
    )
    db.add(membership)
    db.commit()
    
    return new_project

@router.get("", response_model=List[schemas.ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Query projects where the user is a member/maintainer
    projects = (
        db.query(models.Project)
        .join(models.ProjectMember)
        .filter(models.ProjectMember.user_id == current_user.id)
        .all()
    )
    return projects


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "PROJECT_NOT_FOUND", "message": "Project not found."}}
        )
    # Only members can fetch a project
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Not a member of this project."}}
        )
    return project

@router.post("/{project_id}/members", response_model=schemas.ProjectMemberOut)
def add_project_member(
    project_id: int,
    member_data: schemas.ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if the project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "PROJECT_NOT_FOUND",
                    "message": "Project does not exist."
                }
            }
        )
        
    # Check if current user is a maintainer of the project
    current_user_membership = (
        db.query(models.ProjectMember)
        .filter(models.ProjectMember.project_id == project_id, models.ProjectMember.user_id == current_user.id)
        .first()
    )
    if not current_user_membership or current_user_membership.role != "maintainer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Only project maintainers can manage project membership."
                }
            }
        )
        
    # Find user to invite by email
    target_user = db.query(models.User).filter(models.User.email == member_data.email).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": f"User with email '{member_data.email}' was not found."
                }
            }
        )
        
    # Check if target user is already a member
    existing_membership = (
        db.query(models.ProjectMember)
        .filter(models.ProjectMember.project_id == project_id, models.ProjectMember.user_id == target_user.id)
        .first()
    )
    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "USER_ALREADY_MEMBER",
                    "message": "User is already a member of this project."
                }
            }
        )
        
    # Add new project member
    new_member = models.ProjectMember(
        project_id=project_id,
        user_id=target_user.id,
        role=member_data.role
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return new_member


@router.get("/{project_id}/members", response_model=List[schemas.ProjectMemberOut])
def list_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Must be a member to view the member list
    membership = db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id,
        models.ProjectMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Not a member of this project."}}
        )
    return db.query(models.ProjectMember).filter(
        models.ProjectMember.project_id == project_id
    ).all()
