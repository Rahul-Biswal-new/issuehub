import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    project_memberships = relationship("ProjectMember", back_populates="user", cascade="all, delete-orphan")
    reported_issues = relationship("Issue", foreign_keys="[Issue.reporter_id]", back_populates="reporter")
    assigned_issues = relationship("Issue", foreign_keys="[Issue.assignee_id]", back_populates="assignee")
    comments = relationship("Comment", back_populates="author")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")

class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # "member" or "maintainer"

    __table_args__ = (
        PrimaryKeyConstraint("project_id", "user_id"),
    )

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")

class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="open", nullable=False)      # "open", "in_progress", "resolved", "closed"
    priority = Column(String, default="medium", nullable=False)  # "low", "medium", "high", "critical"
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="issues")
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reported_issues")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_issues")
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    issue = relationship("Issue", back_populates="comments")
    author = relationship("User", back_populates="comments")
