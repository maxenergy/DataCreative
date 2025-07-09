```python
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any
import logging # For logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import os # For path joining and environment variables

# This is a placeholder for actual model loading and inference.
# In a real scenario, you would load your YOLO-UniOW model here (e.g., using PyTorch).
# For now, we'll mock the inference.

# --- Configuration ---
IMAGE_BASE_DIR_INSIDE_CONTAINER = os.getenv("IMAGE_BASE_DIR", "/model_server/data/images/")
logger.info(f"YOLO Server using IMAGE_BASE_DIR: {IMAGE_BASE_DIR_INSIDE_CONTAINER}")


# --- Pydantic Models for Request and Response ---
class InferenceRequest(BaseModel):
    image_path: str # Path to the image, RELATIVE to IMAGE_BASE_DIR_INSIDE_CONTAINER
    confidence_threshold: float = 0.25

class PredictedBoundingBox(BaseModel):
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    label: str
    score: float

class InferenceResponse(BaseModel):
    predictions: List[PredictedBoundingBox]
    model_name: str = "YOLO-UniOW_Mock"
    version: str = "0.1.0"

# --- FastAPI Application ---
app = FastAPI(
    title="YOLO-UniOW Model Server",
    description="Serves the YOLO-UniOW model for object detection.",
    version="0.1.0"
)

# --- Model Loading (Placeholder) ---
# class YOLOUniOWModel:
#     def __init__(self, model_path="path/to/yolo_uniow_weights.pt"):
#         logger.info(f"Initializing YOLO-UniOW model from {model_path}...")
#         # Load your PyTorch model, set to eval mode, move to device (CPU/GPU)
#         # self.model = ...
#         # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         # self.model.to(self.device)
#         logger.info("YOLO-UniOW model initialized (mocked).")

#     def predict(self, image_path: str, confidence_threshold: float) -> List[BoundingBox]:
#         logger.info(f"Predicting on image: {image_path} with threshold: {confidence_threshold}")
#         # Actual preprocessing, inference, and postprocessing would go here
#         # For now, return mocked data
#         mock_predictions = [
#             PredictedBoundingBox(x_min=50, y_min=50, x_max=150, y_max=150, label="known_object_1", score=0.85),
#             PredictedBoundingBox(x_min=200, y_min=100, x_max=250, y_max=180, label="unknown", score=0.70),
#         ]
#         return [p for p in mock_predictions if p.score >= confidence_threshold]

# model = YOLOUniOWModel() # Instantiate the model when the server starts

@app.on_event("startup")
async def startup_event():
    # Initialize model here if it's better for your setup (e.g. with Gunicorn workers)
    logger.info("YOLO-UniOW Model Server started. Mock model active.")
    # global model
    # model = YOLOUniOWModel() # If you define model globally

@app.post("/infer", response_model=InferenceResponse, summary="Perform Object Detection")
async def infer(request: InferenceRequest = Body(...)):
    """
    Receives a RELATIVE image path and returns object detection predictions.
    The image path is joined with IMAGE_BASE_DIR_INSIDE_CONTAINER to get the absolute path.
    """
    absolute_image_path = os.path.join(IMAGE_BASE_DIR_INSIDE_CONTAINER, request.image_path)
    logger.info(f"Received inference request for relative path: {request.image_path}, resolved to: {absolute_image_path}, threshold: {request.confidence_threshold}")

    # Simulate file access check (in real scenario, you'd try to load the image)
    # For example:
    # if not os.path.exists(absolute_image_path):
    #     logger.error(f"Image not found at resolved path: {absolute_image_path}")
    #     raise HTTPException(status_code=404, detail=f"Image not found at resolved path: {absolute_image_path}")

    try:
        # In a real implementation:
        # image = Image.open(absolute_image_path) # Example using Pillow
        # results = actual_yolo_model.predict(image, conf=request.confidence_threshold)
        # predictions = format_results_to_predictedboundingbox(results)

        # Mocked prediction logic:
        if "error_test_image.jpg" in request.image_path: # Simulate an error based on relative path
            logger.error(f"Simulated processing error for image '{request.image_path}'.")
            raise ValueError("Simulated processing error for image.")

        # Example mock predictions
        raw_predictions = [
            PredictedBoundingBox(x_min=50.0, y_min=50.0, x_max=150.0, y_max=150.0, label="mock_car", score=0.92),
            PredictedBoundingBox(x_min=200.0, y_min=100.0, x_max=280.0, y_max=190.0, label="unknown", score=0.75),
            PredictedBoundingBox(x_min=10.0, y_min=10.0, x_max=40.0, y_max=40.0, label="low_score_obj", score=0.15),
        ]

        # Filter by confidence (as a real model might do, or post-process here)
        predictions = [p for p in raw_predictions if p.score >= request.confidence_threshold]

        logger.info(f"Returning {len(predictions)} predictions for {absolute_image_path}.")
        return InferenceResponse(predictions=predictions)

    except ValueError as ve: # Specific error handling
        logger.error(f"ValueError during inference for {absolute_image_path}: {ve}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(ve)) # Bad request if value error
    except Exception as e:
        logger.error(f"Generic error during inference for {absolute_image_path}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error during inference: {e}")

@app.get("/health", summary="Health Check")
async def health_check():
    # Can be expanded to check model readiness
    return {"status": "ok", "model_type": "YOLO-UniOW (Mocked)"}

if __name__ == "__main__":
    import uvicorn
    # This is mainly for local testing of this server.
    # In Docker, Uvicorn will be run as specified in the Dockerfile or docker-compose.yml.
    uvicorn.run(app, host="0.0.0.0", port=8001)
```
