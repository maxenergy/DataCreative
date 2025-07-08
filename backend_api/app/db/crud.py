```python
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from . import models as db_models
from ..models import schemas

# --- Project CRUD ---
def get_project(db: Session, project_id: int) -> Optional[db_models.Project]:
    return db.query(db_models.Project).filter(db_models.Project.id == project_id).first()

def get_project_by_name(db: Session, project_name: str) -> Optional[db_models.Project]:
    return db.query(db_models.Project).filter(db_models.Project.name == project_name).first()

def create_project(db: Session, project: schemas.ProjectCreate) -> db_models.Project:
    db_project = db_models.Project(
        name=project.name,
        description=project.description,
        config_json=project.config_json
    )
    db.add(db_project)
    try:
        db.commit()
        db.refresh(db_project)
    except IntegrityError: # Handles unique constraint violation for name
        db.rollback()
        existing_project = get_project_by_name(db, project.name)
        if existing_project:
            return existing_project # Or raise an error, depending on desired behavior
        else: # Should not happen if IntegrityError was due to name
            raise
    return db_project

def get_or_create_project(db: Session, project_identifier: str) -> db_models.Project:
    """Gets a project by ID (if numeric string) or name, or creates it if it doesn't exist by name."""
    project_id = None
    if project_identifier.isdigit():
        project_id = int(project_identifier)
        db_project = get_project(db, project_id)
        if db_project:
            return db_project

    # If not found by ID or identifier is not numeric, try by name
    db_project = get_project_by_name(db, project_name=project_identifier)
    if db_project:
        return db_project

    # If still not found, create it (assuming identifier was a name)
    # Use default description and config if not provided.
    print(f"Project '{project_identifier}' not found, creating new project.")
    return create_project(db, schemas.ProjectCreate(name=project_identifier))


# --- Label CRUD ---
def get_label_by_name_and_project(db: Session, label_name: str, project_id: int) -> Optional[db_models.Label]:
    return db.query(db_models.Label).filter(
        db_models.Label.name == label_name,
        db_models.Label.project_id == project_id
    ).first()

def create_label(db: Session, label: schemas.LabelCreate) -> db_models.Label:
    db_label = db_models.Label(
        name=label.name,
        project_id=label.project_id,
        color_hex=label.color_hex
    )
    db.add(db_label)
    try:
        db.commit()
        db.refresh(db_label)
    except IntegrityError: # Handles unique constraint (project_id, name)
        db.rollback()
        existing_label = get_label_by_name_and_project(db, label.name, label.project_id)
        if existing_label:
            return existing_label
        else:
            raise
    return db_label

def get_or_create_label(db: Session, label_name: str, project_id: int, color_hex: Optional[str] = None) -> db_models.Label:
    db_label = get_label_by_name_and_project(db, label_name=label_name, project_id=project_id)
    if db_label:
        return db_label

    return create_label(db, schemas.LabelCreate(name=label_name, project_id=project_id, color_hex=color_hex))

# --- Image CRUD ---
def get_image_by_path_and_project(db: Session, image_path: str, project_id: int) -> Optional[db_models.Image]:
    return db.query(db_models.Image).filter(
        db_models.Image.original_file_path == image_path,
        db_models.Image.project_id == project_id
    ).first()

def create_image_record(db: Session, image: schemas.ImageCreate) -> db_models.Image:
    db_image = db_models.Image(
        project_id=image.project_id,
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

def get_or_create_image(db: Session, image_path: str, project_id: int, width: Optional[int]=None, height: Optional[int]=None) -> db_models.Image:
    db_image = get_image_by_path_and_project(db, image_path=image_path, project_id=project_id)
    if db_image:
        # Optionally update width/height if not set and provided now
        if width and not db_image.width: db_image.width = width
        if height and not db_image.height: db_image.height = height
        if db.is_modified(db_image):
            db.commit()
            db.refresh(db_image)
        return db_image

    return create_image_record(db, schemas.ImageCreate(
        project_id=project_id,
        original_file_path=image_path,
        width=width,
        height=height
    ))


def get_image(db: Session, image_id: int) -> Optional[db_models.Image]:
    return db.query(db_models.Image).filter(db_models.Image.id == image_id).first()

# --- Annotation CRUD ---
def create_annotation_records(db: Session, annotations_data: List[schemas.AnnotationCreate], image_id: int, project_id: int) -> List[db_models.Annotation]:
    db_annotations = []
    for ann_data in annotations_data:
        # Get or create the label for this annotation
        db_label = get_or_create_label(db, label_name=ann_data.label_name, project_id=project_id)

        db_ann = db_models.Annotation(
            image_id=image_id,
            label_id=db_label.id, # Use the ID from the fetched/created label
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

    if db_annotations: # Only commit if there are annotations to add
        db.commit()
        for db_ann in db_annotations: # Refresh each object to get IDs, etc.
            db.refresh(db_ann)
    return db_annotations

def get_annotations_for_image(db: Session, image_id: int) -> List[db_models.Annotation]:
    return db.query(db_models.Annotation).filter(db_models.Annotation.image_id == image_id).all()
```
