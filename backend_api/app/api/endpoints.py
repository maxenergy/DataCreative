```python
from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Dict, Any, Optional
import httpx # For making async HTTP requests to model servers
import json # For serializing generation_params
from datetime import datetime # For filenames

# Assuming schemas will be defined in backend_api.app.models.schemas
from ..models import schemas
from ..core.config import settings # Import settings for model server URLs
from ..db import crud, database # Import CRUD operations and database session management

from sqlalchemy.orm import Session

router = APIRouter()

# Dependency for an async HTTP client
async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client

@router.post("/predict",
             response_model=List[schemas.LSPredictionItem],
             summary="Get AI Model Predictions (Pre-annotations)")
async def predict_annotations(
    request_data: schemas.LabelStudioRequest,
    client: httpx.AsyncClient = Depends(get_http_client),
    db: Session = Depends(database.get_db) # Inject DB session
) -> List[schemas.LSPredictionItem]:
    """
    Endpoint to receive tasks from Label Studio, pass them to an AI model (e.g., YOLO-UniOW),
    save the predictions to the database, and return predictions in Label Studio format.
    """
    print(f"Received /predict request for {len(request_data.tasks)} tasks. Project identifier: {request_data.project}")

    api_predictions_for_ls: List[schemas.LSPredictionItem] = []

    # 1. Get or Create Project
    if not request_data.project:
        raise HTTPException(status_code=400, detail="Project identifier (ID or name) is required.")

    db_project = crud.get_or_create_project(db, project_identifier=request_data.project)
    if not db_project:
        raise HTTPException(status_code=404, detail=f"Project '{request_data.project}' not found and could not be created.")

    if request_data.label_config and (not db_project.config_json or db_project.config_json != request_data.label_config) :
        db_project.config_json = request_data.label_config
        db.commit()
        db.refresh(db_project)
        print(f"Updated/set label_config for project ID {db_project.id}")


    for task in request_data.tasks:
        image_path_key = "image"
        image_url_or_path = getattr(task.data, image_path_key, None)

        if not image_url_or_path:
            print(f"Task {task.id} missing image data under key '{image_path_key}'. Skipping.")
            api_predictions_for_ls.append(schemas.LSPredictionItem(result=[]))
            continue

        db_image = crud.get_or_create_image(db, image_path=image_url_or_path, project_id=db_project.id)
        if not db_image:
             print(f"Failed to get/create image record for {image_url_or_path}. Skipping task {task.id}.")
             api_predictions_for_ls.append(schemas.LSPredictionItem(result=[]))
             continue

        yolo_request_payload = {
            "image_path": image_url_or_path,
            "confidence_threshold": 0.2
        }
        model_server_predictions = []
        model_version_str = f"yolo_uniow_mock_v0.1"

        try:
            print(f"Calling YOLO server at {settings.YOLO_UNIOW_SERVER_URL} for task {task.id}, image_id {db_image.id}")
            response = await client.post(settings.YOLO_UNIOW_SERVER_URL, json=yolo_request_payload, timeout=30.0)
            response.raise_for_status()

            yolo_server_response = response.json()
            model_server_predictions = yolo_server_response.get("predictions", [])
            model_version_str = f"{yolo_server_response.get('model_name', 'yolo_uniow')}_v{yolo_server_response.get('version', 'unknown')}"
            print(f"Received {len(model_server_predictions)} predictions from YOLO server for task {task.id}")

        except httpx.RequestError as e:
            print(f"Error calling YOLO-UniOW server for task {task.id} (image: {image_url_or_path}): {e}")
            api_predictions_for_ls.append(schemas.LSPredictionItem(result=[], model_version=model_version_str))
            continue
        except Exception as e:
            print(f"Generic error processing task {task.id} with YOLO-UniOW server: {e}")
            api_predictions_for_ls.append(schemas.LSPredictionItem(result=[], model_version=model_version_str))
            continue

        annotations_to_create: List[schemas.AnnotationCreate] = []
        if model_server_predictions:
            for pred in model_server_predictions:
                annotations_to_create.append(schemas.AnnotationCreate(
                    label_name=pred.get("label", "unknown_label"),
                    x_min=pred.get("x_min", 0.0),
                    y_min=pred.get("y_min", 0.0),
                    x_max=pred.get("x_max", 0.0),
                    y_max=pred.get("y_max", 0.0),
                    confidence_score=pred.get("score"),
                    source_type=model_version_str,
                    is_unknown=(pred.get("label", "").lower() == "unknown")
                ))

        if annotations_to_create:
            try:
                crud.create_annotation_records(db, annotations_data=annotations_to_create, image_id=db_image.id, project_id=db_project.id)
                print(f"Saved {len(annotations_to_create)} annotations to DB for image_id {db_image.id}")
            except Exception as e:
                print(f"Error saving annotations to DB for image_id {db_image.id}: {e}")

        from_name_found, to_name_found = "label", "image"
        if request_data.label_config:
            try:
                if "<RectangleLabels" in request_data.label_config:
                    from_name_found = request_data.label_config.split('<RectangleLabels name="')[1].split('"')[0]
                    to_name_found = request_data.label_config.split('toName="')[1].split('"')[0]
            except IndexError:
                print("Could not parse from_name/to_name from label_config, using defaults.")

        ls_results_for_task: List[schemas.LSAnnotationResultItem] = []
        if model_server_predictions:
            for pred in model_server_predictions:
                ls_results_for_task.append(
                    schemas.LSAnnotationResultItem(
                        from_name=from_name_found,
                        to_name=to_name_found,
                        type="rectanglelabels",
                        value=schemas.LSAnnotationResultItemValue(
                            rectanglelabels=[pred.get("label", "unknown_label")],
                            x=pred.get("x_min", 0.0),
                            y=pred.get("y_min", 0.0),
                            width=(pred.get("x_max", 0.0) - pred.get("x_min", 0.0)),
                            height=(pred.get("y_max", 0.0) - pred.get("y_min", 0.0)),
                        ),
                        score=pred.get("score")
                    )
                )

        api_predictions_for_ls.append(schemas.LSPredictionItem(
            result=ls_results_for_task,
            score=max((res.score for res in ls_results_for_task if res.score is not None), default=0) if ls_results_for_task else 0,
            model_version=model_version_str
        ))

    return api_predictions_for_ls

@router.post("/generate_object",
             response_model=schemas.ObjectGenerationResponse,
             summary="Generate Object in Image (GLIGEN)")
async def generate_object(
    request_data: schemas.ObjectGenerationRequest,
    client: httpx.AsyncClient = Depends(get_http_client),
    db: Session = Depends(database.get_db)
) -> schemas.ObjectGenerationResponse:
    """
    Endpoint to generate an object in an image (using a mock GLIGEN call).
    Saves metadata about the generated image and its annotation to the database.
    """
    print(f"Received /generate_object request for project {request_data.project_id}")

    db_project = crud.get_project(db, project_id=request_data.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail=f"Project with ID {request_data.project_id} not found.")

    source_db_image_id: Optional[int] = None
    source_image_width: Optional[int] = None
    source_image_height: Optional[int] = None
    if request_data.source_image_path:
        source_db_image = crud.get_or_create_image(db, image_path=request_data.source_image_path, project_id=db_project.id)
        source_db_image_id = source_db_image.id
        source_image_width = source_db_image.width
        source_image_height = source_db_image.height
        print(f"Using source image ID: {source_db_image_id} from path: {request_data.source_image_path}")

    base_filename = request_data.source_image_path.split('/')[-1] if request_data.source_image_path else "from_scratch"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    mock_generated_filename = f"gligen_mock_{timestamp}_{base_filename}.jpg"

    # Path where the generated image would be "saved" by the application logic
    # This is relative to the IMAGE_STORAGE_BASE_PATH
    generated_image_relative_path = f"project_{db_project.id}/generated/{mock_generated_filename}"
    # The actual generated_file_path to store in DB includes the base path for consistency if needed elsewhere,
    # but often it's better to store relative paths and prepend base path on use.
    # For this example, let's store the path as known from within the Docker volume context.
    db_generated_file_path = f"{settings.IMAGE_STORAGE_BASE_PATH}/{generated_image_relative_path}"

    print(f"Mocking GLIGEN call. Prompt: '{request_data.text_prompt}'. Label: '{request_data.label_name_for_generated_object}'")
    print(f"Mock generated image path (for DB): {db_generated_file_path}")
    # TODO: (Actual GLIGEN call)
    # gligen_payload = { "source_image_path": request_data.source_image_path,
    #                    "target_bbox": request_data.target_bbox,
    #                    "text_prompt": request_data.text_prompt }
    # response = await client.post(settings.GLIGEN_SERVER_URL, json=gligen_payload, timeout=120.0)
    # response.raise_for_status()
    # gligen_server_response = response.json()
    # actual_generated_image_path_from_gligen = gligen_server_response.get("output_image_path")
    # db_generated_file_path = actual_generated_image_path_from_gligen # Adjust based on where GLIGEN server saves it

    generation_params = {
        "prompt": request_data.text_prompt,
        "target_bbox": request_data.target_bbox,
        "model_used": "GLIGEN_mock_v0.1",
        "label_name_for_generated_object": request_data.label_name_for_generated_object
    }
    image_create_data = schemas.ImageCreate(
        project_id=db_project.id,
        original_file_path=request_data.source_image_path, # Background image
        generated_file_path=db_generated_file_path,       # New image with object
        source_image_id=source_db_image_id,
        generation_params_json=json.dumps(generation_params),
        width=source_image_width, # Assume generated image has same dimensions as source for now
        height=source_image_height
    )
    new_db_image = crud.create_image_record(db, image=image_create_data)
    print(f"Created new image record in DB with ID: {new_db_image.id} at path {new_db_image.generated_file_path}")

    db_label = crud.get_or_create_label(db, label_name=request_data.label_name_for_generated_object, project_id=db_project.id)
    print(f"Using label ID: {db_label.id} for label name: '{request_data.label_name_for_generated_object}'")

    annotation_create_data = schemas.AnnotationCreate(
        label_name=db_label.name,
        x_min=request_data.target_bbox[0],
        y_min=request_data.target_bbox[1],
        x_max=request_data.target_bbox[2],
        y_max=request_data.target_bbox[3],
        source_type=generation_params["model_used"],
        confidence_score=1.0
    )
    created_db_annotations = crud.create_annotation_records(
        db,
        annotations_data=[annotation_create_data],
        image_id=new_db_image.id,
        project_id=db_project.id
    )

    if not created_db_annotations:
        raise HTTPException(status_code=500, detail="Failed to create annotation record for the generated object.")

    db_annotation_created = created_db_annotations[0]
    print(f"Created annotation record in DB with ID: {db_annotation_created.id}")

    response_annotation = schemas.Annotation.from_orm(db_annotation_created)

    return schemas.ObjectGenerationResponse(
        new_image_path=new_db_image.generated_file_path,
        annotation=response_annotation
    )

@router.post("/edit_scene",
             response_model=schemas.SceneEditResponse,
             summary="Edit Scene with Inpainting (ControlNet)")
async def edit_scene(
    request_data: schemas.SceneEditRequest,
    client: httpx.AsyncClient = Depends(get_http_client),
    db: Session = Depends(database.get_db)
) -> schemas.SceneEditResponse:
    """
    Endpoint to edit a scene using ControlNet for inpainting.
    Expects: background image path, mask data, text prompt, project ID.
    Returns: path to edited image.
    """
    print(f"Received /edit_scene request for project {request_data.project_id} on image {request_data.image_path}")

    db_project = crud.get_project(db, project_id=request_data.project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail=f"Project {request_data.project_id} not found.")

    # TODO: Implement call to ControlNet model service
    # controlnet_payload = { ... }
    # response = await client.post(settings.CONTROLNET_SERVER_URL, json=controlnet_payload, timeout=180.0)
    # response.raise_for_status()
    # controlnet_result = response.json()
    # 1. Save the edited image (returned as path or bytes by ControlNet server) to a new file path.
    #    This new path would be similar to how generated_file_path is constructed for GLIGEN.
    # 2. Create a new Image record in DB for this edited image:
    #    - original_file_path = request_data.image_path (the image that was edited)
    #    - generated_file_path = path of the new edited image
    #    - source_image_id = ID of the original image that was edited
    #    - generation_params_json = { "prompt": request_data.text_prompt, "mask_info": "...", "model_used": "ControlNet_mock_v0.1" }
    #    - Potentially, new annotations might be relevant if objects changed class or new ones appeared. This is complex.
    #      For now, just saving the new image might be sufficient for MVP.

    # Mocked response
    base_filename = request_data.image_path.split('/')[-1]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    mock_edited_filename = f"controlnet_mock_{timestamp}_{base_filename}.jpg"
    edited_image_relative_path = f"project_{db_project.id}/generated/{mock_edited_filename}"
    db_edited_file_path = f"{settings.IMAGE_STORAGE_BASE_PATH}/{edited_image_relative_path}"

    print(f"Mocked ControlNet edit. Output path (for DB): {db_edited_file_path}")
    # This response should ideally include more info, like DB record ID of the new image.
    return schemas.SceneEditResponse(edited_image_path=db_edited_file_path)

@router.post("/suggest_prompts",
             response_model=schemas.PromptSuggestionResponse,
             summary="Suggest Prompts (InternVL2)")
async def suggest_prompts(
    request_data: schemas.PromptSuggestionRequest,
    client: httpx.AsyncClient = Depends(get_http_client),
    db: Session = Depends(database.get_db) # Added DB session if context from DB is needed
) -> schemas.PromptSuggestionResponse:
    """
    Endpoint to get prompt suggestions from InternVL2.
    Expects: base keyword, optional project ID for context.
    Returns: list of suggested prompts.
    """
    print(f"Received /suggest_prompts request for keyword: {request_data.base_keyword}")
    if request_data.project_id:
        db_project = crud.get_project(db, project_id=request_data.project_id)
        if not db_project:
            print(f"Warning: Project ID {request_data.project_id} provided for prompt suggestion but not found.")
        # else: use db_project.name or description to add context to prompt for InternVL2

    # TODO: Implement call to InternVL2 model service
    # internvl2_payload = {"keyword": request_data.base_keyword, "context": "..." } # Add project context if available
    # response = await client.post(settings.INTERNVL2_SERVER_URL, json=internvl2_payload, timeout=60.0)
    # response.raise_for_status()
    # suggestions_result = response.json() # e.g., {"suggestions": []}

    # Mocked response
    mock_suggestions = [
        f"A high-quality, photorealistic image of a {request_data.base_keyword} in a sunlit environment, 4k, detailed.",
        f"Close-up studio shot of a {request_data.base_keyword}, highly detailed, dramatic lighting.",
        f"An artistic rendering of a {request_data.base_keyword} in a surreal landscape, concept art."
    ]
    print(f"Mocked InternVL2 suggestions for '{request_data.base_keyword}'.")
    return schemas.PromptSuggestionResponse(suggestions=mock_suggestions)

@router.post("/setup", summary="ML Backend Setup/Health Check (Optional)")
async def setup_ml_backend(config: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Optional endpoint for Label Studio ML backend to send its configuration
    and for the backend to return its capabilities or model information.
    This can be used by the ML backend script on its initialization.
    """
    print(f"Received /setup request with config: {config.get('label_config')[:200]}...") # Print snippet of config
    # You could parse the label_config here if needed to adjust behavior
    # For now, just acknowledge and return basic model info
    return {
        "message": "Backend setup endpoint called successfully.",
        "model_name": "AgileAIVision_Backend",
        "capabilities": {
            "predictions": True,
            "generations": True,
            "prompt_suggestions": True
        }
    }

# TODO: Add /train endpoint later for model adaptation:
# @router.post("/train", summary="Trigger Model Adaptation/Fine-tuning")
# async def train_model(project_id: int = Body(..., embed=True)):
#     print(f"Received /train request for project_id: {project_id}")
#     # 1. Logic to gather data for the project (from DB: annotations, image paths)
#     # 2. Prepare data in the format expected by the training script
#     # 3. Trigger the training script (e.g., subprocess call, or message queue)
#     # This is a complex operation and would need careful design.
#     return {"message": f"Training process initiated for project {project_id} (mocked)."}
```
