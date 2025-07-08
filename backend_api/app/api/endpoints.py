```python
from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Dict, Any
import httpx # For making async HTTP requests to model servers

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
    request_data: schemas.LabelStudioRequest, # Use Pydantic model for request validation
    client: httpx.AsyncClient = Depends(get_http_client)
) -> List[schemas.LSPredictionItem]:
    """
    Endpoint to receive tasks from Label Studio, pass them to an AI model (e.g., YOLO-UniOW),
    and return predictions in Label Studio format.
    """
    print(f"Received /predict request for {len(request_data.tasks)} tasks.")

    api_predictions: List[schemas.LSPredictionItem] = []

    for task in request_data.tasks:
        image_url_or_path = task.data.get("image") # Assuming 'image' is the key for image path/URL in LS task data
        if not image_url_or_path:
            print(f"Task {task.id} missing image data. Skipping.")
            api_predictions.append(schemas.LSPredictionItem(result=[])) # Empty result for this task
            continue

        # --------------------------------------------------------------------
        # TODO: Call the actual YOLO-UniOW model server
        # This section will be replaced with a real HTTP call to the model server
        # For now, using mocked response.
        # --------------------------------------------------------------------
        print(f"Simulating call to YOLO-UniOW server for task {task.id}, image: {image_url_or_path}")
        # yolo_request_payload = {"image_path": image_url_or_path, "confidence_threshold": 0.25}
        # try:
        #     response = await client.post(settings.YOLO_UNIOW_SERVER_URL, json=yolo_request_payload, timeout=30.0)
        #     response.raise_for_status()
        #     yolo_results = response.json().get("predictions", []) # Assuming this is the structure from yolo_uniow_serve.py
        # except httpx.RequestError as e:
        #     print(f"Error calling YOLO-UniOW server for task {task.id}: {e}")
        #     api_predictions.append(schemas.LSPredictionItem(result=[]))
        #     continue
        # except Exception as e: # Catch other potential errors like JSON decoding
        #     print(f"Generic error processing task {task.id} with YOLO-UniOW server: {e}")
        #     api_predictions.append(schemas.LSPredictionItem(result=[]))
        #     continue
        # --------------------------------------------------------------------

        # Call the YOLO-UniOW model server
        yolo_request_payload = {
            "image_path": image_url_or_path, # This path must be accessible by the YOLO server
                                             # (e.g., via a shared Docker volume mounted at the same path)
            "confidence_threshold": 0.2 # Example threshold, could be configurable
        }
        model_predictions = []
        model_version_str = "yolo_uniow_mock_v0.1" # Default if server call fails

        try:
            print(f"Calling YOLO server at {settings.YOLO_UNIOW_SERVER_URL} for task {task.id}")
            response = await client.post(settings.YOLO_UNIOW_SERVER_URL, json=yolo_request_payload, timeout=30.0)
            response.raise_for_status() # Raise an exception for bad status codes

            yolo_server_response = response.json()
            model_predictions = yolo_server_response.get("predictions", [])
            model_version_str = f"{yolo_server_response.get('model_name', 'yolo_uniow')}_v{yolo_server_response.get('version', 'unknown')}"
            print(f"Received {len(model_predictions)} predictions from YOLO server for task {task.id}")

        except httpx.RequestError as e:
            print(f"Error calling YOLO-UniOW server for task {task.id} (image: {image_url_or_path}): {e}")
            # Fallback to empty predictions for this task if model server call fails
            api_predictions.append(schemas.LSPredictionItem(result=[], model_version=model_version_str))
            continue
        except Exception as e: # Catch other potential errors like JSON decoding or unexpected response structure
            print(f"Generic error processing task {task.id} with YOLO-UniOW server: {e}")
            api_predictions.append(schemas.LSPredictionItem(result=[], model_version=model_version_str))
            continue


        # Determine from_name and to_name from label_config (simplified parsing)
        # A more robust parsing of label_config XML might be needed for complex configs
        from_name_found = "label" # Default or parsed
        to_name_found = "image"   # Default or parsed
        if request_data.label_config:
            if "<RectangleLabels" in request_data.label_config:
                # Simplistic way to get from_name for RectangleLabels
                try:
                    from_name_str = request_data.label_config.split('<RectangleLabels name="')[1].split('"')[0]
                    from_name_found = from_name_str
                    to_name_str = request_data.label_config.split('toName="')[1].split('"')[0]
                    to_name_found = to_name_str
                except IndexError:
                    print("Could not parse from_name/to_name from label_config, using defaults.")


        # Format model_predictions (from YOLO server) into Label Studio prediction format
        ls_results_for_task: List[schemas.LSAnnotationResultItem] = []
        if model_predictions: # Ensure there are predictions to process
            for yolo_pred in model_predictions:
                # yolo_pred is now expected to be a dict from the JSON response
                # e.g. {'x_min': 50.0, 'y_min': 50.0, 'x_max': 150.0, 'y_max': 150.0, 'label': 'mock_car', 'score': 0.92}
                ls_results_for_task.append(
                    schemas.LSAnnotationResultItem(
                        from_name=from_name_found,
                        to_name=to_name_found,
                        type="rectanglelabels",
                        value=schemas.LSAnnotationResultItemValue(
                            rectanglelabels=[yolo_pred.get("label", "unknown_label")], # Use .get for safety
                            x=yolo_pred.get("x_min", 0.0),
                            y=yolo_pred.get("y_min", 0.0),
                            width=(yolo_pred.get("x_max", 0.0) - yolo_pred.get("x_min", 0.0)),
                            height=(yolo_pred.get("y_max", 0.0) - yolo_pred.get("y_min", 0.0)),
                        ),
                        score=yolo_pred.get("score", 0.0)
                    )
                )

        api_predictions.append(schemas.LSPredictionItem(
            result=ls_results_for_task,
            score=max((res.score for res in ls_results_for_task if res.score is not None), default=0) if ls_results_for_task else 0,
            model_version=model_version_str
        ))

    return api_predictions

@router.post("/generate_object",
             response_model=schemas.ObjectGenerationResponse, # Use Pydantic for response
             summary="Generate Object in Image (GLIGEN)")
async def generate_object(
    request_data: schemas.ObjectGenerationRequest, # Use Pydantic for request
    client: httpx.AsyncClient = Depends(get_http_client)
) -> schemas.ObjectGenerationResponse:
    """
    Endpoint to generate an object in an image using GLIGEN.
    Expects: background image path, target bounding box, text prompt, project ID.
    Returns: path to new image and its annotation.
    """
    print(f"Received /generate_object request for project {request_data.project_id} on image {request_data.image_path}")

    # TODO:
    # 1. Construct payload for GLIGEN model server
    #    gligen_payload = {
    #        "image_path": request_data.image_path, # This path needs to be accessible by GLIGEN server
    #        "target_bbox": request_data.target_bbox,
    #        "text_prompt": request_data.text_prompt
    #    }
    # 2. Call GLIGEN model service using 'client' (httpx.AsyncClient)
    #    response = await client.post(settings.GLIGEN_SERVER_URL, json=gligen_payload, timeout=120.0) # Long timeout for generation
    #    response.raise_for_status()
    #    gligen_result = response.json() # e.g., {"generated_image_path_on_server": "..."}
    # 3. Process result:
    #    - If GLIGEN server saves the image, determine its path relative to IMAGE_STORAGE_BASE_PATH.
    #    - Or, if it returns image bytes, save it here.
    #    - Create an annotation entry in the database for the new object.

    # Mocked response for now
    mock_new_image_path = f"{settings.IMAGE_STORAGE_BASE_PATH}/project_{request_data.project_id}/generated/gligen_mock_{request_data.image_path.split('/')[-1]}"
    mock_annotation = schemas.Annotation(
        image_id=-1, # Placeholder, would come from DB insert of new image
        label_id=-1, # Placeholder, would come from DB lookup of label by name (derived from prompt or new label)
        x_min=request_data.target_bbox[0],
        y_min=request_data.target_bbox[1],
        x_max=request_data.target_bbox[2],
        y_max=request_data.target_bbox[3],
        source_type="gligen_generated"
    )

    print(f"Mocked GLIGEN generation. Output path: {mock_new_image_path}")
    return schemas.ObjectGenerationResponse(
        new_image_path=mock_new_image_path,
        annotation=mock_annotation
    )

@router.post("/edit_scene",
             response_model=schemas.SceneEditResponse,
             summary="Edit Scene with Inpainting (ControlNet)")
async def edit_scene(
    request_data: schemas.SceneEditRequest,
    client: httpx.AsyncClient = Depends(get_http_client)
) -> schemas.SceneEditResponse:
    """
    Endpoint to edit a scene using ControlNet for inpainting.
    Expects: background image path, mask data, text prompt, project ID.
    Returns: path to edited image.
    """
    print(f"Received /edit_scene request for project {request_data.project_id} on image {request_data.image_path}")
    # TODO: Implement call to ControlNet model service
    # controlnet_payload = { ... }
    # response = await client.post(settings.CONTROLNET_SERVER_URL, json=controlnet_payload, timeout=180.0)
    # response.raise_for_status()
    # controlnet_result = response.json()
    # 1. Save the edited image (returned as path or bytes by ControlNet server)
    # 2. Store metadata in DB (e.g., link to original image, generation params)

    # Mocked response
    mock_edited_path = f"{settings.IMAGE_STORAGE_BASE_PATH}/project_{request_data.project_id}/generated/controlnet_mock_{request_data.image_path.split('/')[-1]}"
    print(f"Mocked ControlNet edit. Output path: {mock_edited_path}")
    # This response should ideally include more info, like DB record ID of the new image.
    return schemas.SceneEditResponse(edited_image_path=mock_edited_path)

@router.post("/suggest_prompts",
             response_model=schemas.PromptSuggestionResponse,
             summary="Suggest Prompts (InternVL2)")
async def suggest_prompts(
    request_data: schemas.PromptSuggestionRequest,
    client: httpx.AsyncClient = Depends(get_http_client)
) -> schemas.PromptSuggestionResponse:
    """
    Endpoint to get prompt suggestions from InternVL2.
    Expects: base keyword, optional project ID for context.
    Returns: list of suggested prompts.
    """
    print(f"Received /suggest_prompts request for keyword: {request_data.base_keyword}")
    # TODO: Implement call to InternVL2 model service
    # internvl2_payload = {"keyword": request_data.base_keyword, "context": "..." }
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
