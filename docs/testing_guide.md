```markdown
# Testing Guide: Agile AI Vision Application

This guide outlines the steps to test the core pre-annotation workflow of the Agile AI Vision Application. This involves running the Dockerized backend services, a locally hosted Label Studio ML backend script, and Label Studio itself.

## Prerequisites

*   Docker and Docker Compose installed.
*   Project cloned and you are in the root directory (`agile-ai-vision/`).
*   Python environment with `label-studio-ml` installed (for running the ML backend script locally):
    ```bash
    pip install label-studio-ml requests
    ```
*   Label Studio installed and runnable (can be a local pip install or its own Docker container if preferred, but ensure network visibility as per below). For simplicity, this guide assumes a local pip install of Label Studio for UI interaction.
    ```bash
    pip install label-studio
    ```
*   An image file (e.g., `test_image.jpg`) available on your host machine for uploading to Label Studio.

## I. Running Backend Services with Docker Compose

1.  **Ensure Docker is running.**
2.  **Host Data Directory Setup:**
    *   This project expects a shared data directory on your host machine. By default, this is `agile-ai-vision/data/images/`.
    *   Inside this directory, it's recommended to organize images by project, e.g., `agile-ai-vision/data/images/my_project_1/image1.jpg`.
    *   Create these directories if they don't exist:
        ```bash
        # From your project root (agile-ai-vision/)
        mkdir -p ./data/images/project_test/original
        mkdir -p ./data/database
        mkdir -p ./data/label_studio_data
        ```
    *   Place a test image (e.g., `cat.jpg`) into `./data/images/project_test/original/`.

3.  **Environment Variables:**
    *   Copy `.env.example` to `.env` if you haven't already: `cp .env.example .env`.
    *   **Crucially for ML Backend Script (if paths are absolute):** If your Label Studio provides absolute local file paths, and your project root `agile-ai-vision/` is, for example, at `/home/user/dev/agile-ai-vision/`, you might need to set `HOST_DATA_IMAGES_ROOT` when running the ML backend script later. The script defaults this to `../data/images` relative to its own location, which should resolve correctly if you run `label-studio-ml start` from the `agile-ai-vision` root.
        ```bash
        # Example: if your project is at /home/user/dev/agile-ai-vision
        # and you run the ML script from the project root, the default should work.
        # HOST_DATA_IMAGES_ROOT will be /home/user/dev/agile-ai-vision/data/images
        ```

4.  **Start the Dockerized services:**
    Open a terminal in the project root (`agile-ai-vision/`) and run:
    ```bash
    docker-compose up --build
    ```
    *   `--build` ensures images are rebuilt if there are changes.
    *   Do not use `-d` (detached mode) for this initial test, so you can see logs from all services (`backend_api`, `yolo_uniow_model_server`, and `label_studio` if you were running it via compose) directly in this terminal.
    *   You should see logs indicating that `backend_api` started (e.g., "Uvicorn running on http://0.0.0.0:8000") and `yolo_uniow_model_server` started (e.g., "YOLO-UniOW Model Server started. Mock model active.").
    *   The `label_studio` service defined in `docker-compose.yml` will also start. You can access its UI at `http://localhost:8080`.

## II. Running the Label Studio ML Backend Script Locally

1.  **Open a new terminal window/tab.** Navigate to the project root.
2.  **Set the `FASTAPI_PREDICT_URL` environment variable (optional, if different from default):**
    The script `label_studio_ml_backend/yolo_preannotation_backend.py` defaults to `http://localhost:8000/api/v1/predict`. This should be correct if `backend_api`'s port 8000 is exposed to your host machine by Docker.
    ```bash
    # On Linux/macOS (optional, if default is fine)
    # export FASTAPI_PREDICT_URL="http://localhost:8000/api/v1/predict"
    # On Windows (PowerShell)
    # $env:FASTAPI_PREDICT_URL="http://localhost:8000/api/v1/predict"
    ```
3.  **Start the ML backend script:**
    ```bash
    label-studio-ml start ./label_studio_ml_backend --script ./label_studio_ml_backend/yolo_preannotation_backend.py -p 9090
    ```
    *   This command tells `label-studio-ml` to serve the `YoloPreannotationBackend` class found in the specified script.
    *   It will typically run on `http://localhost:9090` (or the IP of your machine if accessed from elsewhere).
    *   You should see logs like "INFO:label_studio_ml.server: εποχές [epochs]: 0" and "INFO:label_studio_ml.server:Your server running at http://localhost:9090".
    *   You should also see: `INFO:__main__:ML Backend using HOST_DATA_IMAGES_ROOT: /path/to/your/agile-ai-vision/data/images` (the actual absolute path). Verify this path is correct.

## III. Configuring and Using Label Studio

1.  **Access Label Studio UI:** Open your browser to `http://localhost:8080` (this uses the Label Studio instance started by `docker-compose`).
    *   Log in with credentials from `docker-compose.yml` (default: `admin@example.com` / `password`).
    *   Create a new project (e.g., "Test YOLO Preannotation").

2.  **Configure Labeling Interface:**
    *   In your project, go to `Settings` -> `Labeling Interface`.
    *   Click `Browse Templates` and choose (or create) a template for **Object Detection with Bounding Boxes**.
    *   Example minimal config:
        ```xml
        <View>
          <Image name="image" value="$image_url"/>
          <RectangleLabels name="label" toName="image">
            <Label value="Car" background="green"/>
            <Label value="Person" background="blue"/>
            <Label value="Unknown" background="grey"/>
          </RectangleLabels>
        </View>
        ```
        *   **Important:** The `<Image name="image" .../>` means the ML backend script should expect image data under the key `"image"` in the task data. `yolo_preannotation_backend.py`'s `self.value` will parse to `"image"`.
        *   The `<RectangleLabels name="label" .../>` means `from_name` will be `"label"`.

4.  **Connect to the ML Backend:**
    *   In project `Settings` -> `Machine Learning`.
    *   Click `Add Model`.
    *   **Title:** "My YOLOv8 Backend" (or any title).
    *   **URL:** `http://localhost:9090` (This is where your `label-studio-ml start` script is running).
    *   Toggle "Use for interactive preannotations".
    *   Click `Validate and Save`. It should connect successfully.

5.  **Configure Data Storage (Crucial for Local Files):**
    *   In project `Settings` -> `Cloud Storage`.
    *   Click `Add Source Storage`.
    *   Choose `Local files`.
    *   **Absolute local path:** Enter the **absolute path** on your host machine to the `agile-ai-vision/data/images` directory.
        *   Example Linux/macOS: `/home/user/dev/agile-ai-vision/data/images`
        *   Example Windows: `C:\Users\user\dev\agile-ai-vision\data\images`
    *   **File filter regex:** `.*` (to sync all files) or be more specific e.g., `project_test/original/.*\.jpg`
    *   Check "Treat every bucket object as a source file".
    *   Click `Add Storage`. Then click `Sync Storage`.
    *   This makes Label Studio aware of your local image files. The paths it generates for tasks will be based on this root.

6.  **Import Data (Alternative to Syncing Cloud Storage):**
    *   If not using the "Cloud Storage" sync method above for local files, you can use the standard "Import" button.
    *   When Label Studio asks for file paths during import, or if you upload files, the paths it stores and passes to the ML backend are critical. The ML backend script's `HOST_DATA_IMAGES_ROOT` is designed to make these paths relative if they are absolute and start with that root.

7.  **Test Pre-annotation:**
    *   Open the imported image for labeling.
    *   The ML backend should be automatically queried.
    *   You should see bounding boxes predicted by the (mocked) YOLO server appear on the image. These will be "mock_car" and "unknown" based on current mock logic.

## IV. What to Check

1.  **Label Studio ML Backend Script Logs (Terminal 2):**
    *   Look for lines indicating it received tasks (e.g., "Received 1 tasks for prediction.").
    *   Check for logs about sending requests to `http://localhost:8000/api/v1/predict`.
    *   Crucially, check logs like:
        *   `INFO:__main__:Initialized YoloPreannotationBackend. FastAPI Predict URL: http://localhost:8000/api/v1/predict`
        *   `INFO:__main__:ML Backend using HOST_DATA_IMAGES_ROOT: /actual/path/to/agile-ai-vision/data/images`
        *   `INFO:__main__:Converted absolute path /actual/path/to/agile-ai-vision/data/images/project_test/original/cat.jpg to relative path project_test/original/cat.jpg ...` (or similar, depending on how LS provides the path).
        *   `INFO:__main__:Sending request to FastAPI backend: ... with data: {'image': 'project_test/original/cat.jpg'}` (or similar relative path).
    *   Look for logs about receiving predictions from FastAPI and any potential errors.

2.  **Docker Compose Logs (Terminal 1 - `backend_api` service):**
    *   Look for logs from `uvicorn` indicating a POST request to `/api/v1/predict`.
    *   Example: `INFO:     172.19.0.1:0 - "POST /api/v1/predict HTTP/1.1" 200 OK`
    *   Check for print statements like "Received /predict request for 1 tasks. Project identifier: <your_project_id_or_name>".
    *   The `image_url_or_path` logged here should be the *relative path* (e.g., `project_test/original/cat.jpg`).
    *   Look for "Calling YOLO server..." with the same relative path.
    *   Check for database interaction logs.

3.  **Docker Compose Logs (Terminal 1 - `yolo_uniow_model_server` service):**
    *   Look for logs indicating a POST request to its `/infer` endpoint.
    *   Example: `INFO:     172.20.0.3:50884 - "POST /infer HTTP/1.1" 200 OK` (IP will be `backend_api`'s Docker IP)
    *   Check for `INFO:__main__:Received inference request for relative path: project_test/original/cat.jpg, resolved to: /model_server/data/images/project_test/original/cat.jpg ...`. This confirms the YOLO server correctly reconstructs the absolute path inside its container.
    *   Check for "Returning ... predictions...".

4.  **Database Check (Optional, more advanced):**
    *   You can connect to the SQLite database (`agile-ai-vision/data/database/metadata.db`) using a tool like DB Browser for SQLite.
    *   Check the `projects`, `images`, `labels`, and `annotations` tables for new entries corresponding to your test.

## Troubleshooting Common Issues

*   **Networking:**
    *   "Connection refused" when ML backend script tries to call FastAPI: Ensure `backend_api` port 8000 is correctly exposed in `docker-compose.yml` (`ports: - "8000:8000"`) and `FASTAPI_PREDICT_URL` is `http://localhost:8000/...`.
    *   "Connection refused" when FastAPI tries to call `yolo_uniow_model_server`: Ensure service names and ports in `YOLO_UNIOW_SERVER_URL` (`http://yolo_uniow_model_server:8001/infer`) match `docker-compose.yml`. Services in the same Docker network can reach each other by service name.
*   **Image Paths:** If using local file storage in Label Studio, the paths provided in tasks must be resolvable by the `backend_api` and subsequently by the `yolo_uniow_model_server`. This often requires careful volume mounting in `docker-compose.yml` so that a path like `/data/my_image.jpg` on the host maps to the *same path* or a *predictably translatable path* inside all relevant containers. For initial tests, using image URLs (if LS is configured to serve them or from cloud storage) or ensuring very simple, consistent mount points is easiest. The current setup mounts `./data/images` from host to `/app/data/images` in `backend_api` and `/model_server/data/images` in `yolo_uniow_model_server`. This path difference means `image_url_or_path` passed from `backend_api` to `yolo_uniow_model_server` would need translation if it's an absolute path from `backend_api`'s perspective.
    *   **Simplification for Test:** The guide now emphasizes setting up Label Studio "Local files" source storage with an absolute path to `agile-ai-vision/data/images` on the host. The ML backend script then attempts to make paths relative to `HOST_DATA_IMAGES_ROOT`. This relative path (e.g., `project_test/original/cat.jpg`) is what `backend_api` receives and passes to `yolo_uniow_model_server`. The `yolo_uniow_model_server` then prepends its internal `IMAGE_BASE_DIR` (e.g., `/model_server/data/images/`) to this relative path. This chain should work if all components' base paths correctly map to the host's `./data/images` via Docker volumes.
*   **JSON Formatting/Pydantic Errors:** Check logs for Pydantic validation errors if the structure of data sent or received doesn't match schemas.
```
