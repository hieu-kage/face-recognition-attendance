from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

class FaceEmbedding(SQLModel, table=True):
    __tablename__ = 'face_embeddings'
    id: Optional[int] = Field(default=None, primary_key=True)

    profile_id: int = Field(foreign_key="profiles.id", unique=True)
    profile: "Profile" = Relationship(back_populates="face_embedding")