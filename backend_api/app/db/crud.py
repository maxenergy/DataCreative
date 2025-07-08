```python
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models as db_models # To avoid confusion with Pydantic schemas
from ..models import schemas # Pydantic schemas for request/response data validation

# --- Project CRUD ---
def get_project(db: Session, project_id: int) -> Optional[db_models.Project]:
    return db.query(db_models.Project).filter(db_models.Project.id == project_id).first()

def get_project_by_name(db: Session, project_name: str) -> Optional[db_models.Project]:
    return db.query(db_models.Project).filter(db_models.Project.name == project_name).first()

def create_project(db: Session, project: schemas.Project) -> db_models.Project:
    # Assuming schemas.Project is used for creation and has compatible fields.
    # You might want a specific schemas.ProjectCreate if fields differ.
    db_project = db_models.Project(
        name=project.project_name, # Assuming project_name in Pydantic schema
        description=project.description,
        config_json=project.config_json
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# --- Label CRUD ---
def get_label_by_name(db: Session, label_name: str, project_id: int) -> Optional[db_models.Label]:
    return db.query(db_models.Label).filter(db_models.Label.name == label_name, db_models.Label.project_id == project_id).first()

def get_or_create_label(db: Session, label_name: str, project_id: int, color_hex: Optional[str] = None) -> db_models.Label:
    db_label = get_label_by_name(db, label_name=label_name, project_id=project_id)
    if db_label:
        return db_label
    db_label = db_models.Label(name=label_name, project_id=project_id, color_hex=color_hex)
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label

# --- Image CRUD ---
def create_image_record(db: Session, image: schemas.Image, project_id: int) -> db_models.Image:
    # Assuming schemas.Image is used for creation.
    # You might want a specific schemas.ImageCreate.
    db_image = db_models.Image(
        project_id=project_id,
        original_file_path=image.original_file_path,
        generated_file_path=image.generated_file_path,
        width=image.width,
        height=image.height,
        source_image_id=image.source_image_id,
        generation_params_json=image.generation_params_json
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

def get_image(db: Session, image_id: int) -> Optional[db_models.Image]:
    return db.query(db_models.Image).filter(db_models.Image.id == image_id).first()

# --- Annotation CRUD ---
def create_annotation_records(db: Session, annotations: List[schemas.Annotation], image_id: int) -> List[db_models.Annotation]:
    # Assuming schemas.Annotation is used for creation.
    # You might want a specific schemas.AnnotationCreate.
    db_annotations = []
    for ann_data in annotations:
        # Ensure label_id is present or fetch/create it
        # This part depends on how label_id is handled in schemas.Annotation
        # If ann_data.label_id is not directly provided, you'd fetch it using get_or_create_label
        # For now, assuming ann_data.label_id is correctly populated or handled upstream.
        if ann_data.label_id is None: # Or some other check if label name is provided instead
            raise ValueError("label_id must be provided for creating an annotation.")

        db_ann = db_models.Annotation(
            image_id=image_id,
            label_id=ann_data.label_id, # This assumes schemas.Annotation has label_id
            x_min=ann_data.x_min,
            y_min=ann_data.y_min,
            x_max=ann_data.x_max,
            y_max=ann_data.y_max,
            confidence_score=ann_data.confidence_score,
            source_type=ann_data.source_type,
            is_unknown=ann_data.is_unknown
        )
        db.add(db_ann)
        db_annotations.append(db_ann)
    db.commit()
    for db_ann in db_annotations: # Refresh each object to get IDs, etc.
        db.refresh(db_ann)
    return db_annotations

def get_annotations_for_image(db: Session, image_id: int) -> List[db_models.Annotation]:
    return db.query(db_models.Annotation).filter(db_models.Annotation.image_id == image_id).all()

# Placeholder for Pydantic create schemas if they differ significantly from main schemas
# For example:
# class ProjectCreate(schemas.ProjectBase): # Assuming ProjectBase has common fields
#     pass
# class ImageCreate(schemas.ImageBase):
#     pass
# class AnnotationCreate(schemas.AnnotationBase):
#     label_name: Optional[str] = None # Could pass label name instead of id
```
