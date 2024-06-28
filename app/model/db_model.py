from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.model.db_enum import UserRole

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    is_allowed = Column(Boolean, default=True)
    scopes = Column(Enum(UserRole), default=UserRole.USER)

    response_sentence = relationship("ResponseSentence", back_populates="user")


class Project(Base):
    __tablename__ = "project"
    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    source_sentences = relationship("SourceSentence", back_populates="project")
    response_sentences = relationship("ResponseSentence", back_populates="project")


class SourceSentence(Base):
    __tablename__ = "source_sentence"
    sentence_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    source_sentence = Column(String)

    project = relationship("Project", back_populates="source_sentences")
    response_sentence = relationship("ResponseSentence", back_populates="source_sentences")


class ResponseSentence(Base):
    __tablename__ = "response_sentence"
    sentence_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.project_id"))
    source_sentence_id = Column(Integer, ForeignKey("source_sentence.sentence_id"))
    response_sentence = Column(String)
    user_id = Column(Integer, ForeignKey("user.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    project = relationship("Project", back_populates="response_sentences")
    source_sentences = relationship("SourceSentence", back_populates="response_sentence")
    user = relationship("User", back_populates="response_sentence")
