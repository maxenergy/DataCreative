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
# URL of your FastAPI backend's /predict endpoint.
# IMPORTANT NETWORKING CONSIDERATIONS:
# - If this ML backend script is run ON THE HOST machine (e.g., using `label-studio-ml start .`):
#   And the FastAPI backend (`backend_api` service) is running in Docker with port 8000 exposed to the host,
#   then `localhost:8000` (or `127.0.0.1:8000`) should be used.
# - If this ML backend script is ALSO run as a Docker container WITHIN THE SAME Docker network as `backend_api`:
#   Then `http://backend_api:8000/...` would be correct.
# We are assuming the first case for local development and testing with `label-studio-ml start`.
FASTAPI_PREDICT_URL = os.getenv("FASTAPI_PREDICT_URL", "http://localhost:8000/api/v1/predict")

# If your FastAPI backend needs an API key (good practice for security) - currently not implemented in FastAPI
FASTAPI_API_KEY = os.getenv("FASTAPI_API_KEY", None)

# Define the assumed root directory on the HOST machine where Label Studio's local file storage is based.
# This path should correspond to what's mounted into the Docker containers at `./data/images`.
# Example: If your project root is /home/user/agile-ai-vision, then HOST_DATA_IMAGES_ROOT would be /home/user/agile-ai-vision/data/images
# It's crucial this is set correctly for local file paths to be made relative.
# For robustness, this should ideally come from an environment variable.
HOST_DATA_IMAGES_ROOT = os.getenv("HOST_DATA_IMAGES_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'images')))
logger.info(f"ML Backend using HOST_DATA_IMAGES_ROOT: {HOST_DATA_IMAGES_ROOT}")
# Ensure this path exists, or at least warn if it doesn't seem right, although the script doesn't access it directly.
if not os.path.isdir(HOST_DATA_IMAGES_ROOT) and len(HOST_DATA_IMAGES_ROOT) > 3 : # Basic check
    logger.warning(f"Configured HOST_DATA_IMAGES_ROOT '{HOST_DATA_IMAGES_ROOT}' does not exist or is not a directory. Path relativity might be incorrect for local files.")


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
            # Its sub-schema schemas.LabelStudioTaskDataItem expects a field like `image`.
            # The key in `task.data` (e.g., `task.data['image']` or `task.data['my_image_key']`)
            # is determined by the <Image value="$my_image_key" /> in Label Studio's labeling config.
            # `self.value` should hold this key (e.g., "my_image_key" or "image").

            # If Label Studio serves images from a local path (e.g., /data/upload/myimage.jpg)
            # and the ML backend script runs on the host, this path might be directly usable if
            # the FastAPI backend (in Docker) has this same path mounted as a volume from the host.
            # Example: Host's /abs/path/to/data/upload/ is mounted to Docker's /app/data/images.
            # If LS gives path /abs/path/to/data/upload/myimage.jpg, and FastAPI's IMAGE_STORAGE_BASE_PATH
            # is /app/data/images, then FastAPI needs to know how to map or expect relative paths.
            # For now, we pass the path as is. The FastAPI backend will use this path to call the
            # YOLO server, which also needs access to this path (e.g., via another shared volume).
            # This path mapping across LS <-> ML script (host) <-> FastAPI (Docker) <-> YOLO server (Docker)
            # is the most complex part of local file handling.
            # Using URLs served by Label Studio (if configured for cloud storage) simplifies this.

            # Attempt to make the path relative to HOST_DATA_IMAGES_ROOT
            # This is crucial if image_url_or_path is an absolute path from the host system.
            processed_image_path = image_url_or_path
            if os.path.isabs(image_url_or_path) and HOST_DATA_IMAGES_ROOT:
                if image_url_or_path.startswith(HOST_DATA_IMAGES_ROOT):
                    processed_image_path = os.path.relpath(image_url_or_path, HOST_DATA_IMAGES_ROOT)
                    # On Windows, relpath might produce backslashes, ensure forward slashes for cross-platform/URL compatibility
                    processed_image_path = processed_image_path.replace(os.sep, '/')
                    logger.info(f"Converted absolute path {image_url_or_path} to relative path {processed_image_path} using root {HOST_DATA_IMAGES_ROOT}")
                else:
                    logger.warning(f"Absolute path {image_url_or_path} does not start with HOST_DATA_IMAGES_ROOT {HOST_DATA_IMAGES_ROOT}. Sending path as is. This might fail in backend.")
            elif "://" in image_url_or_path: # It's a URL, pass as is. Backend needs to handle fetching.
                logger.info(f"Passing URL {image_url_or_path} as is to backend.")
                # NOTE: Current backend/YOLO server mock expects file paths, not URLs. This would need handling there.
                # For now, this test guide focuses on local file paths.
            else: # Already a relative path or a non-HTTP URL, pass as is.
                 logger.info(f"Passing path {image_url_or_path} as is (assumed relative or special scheme).")


            api_task_data = {image_data_key: processed_image_path}
            # If other data fields from the task are needed by the backend, add them here.

            api_tasks.append({
                "id": task.get("id", i),
                "data": api_task_data
            })
            task_id_map[i] = len(api_tasks) -1

        if not api_tasks:
            logger.info("No valid tasks with processable image paths to send to backend.")
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
