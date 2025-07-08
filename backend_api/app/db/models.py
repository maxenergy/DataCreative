```python
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # For server-side default timestamp

from .database import Base # Import Base from database.py

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    config_json = Column(Text, nullable=True) # For Label Studio labeling config or other settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    images = relationship("Image", back_populates="project")
    labels = relationship("Label", back_populates="project")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    original_file_path = Column(String, nullable=False) # Path in the local FS or object storage key
    generated_file_path = Column(String, nullable=True) # Path if this is an AI-generated image

    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    # If generated, links to the base image used for generation
    source_image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    generation_params_json = Column(Text, nullable=True) # e.g., prompt, model used for generation

    project = relationship("Project", back_populates="images")
    source_image = relationship("Image", remote_side=[id], backref="generated_from_this") # Self-referential for source image
    annotations = relationship("Annotation", back_populates="image")


class Label(Base): # Represents an object category/class
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False, index=True) # e.g., "car", "person", "unknown"
    color_hex = Column(String, nullable=True) # Optional, for UI display

    project = relationship("Project", back_populates="labels")
    annotations = relationship("Annotation", back_populates="label")

    __table_args__ = (UniqueConstraint('project_id', 'name', name='_project_label_uc'),)


class Annotation(Base): # Represents a single bounding box annotation
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_id = Column(Integer, ForeignKey("images.id"), nullable=False)
    label_id = Column(Integer, ForeignKey("labels.id"), nullable=False) # Foreign key to the 'labels' table

    x_min = Column(Float, nullable=False)
    y_min = Column(Float, nullable=False)
    x_max = Column(Float, nullable=False)
    y_max = Column(Float, nullable=False)

    confidence_score = Column(Float, nullable=True) # If from an AI model
    source_type = Column(String, nullable=True) # e.g., 'manual', 'yolo_uniow_v1.0', 'gligen_v1.1'
    is_unknown = Column(Boolean, default=False) # If flagged as 'unknown' by OWOD model initially

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    image = relationship("Image", back_populates="annotations")
    label = relationship("Label", back_populates="annotations")

# To ensure all models are known to Base before table creation,
# you might need to import them in database.py before calling Base.metadata.create_all,
# or ensure this file (models.py) is imported by an __init__.py in the db folder
# which in turn is imported before create_db_and_tables is called.
```
