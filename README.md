```markdown
# Agile AI Vision Application

This project implements the "Agile AI Vision Application" as described in the technical architecture and implementation blueprint. It aims to provide a system for non-technical users to rapidly iterate on AI vision models through a "Data Flywheel" approach, integrating object detection, user-guided correction, intelligent data synthesis, and rapid model adaptation.

## Project Structure

```
 agile-ai-vision/
 │
 ├── backend_api/           # FastAPI application (Business Logic/API Layer)
 │   ├── app/
 │   │   ├── main.py         # FastAPI app instantiation
 │   │   ├── api/            # API endpoint definitions
 │   │   ├── core/           # Core logic, config
 │   │   ├── models/         # Pydantic models
 │   │   ├── services/       # Business logic services
 │   │   └── db/             # Database related modules
 │   ├── Dockerfile
 │   └── requirements.txt
 │
 ├── model_servers/         # AI Model Serving Layer components
 │   ├── yolo_uniow/         # YOLO-UniOW model server
 │   │   ├── Dockerfile
 │   │   ├── requirements.txt
 │   │   └── serve.py
 │   ├── grounding_dino/     # Placeholder
 │   ├── gligen/             # Placeholder
 │   ├── controlnet_sd3/     # Placeholder
 │   └── internvl2/          # Placeholder
 │
 ├── label_studio_ml_backend/ # Scripts for Label Studio ML Backend integration
 │   └── yolo_preannotation_backend.py
 │
 ├── data/                    # Local data storage (mounted into Docker)
 │   ├── images/
 │   ├── database/
 │   │   └── metadata.db
 │   └── label_studio_data/
 │
 ├── docs/                    # Design documents
 │   ├── prd.md
 │   └── architecture_design.md
 │
 ├── scripts/                 # Utility scripts (e.g., model fine-tuning)
 │
 ├── docker-compose.yml       # Main Docker Compose file
 ├── .env.example             # Example environment variables
 └── README.md                # This file
```

## Prerequisites

*   Docker
*   Docker Compose (usually included with Docker Desktop)
*   NVIDIA GPU and NVIDIA Docker support (if using GPU acceleration for models)

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd agile-ai-vision
    ```

2.  **Environment Variables:**
    Copy `.env.example` to `.env` and customize if necessary.
    ```bash
    cp .env.example .env
    ```
    Key variables to check:
    *   `LABEL_STUDIO_USERNAME` / `LABEL_STUDIO_PASSWORD` in `docker-compose.yml` (or configure via `.env` if you modify docker-compose to use them).
    *   The `FASTAPI_BACKEND_URL` in `label_studio_ml_backend/yolo_preannotation_backend.py` should be correctly set to where the `backend_api` service's `/predict` (or relevant endpoint) is accessible from the ML backend script's perspective. If the ML backend script is run by Label Studio *outside* the main docker-compose network (e.g., on host), this might be `http://localhost:8000/predict`. If the ML backend script is *also* a Docker container within the `agile_ai_network`, it would be `http://backend_api:8000/predict`. For now, `yolo_preannotation_backend.py` defaults to `http://backend_api:8000/api/v1/predict` which implies the FastAPI router in `main.py` should be configured with `/api/v1` prefix for its endpoints. *(Note: The current `main.py` and `endpoints.py` stubs do not yet include the `/api/v1` prefix; this will need to be added or the URL adjusted).*

3.  **Create Data Directories:**
    The `docker-compose.yml` expects certain directories under `./data/` for persistent storage. Create them if they don't exist:
    ```bash
    mkdir -p ./data/images/project_1/original ./data/images/project_1/generated
    mkdir -p ./data/database
    mkdir -p ./data/label_studio_data
    ```

4.  **Build and Run with Docker Compose:**
    ```bash
    docker-compose up --build -d
    ```
    *   `--build` forces a rebuild of images if Dockerfiles have changed.
    *   `-d` runs containers in detached mode.

5.  **Access Label Studio:**
    Open your browser and go to `http://localhost:8080`. Log in with the credentials you set (default: `admin@example.com` / `password` in `docker-compose.yml`).

6.  **Configure ML Backend in Label Studio:**
    This step requires the `yolo_preannotation_backend.py` script to be running as a server that Label Studio can connect to.
    1.  You would typically run the ML backend script using `label-studio-ml start path/to/label_studio_ml_backend/`. This script needs its `FASTAPI_BACKEND_URL` environment variable set to `http://backend_api:8000` (or `http://host.docker.internal:8000` if the ML script runs on the host and needs to reach the Dockerized `backend_api`).
    2.  In Label Studio UI (Project Settings -> Machine Learning -> Add Model), you would add the URL where the ML backend script is listening (e.g., `http://<ip_of_ml_backend_script_host>:9090`).
    *(This part of the setup needs careful handling of networking between Label Studio, the ML backend script, and the FastAPI service).*

## Development

*   **Backend API (`backend_api`):** FastAPI for business logic and communication between Label Studio and model servers.
*   **Model Servers (`model_servers/*`):** Individual FastAPI/TorchServe/etc. servers for each AI model.
*   **Label Studio ML Backend (`label_studio_ml_backend`):** Python scripts using `label-studio-ml` library to integrate with Label Studio.

### To run linters/formatters (example using ruff):
Ensure ruff is installed in your environment or run it via docker.
```bash
# For backend_api (from project root)
# ruff check backend_api/
# ruff format backend_api/
```

## Future Work (High Level)
*   Refine ML Backend integration with Label Studio within the Docker Compose setup.
*   Implement actual model loading and inference in `model_servers`.
*   Complete database schema and CRUD operations in `backend_api`.
*   Flesh out Label Studio ML backend scripts for all functionalities (generation, suggestions).
*   Develop the model fine-tuning script.
*   Add more robust error handling, logging, and testing.
*   Ensure the FastAPI router in `backend_api/app/main.py` uses a prefix like `/api/v1` and update `FASTAPI_BACKEND_URL` in `yolo_preannotation_backend.py` accordingly.
```
