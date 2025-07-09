```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Base Schemas (common fields for creation and reading) ---

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, example="Project Alpha")
    description: Optional[str] = Field(None, example="Initial project for detecting cars.")
    config_json: Optional[str] = Field(None, example="<View>...</View>") # Label Studio labeling config

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime # Should be populated by DB default
    updated_at: Optional[datetime] = None # Should be populated by DB on update

    class Config:
        orm_mode = True

class ImageBase(BaseModel):
    original_file_path: Optional[str] = Field(None, example="/data/images/project_1/original/img_001.jpg") # Made optional
    generated_file_path: Optional[str] = Field(None, example="/data/images/project_1/generated/img_001_gen.jpg")
    width: Optional[int] = Field(None, example=1920)
    height: Optional[int] = Field(None, example=1080)
    source_image_id: Optional[int] = Field(None, description="If generated, ID of the base image.")
    generation_params_json: Optional[str] = Field(None, description="e.g., prompt, model used for generation.")

class ImageCreate(ImageBase):
    project_id: int

class Image(ImageBase):
    id: int
    project_id: int
    uploaded_at: datetime # Should be populated by DB default

    class Config:
        orm_mode = True

class LabelBase(BaseModel):
    name: str = Field(..., min_length=1, example="car")
    color_hex: Optional[str] = Field(None, example="#FF0000")

class LabelCreate(LabelBase):
    project_id: int

class Label(LabelBase):
    id: int
    project_id: int

    class Config:
        orm_mode = True

class AnnotationBase(BaseModel):
    x_min: float = Field(..., example=100.5)
    y_min: float = Field(..., example=200.0)
    x_max: float = Field(..., example=150.5)
    y_max: float = Field(..., example=250.0)
    confidence_score: Optional[float] = Field(None, example=0.95)
    source_type: Optional[str] = Field(None, example="yolo_uniow_v1.0")
    is_unknown: Optional[bool] = Field(False, example=False)

class AnnotationCreate(AnnotationBase):
    # image_id and label_id will be passed directly to CRUD, not part of this schema
    # if we build annotations before we have the image/label DB records.
    # Alternatively, if creating via an image, label_id is essential.
    # For now, let's assume label_name will be used to find/create label_id in CRUD.
    label_name: str # We'll use this to find/create the Label record and get its ID.

class Annotation(AnnotationBase):
    id: int
    image_id: int
    label_id: int
    created_at: datetime # Should be populated by DB default
    updated_at: Optional[datetime] = None # Should be populated by DB on update

    class Config:
        orm_mode = True

# --- API Specific Schemas (matching Label Studio ML Backend expectations where applicable) ---

class LabelStudioTaskDataItem(BaseModel):
    # Flexible data part of a task, often contains 'image' or other keys based on LS config
    image: Optional[str] = None # Example: value of <Image name="image" value="$image_url" />
    # Add other potential keys if your LS configs use them, e.g. text: Optional[str] = None

class LabelStudioTaskItem(BaseModel):
    id: int # Task ID from Label Studio
    data: LabelStudioTaskDataItem # More specific data type

class LabelStudioRequest(BaseModel):
    tasks: List[LabelStudioTaskItem]
    label_config: Optional[str] = Field(None, description="Label Studio XML Labeling Configuration")
    project: Optional[str] = Field(None, description="Project ID from Label Studio (can be string ID)")
    params: Optional[Dict[str, Any]] = Field(None, description="Other params like context from LS")

class LSAnnotationResultItemValue(BaseModel):
    rectanglelabels: Optional[List[str]] = None
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    # Add other LS types like: choices: Optional[List[str]] = None

class LSAnnotationResultItem(BaseModel):
    from_name: str
    to_name: str
    type: str # e.g., "rectanglelabels"
    value: LSAnnotationResultItemValue
    score: Optional[float] = None

class LSPredictionItem(BaseModel):
    result: List[LSAnnotationResultItem]
    score: Optional[float] = None # Overall confidence for the task's prediction
    model_version: Optional[str] = None

# --- Schemas for our custom generation/suggestion endpoints ---

class ObjectGenerationRequest(BaseModel):
    source_image_path: Optional[str] = Field(None, description="Path to an existing background image, if any.")
    target_bbox: List[float] = Field(..., min_items=4, max_items=4, description="[x_min, y_min, x_max, y_max] for object placement.")
    text_prompt: str = Field(..., description="Text prompt describing the object to generate.")
    label_name_for_generated_object: str = Field(..., description="The class label to assign to the generated object.")
    project_id: int

class ObjectGenerationResponse(BaseModel):
    new_image_path: str # Path to the newly created image (will be the generated_file_path)
    annotation: Annotation # Returns the full Annotation schema for the new object

class SceneEditRequest(BaseModel):
    image_path: str
    mask_data: str
    text_prompt: str
    project_id: int

class SceneEditResponse(BaseModel):
    edited_image_path: str

class PromptSuggestionRequest(BaseModel):
    base_keyword: str
    project_id: Optional[int] = None

class PromptSuggestionResponse(BaseModel):
    suggestions: List[str]
```
