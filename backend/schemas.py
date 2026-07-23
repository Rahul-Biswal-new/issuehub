from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# ---------------- User Schemas ----------------

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------------- Token Schemas ----------------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

# ---------------- Project Schemas ----------------

class ProjectBase(BaseModel):
    name: str
    key: str
    description: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------------- Project Member Schemas ----------------

class ProjectMemberCreate(BaseModel):
    email: EmailStr
    role: str  # "member" or "maintainer"

class ProjectMemberOut(BaseModel):
    project_id: int
    user_id: int
    role: str
    user: UserOut

    class Config:
        from_attributes = True

# ---------------- Issue Schemas ----------------

class IssueCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"  # low | medium | high | critical
    assignee_id: Optional[int] = None

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None       # open | in_progress | resolved | closed
    priority: Optional[str] = None
    assignee_id: Optional[int] = None

class IssueOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    reporter_id: Optional[int] = None
    assignee_id: Optional[int] = None
    reporter: Optional[UserOut] = None
    assignee: Optional[UserOut] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ---------------- Comment Schemas ----------------

class CommentCreate(BaseModel):
    body: str

class CommentOut(BaseModel):
    id: int
    issue_id: int
    author_id: Optional[int] = None
    body: str
    author: Optional[UserOut] = None
    created_at: datetime

    class Config:
        from_attributes = True
