```python
import os
import requests # To call the FastAPI backend
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4

from label_studio_ml.model import LabelStudioMLBase
from label_studio_ml.utils import get_image_local_path, get_image_url, \
    get_label_config, DATA_UNDEFINED_NAME, is_skipped

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
# URL of your FastAPI backend's /predict endpoint
# Ensure this matches the FastAPI service name and port in docker-compose.yml and the correct endpoint path
FASTAPI_PREDICT_URL = os.getenv("FASTAPI_PREDICT_URL", "http://backend_api:8000/api/v1/predict")
# If your FastAPI backend needs an API key (good practice for security)
FASTAPI_API_KEY = os.getenv("FASTAPI_API_KEY", None) # Example: "your_secret_api_key"


class YoloPreannotationBackend(LabelStudioMLBase):
    """
    Label Studio ML Backend for YOLO-UniOW pre-annotations via a FastAPI backend.
    """

    def __init__(self, **kwargs):
        super(YoloPreannotationBackend, self).__init__(**kwargs)

        # Preload model (if any part of it is managed by this script directly)
        # For this setup, the actual model is in a separate FastAPI service.
        # This ML backend script primarily acts as a client to that service.

        # Parse labeling config to get names of <Image> and <Label> tags
        # This is important for formatting results correctly for Label Studio
        self.from_name, self.to_name, self.value, self.labels_in_config = \
            self._get_labeling_config_details()

        logger.info(f"Initialized YoloPreannotationBackend. FastAPI Predict URL: {FASTAPI_PREDICT_URL}")
        logger.info(f"Labeling Config Details: from_name={self.from_name}, to_name={self.to_name}, value={self.value}")

    def _get_labeling_config_details(self):
        """Helper to parse label config."""
        try:
            config = get_label_config(self.labeling_interface.config)
            from_name, schema = list(config.items())[0]
            to_name = schema['to_name'][0]
            value = schema['inputs'][0]['value']
            labels_in_config = set(config.get('labels_in_config', [])) # If labels are pre-defined in config
            return from_name, to_name, value, labels_in_config
        except Exception as e:
            logger.error(f"Error parsing label config: {e}. Using defaults.")
            # Fallback defaults if parsing fails, adjust as needed
            return "label", "image", "image", set()


    def predict(self, tasks: List[Dict], context: Optional[Dict] = None, **kwargs) -> List[Dict]:
        """
        Main prediction method called by Label Studio.
        :param tasks: A list of tasks to process. Each task is a dictionary.
        :param context: Optional context dictionary from Label Studio.
        :return: A list of predictions in Label Studio format.
        """
        predictions = []
        if not tasks:
            logger.info("No tasks received for prediction.")
            return predictions

        logger.info(f"Received {len(tasks)} tasks for prediction.")

        # Prepare data to send to the FastAPI backend
        # This might involve just sending task IDs or image URLs/paths
        # depending on how your FastAPI backend is designed to fetch data.

        # For this example, let's assume FastAPI backend expects a structure
        # similar to what Label Studio provides, or at least image URLs/paths.

        # The FastAPI /predict endpoint expects a schemas.LabelStudioRequest model.
        # We need to transform the tasks list into this structure.

        api_tasks: List[Dict[str, Any]] = []
        task_id_map: Dict[int, int] = {} # To map original task index to submitted task index

        for i, task in enumerate(tasks):
            # Assuming self.value holds the key for the image URL/path in task['data']
            # e.g. if LS config is <Image name="image" value="$image_url" />, self.value is "image_url"
            # However, LS usually provides data under a key like "image" or "text" directly.
            # Let's assume the key for image data is `self.value` which was parsed from config (e.g. "image")
            image_data_key = self.value
            image_url_or_path = task['data'].get(image_data_key)

            if not image_url_or_path:
                logger.warning(f"Task {task.get('id')} (index {i}) has no image data for key '{image_data_key}'. Skipping.")
                # We'll add an empty prediction later for tasks that couldn't be processed
                continue

            # The FastAPI endpoint schemas.LabelStudioRequest expects task.data to be a dict.
            # And its sub-schema schemas.LabelStudioTaskItem expects task.data.image (or the key used in from_name/to_name)
            # Ensure the data sent to FastAPI matches its expected input schema.
            # The key in task.data should be the one specified in <Image value="$key_name" />
            # For simplicity, if self.value is 'image', then task.data = {"image": image_url_or_path} is expected by FastAPI
            api_tasks.append({
                "id": task.get("id", i), # Use original task ID or index if not present
                "data": {image_data_key: image_url_or_path} # e.g. {"image": "url/path"}
            })
            task_id_map[i] = len(api_tasks) -1 # Map original task index to its index in api_tasks

        if not api_tasks:
            logger.info("No valid tasks with image data to send to backend.")
            # Return empty predictions for all original tasks
            return [{"result": [], "score": 0} for _ in tasks]

        request_payload = {
            "tasks": api_tasks,
            "label_config": self.labeling_interface.config,
            "project": str(self.project_id) if self.project_id else None, # Ensure project_id is string or None
             # "params": context # Pass context if your backend uses it
        }

        headers = {"Content-Type": "application/json"}
        if FASTAPI_API_KEY:
            headers["X-API-Key"] = FASTAPI_API_KEY

        logger.info(f"Sending request to FastAPI backend: {FASTAPI_PREDICT_URL} with {len(api_tasks)} tasks.")

        try:
            response = requests.post(FASTAPI_PREDICT_URL, json=request_payload, headers=headers, timeout=120)
            response.raise_for_status()

            backend_predictions_list = response.json() # This should be List[schemas.LSPredictionItem]

            # Reconstruct predictions list in the original order of tasks
            # and handle tasks that were skipped or failed at the backend.
            final_predictions = [{"result": [], "score": 0} for _ in tasks] # Initialize for all original tasks

            if not isinstance(backend_predictions_list, list) or len(backend_predictions_list) != len(api_tasks):
                logger.error(f"Unexpected response format or length from FastAPI. Expected list of {len(api_tasks)} items. Got: {type(backend_predictions_list)} len {len(backend_predictions_list) if isinstance(backend_predictions_list, list) else 'N/A'}")
                return final_predictions # Return initialized empty predictions

            for original_task_idx, submitted_task_idx in task_id_map.items():
                if submitted_task_idx < len(backend_predictions_list):
                    # Ensure the backend prediction matches Pydantic structure, though it's already validated by FastAPI's response_model
                    # Here we just pass it through as it should be correctly formatted by FastAPI.
                    final_predictions[original_task_idx] = backend_predictions_list[submitted_task_idx]
                else: # Should not happen if lengths match
                    logger.error(f"Mismatch in task mapping for task index {original_task_idx}")


            logger.info(f"Processed {len(final_predictions)} predictions corresponding to original tasks.")
            return final_predictions

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request to FastAPI backend failed: {e}", exc_info=True)
            return [{"result": [], "score": 0} for _ in tasks]
        except Exception as e:
            logger.error(f"An error occurred during prediction processing: {e}", exc_info=True)
            return [{"result": [], "score": 0} for _ in tasks]


    def fit(self, event, data, **kwargs):
        """
        This method is called training (fitting) model.
        Not used in this example as training is handled by a separate process/script.
        """
        logger.info("fit() method called, but not implemented in this YOLO pre-annotation backend.")
        pass

if __name__ == '__main__':
    # This part is for local testing of the ML backend script (optional)
    # It's not run when Label Studio uses the script.
    logger.info("Running YoloPreannotationBackend locally for testing (mocked).")
    # To test, you would need to simulate Label Studio's input (tasks, config).
    # Example:
    # ml_backend = YoloPreannotationBackend(project_id="1")
    # ml_backend.labeling_interface = type('obj', (object,), {
    #    'config': '<View><Image name="image" value="$image_url"/><RectangleLabels name="label" toName="image"><Label value="Car"/><Label value="Person"/></RectangleLabels></View>'
    # })
    # ml_backend.from_name, ml_backend.to_name, ml_backend.value, _ = ml_backend._get_labeling_config_details()

    # test_tasks = [{"id": 1, "data": {"image_url": "https://example.com/image1.jpg"}}]
    # preds = ml_backend.predict(test_tasks)
    # logger.info(f"Mocked local prediction: {preds}")
    pass
```
