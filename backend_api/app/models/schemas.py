```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- General Schemas ---
class Project(BaseModel):
    project_id: Optional[int] = None
    project_name: str
    description: Optional[str] = None
    config_json: Optional[str] = None # Label Studio labeling config

    class Config:
        orm_mode = True

class Image(BaseModel):
    image_id: Optional[int] = None
    project_id: int
    original_file_path: str
    generated_file_path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    source_image_id: Optional[int] = None
    generation_params_json: Optional[str] = None

    class Config:
        orm_mode = True

class Label(BaseModel):
    label_id: Optional[int] = None
    project_id: int
    label_name: str
    color_hex: Optional[str] = None

    class Config:
        orm_mode = True

class Annotation(BaseModel):
    annotation_id: Optional[int] = None
    image_id: int
    label_id: int
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    confidence_score: Optional[float] = None
    source_type: Optional[str] = None # 'manual', 'yolo-uniow', 'gligen_generated'
    is_unknown: Optional[bool] = False

    class Config:
        orm_mode = True


# --- API Specific Schemas (matching Label Studio ML Backend expectations where applicable) ---

# For Label Studio /predict endpoint request (simplified, actual can be more complex)
class LabelStudioTaskItem(BaseModel):
    id: int # Task ID
    data: Dict[str, Any] # Typically {"image": "url_or_path_to_image"}

class LabelStudioRequest(BaseModel):
    tasks: List[LabelStudioTaskItem]
    label_config: Optional[str] = None # XML Labeling config
    project: Optional[str] = None # Project ID from Label Studio
    params: Optional[Dict[str, Any]] = None # Other params like context

# For Label Studio /predict endpoint response
class LSAnnotationResultItemValue(BaseModel):
    # For rectanglelabels
    rectanglelabels: Optional[List[str]] = None
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    # Add other types like choices, keypoints etc. if needed
    # Example for choices:
    # choices: Optional[List[str]] = None

class LSAnnotationResultItem(BaseModel):
    from_name: str
    to_name: str
    type: str # e.g., "rectanglelabels", "choices"
    value: LSAnnotationResultItemValue
    score: Optional[float] = None # Confidence for this specific annotation item

class LSPredictionItem(BaseModel):
    result: List[LSAnnotationResultItem]
    score: Optional[float] = None # Overall confidence for the task's prediction
    model_version: Optional[str] = None
    # cluster: Optional[Any] = None # For active learning
    # neighbors: Optional[Any] = None # For active learning
    # mislabeling: Optional[float] = 0 # For active learning

# --- Schemas for our custom generation/suggestion endpoints ---

class ObjectGenerationRequest(BaseModel):
    image_path: str # Path to background image
    target_bbox: List[float] = Field(..., min_items=4, max_items=4) # [x_min, y_min, x_max, y_max]
    text_prompt: str
    project_id: int

class ObjectGenerationResponse(BaseModel):
    new_image_path: str
    annotation: Annotation # The annotation for the newly generated object

class SceneEditRequest(BaseModel):
    image_path: str
    mask_data: str # Could be path to mask image or base64 encoded mask
    text_prompt: str
    project_id: int

class SceneEditResponse(BaseModel):
    edited_image_path: str

class PromptSuggestionRequest(BaseModel):
    base_keyword: str
    project_id: Optional[int] = None # Context for suggestions

class PromptSuggestionResponse(BaseModel):
    suggestions: List[str]

```
