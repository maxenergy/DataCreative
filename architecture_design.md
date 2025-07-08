```markdown
# Architecture Design Document: Agile AI Vision Application

## 1. Introduction

### 1.1. Purpose of this Document
This document provides a comprehensive architectural overview of the Agile AI Vision Application. It details the system's components, their interactions, data flows, technology stack, and deployment strategy. This document is intended for software engineers, system architects, and technical stakeholders involved in the development, deployment, and maintenance of the system.

### 1.2. Scope
The scope of this architecture document covers all major components of the system, including the user interface, application server, business logic/API layer, AI model serving infrastructure, and data persistence mechanisms, as outlined in the source "敏捷AI视觉应用" whitepaper.

### 1.3. Goals and Non-Goals of the Architecture
**Goals:**
*   **Modularity:** Design components that are loosely coupled and can be developed, deployed, and scaled independently.
*   **User-Centricity:** Prioritize ease of use for non-technical users through the Label Studio interface and streamlined workflows.
*   **Extensibility:** Allow for the future integration of new AI models, data sources, and functionalities.
*   **Rapid Iteration Support:** The architecture must inherently support the "Data Flywheel" concept, enabling quick updates to models based on user feedback and generated data.
*   **Local First Deployment:** Fulfill the initial requirement for local file system storage and operation, while paving the way for potential future cloud scalability.

**Non-Goals (for initial MVP/Phases):**
*   Achieving web-scale scalability with millions of concurrent users.
*   Providing a fully managed cloud service.
*   Advanced, enterprise-grade security features beyond standard practices for local deployments.
*   Real-time, multi-user collaborative editing beyond Label Studio's native capabilities.

### 1.4. References
*   Product Requirements Document: Agile AI Vision Application (`prd.md`)
*   Source Document: "面向非技术用户的敏捷AI视觉应用：技术架构与实施蓝图" (referred to as "Source Whitepaper")

### 1.5. Definitions and Acronyms
*   **AI:** Artificial Intelligence
*   **API:** Application Programming Interface
*   **CVAT:** Computer Vision Annotation Tool
*   **GLIGEN:** Grounded-Language-to-Image Generation
*   **KPI:** Key Performance Indicator
*   **LMM:** Large Multimodal Model
*   **mAP:** mean Average Precision
*   **ML:** Machine Learning
*   **MVP:** Minimum Viable Product
*   **OVD:** Open Vocabulary Object Detection
*   **OWOD:** Open World Object Detection
*   **PRD:** Product Requirements Document
*   **SD3:** Stable Diffusion 3
*   **UI:** User Interface
*   **FS:** File System

## 2. System Overview

### 2.1. Architectural Vision (Reiteration of the Data Flywheel)
The core architectural vision is to realize the "Data Flywheel" concept described in the Source Whitepaper (Part 1.2). This entails a closed-loop system where:
1.  **Detection & Gap Identification:** AI models (primarily YOLO-UniOW) process images, identifying known objects and flagging unknowns.
2.  **User-Guided Correction & Augmentation:** Non-technical users correct errors and initiate data generation via Label Studio.
3.  **Intelligent Data Synthesis:** Generative AI models (GLIGEN, ControlNet) create new, annotated data based on user input.
4.  **Rapid Model Adaptation:** Corrected and synthesized data are used to quickly fine-tune AI models, enhancing their performance for the next cycle.
This iterative process, orchestrated through a user-friendly interface, aims to continuously improve model accuracy and adapt to new requirements with minimal friction.

### 2.2. High-Level Architecture Diagram
The system follows a layered architecture, as depicted in Figure 5.1 of the Source Whitepaper.

*(Placeholder for re-creating or referencing Figure 5.1: End-to-end system architecture图)*
*   **Presentation Layer:** User's Web Browser (Label Studio Frontend)
*   **Application Layer:** Label Studio Server (with ML Backend)
*   **Business Logic/API Layer:** Python FastAPI Service
*   **Model Serving Layer:** Dedicated AI Model Inference Servers (e.g., Triton, TorchServe, Custom)
*   **Data Persistence Layer:** Local File System + SQLite

### 2.3. Key Architectural Principles
*   **Separation of Concerns:** Each layer and component has distinct responsibilities. For example, Label Studio handles UI and annotation workflow, FastAPI handles API requests and business logic, and model servers handle computationally intensive AI inference.
*   **API-Driven Communication:** Interactions between layers (e.g., Label Studio ML Backend to FastAPI, FastAPI to Model Servers) are managed through well-defined APIs.
*   **Modularity for AI Models:** AI models are treated as interchangeable components within the Model Serving Layer, allowing for updates or replacements with minimal impact on other parts of the system.
*   **User Experience Prioritization:** The choice of Label Studio and the design of interaction workflows are geared towards non-technical users.
*   **Pragmatic Local Deployment:** The initial design focuses on a Docker-compose based local deployment to meet user requirements, using local file systems and SQLite for simplicity and ease of setup.
*   **Designed for Extensibility:** While starting local, the architecture anticipates future needs for scalability by abstracting data access and separating model serving, which could be scaled or moved to the cloud.

## 3. Layered Architecture (Detailed from Part 5.1 of Source Whitepaper)

### 3.1. Presentation Layer (Label Studio Front-end)
*   **Responsibilities:**
    *   Provides the primary graphical user interface (GUI) for all user interactions.
    *   Renders images, annotations (bounding boxes, labels), and model suggestions.
    *   Captures user inputs for annotation, correction, data generation triggers, and prompt formulation.
    *   Initiates requests to the Application Layer (Label Studio Server) for backend processing.
*   **Key Technologies:** Standard web technologies (HTML, CSS, JavaScript) as part of the Label Studio front-end application.
*   **User Interaction Points for AI Features:**
    *   Viewing pre-annotations from YOLO-UniOW.
    *   Correcting/labeling "unknown" objects.
    *   Defining new class labels.
    *   Buttons/forms to trigger GLIGEN object generation (specifying location and prompt).
    *   Buttons/forms to trigger ControlNet scene editing (specifying mask and prompt).
    *   Interface elements to request and select prompt suggestions from InternVL2.

### 3.2. Application Layer (Label Studio Server + ML Backend)
*   **Responsibilities:**
    *   Manages user accounts, projects, tasks, and data within Label Studio.
    *   Orchestrates the overall annotation and data iteration workflow.
    *   Serves the Label Studio front-end to the user's browser.
    *   Crucially, its **ML Backend** component acts as a bridge, forwarding requests from the UI that require AI processing to the Business Logic/API Layer and returning results.
*   **Key Technologies:** Label Studio application (Python-based), Label Studio ML Backend SDK/API.

### 3.3. Business Logic / API Layer (Python FastAPI Service)
*   **Responsibilities:**
    *   Exposes a set of RESTful API endpoints that the Label Studio ML Backend consumes.
    *   Receives requests from Label Studio (e.g., for pre-annotation, image generation).
    *   Validates and processes these requests.
    *   Intelligently routes requests to the appropriate AI model(s) in the Model Serving Layer.
    *   Handles interactions with the Data Persistence Layer for creating, reading, updating, and deleting metadata (e.g., storing new annotations, paths to generated images).
    *   Formats responses (e.g., annotation data, generated image paths, prompt suggestions) to be sent back to Label Studio.
*   **Key Technologies:** Python 3.10+, FastAPI framework for building high-performance APIs, Pydantic for data validation.
*   **Core API Endpoint Categories:** (Details in Section 6)
    *   Prediction/Pre-annotation endpoints.
    *   Data generation endpoints (object植入, scene editing).
    *   Prompt assistance endpoints.
    *   (Future) Model training/adaptation trigger endpoints.

### 3.4. Model Serving Layer
*   **Responsibilities:**
    *   Hosts and manages the lifecycle of all AI models.
    *   Provides high-performance inference services for the AI models.
    *   Exposes internal API endpoints (e.g., HTTP or gRPC) that the Business Logic/API Layer can call to get predictions or generated content from the models.
    *   Handles model-specific pre-processing and post-processing of data if not covered by the FastAPI layer.
*   **Key Technologies:**
    *   Options include NVIDIA Triton Inference Server, TorchServe, or custom Python-based model servers (e.g., using Flask/FastAPI with `diffusers` library for generative models). The choice may depend on the specific model and performance requirements.
    *   Docker for containerizing each model service.
*   **Deployment Strategy for Models:** Each AI model (or closely related group of models) will be packaged as a separate Docker container/service, allowing for independent scaling, updating, and resource allocation.

### 3.5. Data Persistence Layer
*   **Responsibilities:**
    *   Stores all persistent data required by the application.
*   **Image Storage (Local File System):**
    *   **Technology:** User's local file system.
    *   **Content:** Original uploaded images, synthetically generated images.
    *   **Structure:** A well-defined directory structure (e.g., per project, with subfolders for originals and generated).
*   **Metadata Storage (SQLite):**
    *   **Technology:** SQLite database.
    *   **Content:** File paths to images, annotation data (bounding box coordinates, class labels, source of annotation), project configurations, user information (if managed by Label Studio), label schemas.
    *   **Rationale:** Lightweight, file-based, easy to set up for local deployments, and adequate for MVP and small to medium-sized projects.
*   **Data Access Abstraction (Design Consideration):**
    *   The Business Logic/API Layer should interact with the data stores (FS and SQLite) through an abstracted Data Access Layer (DAL). This means specific file system paths or SQL queries are encapsulated within this DAL.
    *   **Benefit:** This design significantly simplifies future migration to alternative storage solutions (e.g., cloud object storage like AWS S3, and managed databases like PostgreSQL or MySQL) by localizing the necessary code changes to the DAL, rather than requiring modifications throughout the Business Logic Layer. Label Studio itself also supports cloud storage, which would facilitate such a transition.

## 4. Component Deep Dive: AI Models (Hosted in Model Serving Layer)
This section details the specific AI models chosen for the system, their roles, and key features leveraged, as primarily discussed in Part 2 and 3 of the Source Whitepaper. Each model will be served as a distinct service within the Model Serving Layer.

### 4.1. Real-time Detection: YOLO-UniOW
*   **Role in System:** Primary engine for real-time, interactive object detection and pre-annotation directly within the user interface. It is the first model to process user-uploaded images.
*   **Key Features Leveraged:**
    *   **High Efficiency & Speed:** Suitable for immediate feedback in interactive web applications (Targeting ~64.8 FPS for YOLO-UniOW-L on A100, per Source Whitepaper Table 2.1).
    *   **Open Vocabulary Detection (OVD):** Allows detection of object categories defined dynamically by user text prompts.
    *   **"通配符学习" (Wildcard Learning - OWOD):** Crucially, it can identify objects not belonging to any known vocabulary as "unknown," proactively highlighting potential new categories or missed detections. This directly supports the "Detect & Identify Gaps" phase of the Data Flywheel and simplifies user workflow from "search for errors" to "review suggestions."
*   **Integration:** Called by the FastAPI backend when Label Studio requests pre-annotations for a new image. Returns bounding boxes, class labels (if known), and "unknown" tags.

### 4.2. High-Accuracy Detection: Grounding DINO
*   **Role in System:** Serves as a high-precision, offline analysis tool. Used when accuracy is more critical than real-time speed.
*   **Key Features Leveraged:**
    *   **State-of-the-Art Zero-Shot Accuracy:** Provides highly accurate localization and classification based on text prompts, even for objects not seen during its COCO training (Source Whitepaper Sec 2.2).
    *   **Deep Visual-Language Fusion:** Enables precise understanding of text-image relationships.
*   **Integration:**
    *   Can be used by the FastAPI backend for batch processing tasks (not directly user-facing in real-time).
    *   Potentially used as a "precision locator" to provide accurate bounding boxes as input/conditioning for the GLIGEN generation model, ensuring generated objects are placed precisely.

### 4.3. Object植入式生成 (Object In-place Generation): GLIGEN
*   **Role in System:** Enables users to add new objects to existing images or backgrounds by specifying a location (bounding box) and a textual description. Core to "从零生成" (generate from scratch) and "增量生成" (incremental generation) for data augmentation.
*   **Key Features Leveraged:**
    *   **Grounded Generation:** Generates objects conditioned on both text prompts and spatial location (bounding box) inputs.
    *   **Leverages Pre-trained Diffusion Models (e.g., Stable Diffusion):** Builds upon strong existing generative capabilities, freezing their weights and adding trainable Gated Self-Attention layers for control.
*   **Integration:** Called by the FastAPI backend when a user initiates an "object植入" task from Label Studio. Receives background image, bounding box coordinates, and text prompt. Returns the new image with the generated object, and the FastAPI service will also record the new annotation.

### 4.4. Scene-Aware Repair/Inpainting: ControlNet + SD3 (Stable Diffusion 3)
*   **Role in System:** Provides advanced capabilities for more complex image editing, such as seamlessly replacing objects or modifying regions while maintaining overall scene consistency (lighting, perspective). Used for "修正模型漏检错检" (correcting model false positives/negatives) in complex ways.
*   **Key Features Leveraged:**
    *   **Conditional Inpainting:** Modifies user-defined masked regions based on textual prompts.
    *   **Spatial Condition Control:** Utilizes control signals (e.g., depth maps, Canny edges extracted from the original image) to ensure the generated content aligns realistically with the surrounding scene structure and geometry. SD3 integration enhances this capability.
*   **Integration:** Called by the FastAPI backend when a user initiates an "edit scene" or "inpaint" task. Receives original image, mask, text prompt, and potentially control images (like a depth map automatically extracted by the backend). Returns the modified image.

### 4.5. Prompt Assistance: InternVL2
*   **Role in System:** Acts as a "提示词副驾驶" (Prompt Co-pilot) to help non-technical users formulate effective and diverse textual prompts for the generative models (GLIGEN, ControlNet).
*   **Key Features Leveraged:**
    *   **Advanced Text Generation:** Capable of understanding simple user inputs (e.g., a basic category name like "安全帽") and expanding them into a set of rich, descriptive prompt templates.
    *   **Large Knowledge Base (from LMM pre-training):** Can generate varied prompts covering different styles, contexts, and attributes for the desired object/scene.
*   **Integration:** Called by the FastAPI backend when a user requests prompt suggestions within the generation workflow in Label Studio. Receives a basic concept/keyword from the user. Returns a list of suggested, more detailed prompts.

## 5. Data Models and Schemas
This section will detail the structure of data as it's stored and transferred within the system.

### 5.1. Image Metadata (SQLite Schema - Preliminary)
The SQLite database will store metadata. Below is a preliminary schema design.

*   **Projects Table:**
    *   `project_id` (INTEGER, Primary Key, Autoincrement)
    *   `project_name` (TEXT, Not Null, Unique)
    *   `description` (TEXT)
    *   `creation_date` (TIMESTAMP, Default CURRENT_TIMESTAMP)
    *   `config_json` (TEXT)  -- Stores Label Studio labeling config, etc.

*   **Images Table:**
    *   `image_id` (INTEGER, Primary Key, Autoincrement)
    *   `project_id` (INTEGER, Foreign Key to Projects)
    *   `original_file_path` (TEXT, Not Null) -- Path in the local FS
    *   `generated_file_path` (TEXT, Nullable) -- Path if this is an AI-generated image
    *   `width` (INTEGER)
    *   `height` (INTEGER)
    *   `upload_date` (TIMESTAMP, Default CURRENT_TIMESTAMP)
    *   `source_image_id` (INTEGER, Foreign Key to Images, Nullable) -- If generated, links to base image
    *   `generation_params_json` (TEXT, Nullable) -- Prompt, model used for generation

*   **Labels Table (Object Categories):**
    *   `label_id` (INTEGER, Primary Key, Autoincrement)
    *   `project_id` (INTEGER, Foreign Key to Projects)
    *   `label_name` (TEXT, Not Null)
    *   `color_hex` (TEXT) -- Optional, for UI display
    *   UNIQUE (`project_id`, `label_name`)

*   **Annotations Table (Bounding Boxes):**
    *   `annotation_id` (INTEGER, Primary Key, Autoincrement)
    *   `image_id` (INTEGER, Foreign Key to Images)
    *   `label_id` (INTEGER, Foreign Key to Labels)
    *   `x_min` (REAL, Not Null) -- Bounding box coordinate (normalized or absolute)
    *   `y_min` (REAL, Not Null)
    *   `x_max` (REAL, Not Null)
    *   `y_max` (REAL, Not Null)
    *   `confidence_score` (REAL, Nullable) -- If from AI model
    *   `source_type` (TEXT) -- e.g., 'manual', 'yolo-uniow', 'gligen_generated', 'grounding_dino'
    *   `is_unknown` (BOOLEAN, Default FALSE) -- If flagged as 'unknown' by OWOD model
    *   `creation_date` (TIMESTAMP, Default CURRENT_TIMESTAMP)
    *   `last_modified_date` (TIMESTAMP)

### 5.2. Data Structures for API Communication (Pydantic Models for FastAPI)
FastAPI will use Pydantic models for request and response validation and serialization. Examples:

*   **`ImageUploadRequest`**: May contain file metadata, project ID.
*   **`PredictionRequest`**: Contains image ID or path, project ID (to get relevant labels).
*   **`BoundingBox`**: `x_min, y_min, x_max, y_max, label_name, confidence_score`.
*   **`PredictionResponse`**: List of `BoundingBox` objects.
*   **`ObjectGenerationRequest`**: `base_image_id, target_bbox, text_prompt, project_id`.
*   **`ObjectGenerationResponse`**: `new_image_path, generated_bbox_annotation`.
*   **`SceneEditRequest`**: `base_image_id, mask_image_path_or_data, text_prompt, project_id`.
*   **`SceneEditResponse`**: `edited_image_path`.
*   **`PromptSuggestionRequest`**: `base_keyword, project_id`.
*   **`PromptSuggestionResponse`**: List of suggested prompts.

These will be defined in detail within the FastAPI application code.

## 6. API Specifications (FastAPI Backend)
The FastAPI service will expose endpoints for the Label Studio ML Backend. All interactions are initiated by Label Studio calling these endpoints.

### 6.1. ML Backend API for Label Studio

*   **`POST /predict` (for pre-annotation with YOLO-UniOW)**
    *   **Request Body:** `PredictionRequest` (e.g., list of tasks/images, labeling config from LS).
    *   **Response Body:** List of predictions in Label Studio format. Each prediction contains bounding boxes with labels (or "unknown").
    *   **Action:** Retrieves image(s), sends to YOLO-UniOW service, formats results.

*   **`POST /generate_object` (for GLIGEN)**
    *   **Request Body:** `ObjectGenerationRequest` (containing background image path/ID, user-drawn bounding box for placement, text prompt, project ID).
    *   **Response Body:** `ObjectGenerationResponse` (path to the newly generated image, and its annotation).
    *   **Action:** Retrieves background, calls GLIGEN service, saves new image, stores metadata and annotation in DB.

*   **`POST /edit_scene` (for ControlNet)**
    *   **Request Body:** `SceneEditRequest` (background image path/ID, mask, text prompt, project ID).
    *   **Response Body:** `SceneEditResponse` (path to the edited image).
    *   **Action:** Retrieves image, (optionally extracts control map like depth), calls ControlNet service, saves new image, stores metadata. (Annotation might need user review).

*   **`POST /suggest_prompts` (for InternVL2)**
    *   **Request Body:** `PromptSuggestionRequest` (user's basic keyword/concept, project ID).
    *   **Response Body:** `PromptSuggestionResponse` (list of detailed prompt strings).
    *   **Action:** Calls InternVL2 service with the keyword.

*   **`POST /setup` (ML Backend initial handshake - optional but good practice)**
    *   **Request Body:** Labeling configuration from Label Studio.
    *   **Response Body:** Model information (e.g., available labels if the model is already trained, though for OVD it's dynamic).
    *   **Action:** Initialize or validate model state based on LS project config.

*   **`POST /train` (to trigger model adaptation - simplified for MVP)**
    *   **Request Body:** Could be as simple as a project ID or a signal to use all new data.
    *   **Response Body:** Status message (e.g., "Training initiated").
    *   **Action (MVP):** Triggers a script that prepares data from SQLite and local FS for the specified project and starts a fine-tuning process for YOLO-UniOW.
    *   **Action (Future):** More sophisticated data selection, versioning, and tracking.

### 6.2. Internal API Endpoints
The FastAPI service itself will call internal APIs exposed by the individual model servers in the Model Serving Layer. These are not directly exposed to Label Studio. For example:
*   YOLO-UniOW service might have a `/infer` endpoint.
*   GLIGEN service might have a `/generate` endpoint.
These will be simple HTTP endpoints, likely also using FastAPI or Flask if custom-built.

## 7. Data Flow Scenarios (Detailed from Part 5.2 of Source Whitepaper)

### 7.1. Scenario A: Correcting a Missed Detection / Unknown Object
1.  **Upload & Pre-annotation Request (User -> LS Frontend -> LS Server -> FastAPI):**
    *   User uploads `image_A.jpg` to Project `P1` in Label Studio.
    *   LS Frontend sends `image_A.jpg` and `P1` info to LS Server.
    *   LS Server's ML Backend calls FastAPI's `/predict` endpoint with `image_A.jpg` data and `P1`'s labeling config.
2.  **Detection (FastAPI -> YOLO-UniOW Service -> FastAPI):**
    *   FastAPI service receives the request. It prepares the image and calls the YOLO-UniOW model service (hosted in Model Serving Layer).
    *   YOLO-UniOW processes `image_A.jpg`. It detects known object `Obj1` and an "unknown" object `Unk1`.
    *   YOLO-UniOW service returns `[{bbox_Obj1, label_Obj1}, {bbox_Unk1, label_unknown}]` to FastAPI.
3.  **Pre-annotation Response (FastAPI -> LS Server -> LS Frontend -> User):**
    *   FastAPI formats these results into Label Studio's expected prediction format.
    *   FastAPI returns the formatted predictions to LS Server's ML Backend.
    *   LS Server passes results to LS Frontend.
    *   User sees `image_A.jpg` with a box around `Obj1` (labeled `label_Obj1`) and a box around `Unk1` (labeled "unknown").
4.  **User Correction & Save (User -> LS Frontend -> LS Server -> FastAPI):**
    *   User inspects `Unk1`. It's actually a "新型号传感器" (New Model Sensor).
    *   User changes the label of `bbox_Unk1` from "unknown" to "新型号传感器" (this might involve adding "新型号传感器" to the project's label config if it's new). User clicks "Save" or "Submit" in Label Studio.
    *   LS Frontend sends the updated annotation task (with `image_A.jpg`, `bbox_Unk1`, and new label "新型号传感器") to LS Server.
5.  **Data Persistence (LS Server -> FastAPI -> SQLite/FS):**
    *   LS Server (on task completion/submission) sends the final annotations to a persistence endpoint in FastAPI (or FastAPI infers changes based on prediction ID and user actions if LS ML backend supports this feedback loop directly).
    *   FastAPI service updates/creates an annotation record in the SQLite `Annotations` table for `image_A.jpg`, linking `bbox_Unk1` to the "新型号传感器" label. The `is_unknown` flag is set to `FALSE`, and `source_type` might be updated to 'manual_correction_of_unknown'.

### 7.2. Scenario B: Adding a New Category with Generative Augmentation
1.  **Define New Category (User -> LS Frontend -> LS Server):**
    *   User adds "蓝色小部件" (Blue Widget) to Project `P2`'s label configuration in Label Studio.
2.  **Initiate Generation (User -> LS Frontend):**
    *   User uploads `background_B.jpg` to `P2`.
    *   User clicks a custom "Generate Object" button in the Label Studio interface for `background_B.jpg`.
3.  **Provide Parameters & Prompt Assistance (User -> LS Frontend -> LS Server -> FastAPI -> InternVL2 -> ... -> User):**
    *   A dialog appears in LS Frontend. User draws a bounding box (`target_bbox`) on `background_B.jpg`.
    *   User initially types "blue widget" as a prompt.
    *   User clicks "Get Prompt Suggestions."
        *   LS Frontend sends "blue widget" via LS Server's ML Backend to FastAPI's `/suggest_prompts` endpoint.
        *   FastAPI calls the InternVL2 model service.
        *   InternVL2 returns a list like ["a glossy blue cylindrical widget", "a small matte blue widget with metallic flecks"].
        *   FastAPI forwards this list back to LS Frontend.
    *   User selects "a glossy blue cylindrical widget" as the final prompt.
4.  **Generation Request (LS Frontend -> LS Server -> FastAPI):**
    *   User confirms. LS Frontend sends `background_B.jpg` data, `target_bbox`, and the chosen prompt to LS Server.
    *   LS Server's ML Backend calls FastAPI's `/generate_object` endpoint.
5.  **Object Generation (FastAPI -> GLIGEN Service -> FastAPI):**
    *   FastAPI receives the request. It calls the GLIGEN model service with `background_B.jpg`, `target_bbox`, and the prompt.
    *   GLIGEN service generates `generated_C.jpg` containing the blue widget in the specified location.
    *   GLIGEN service returns the path/data of `generated_C.jpg` to FastAPI.
6.  **Data Persistence & Response (FastAPI -> SQLite/FS; FastAPI -> LS Server -> LS Frontend -> User):**
    *   FastAPI saves `generated_C.jpg` to the local file system (e.g., under `P2/generated/`).
    *   FastAPI creates new records in SQLite:
        *   An entry in `Images` for `generated_C.jpg` (linking to `background_B.jpg` as source).
        *   An entry in `Annotations` for `generated_C.jpg`, with `target_bbox` and the label "蓝色小部件", `source_type` = 'gligen_generated'.
    *   FastAPI returns the path to `generated_C.jpg` and its annotation to LS Server's ML Backend.
    *   LS Server could then make this new image available in the project, possibly as a new task with the annotation already applied, for user review or inclusion in the next training round.

## 8. Technology Stack Summary (From Part 5.3 of Source Whitepaper)

| Component             | Technology Chosen        | Reason                                                                                    |
|-----------------------|--------------------------|-------------------------------------------------------------------------------------------|
| **Annot. Interface/Orchestrator** | Label Studio             | Excellent ML integration (ML Backend), modern UI, open-source.                            |
| **Application Backend (API Layer)** | Python 3.10+, FastAPI    | High performance, modern async framework, easy REST API development, Pydantic validation. |
| **Real-time Detection Model** | YOLO-UniOW               | SOTA speed, revolutionary "Wildcard Learning" for unknown objects.                      |
| **High-Accuracy Detection Model** | Grounding DINO           | SOTA precision, vital for high-quality localization (e.g., for GLIGEN).                 |
| **Object Generation Model** | GLIGEN                   | Specialized in grounded/localized object generation based on bbox and text.             |
| **Scene Editing Model** | ControlNet for SD3       | Flexible scene editing with strong spatial control, enhanced by SD3 capabilities.         |
| **Prompt Assistance Model** | InternVL2                | Powerful open-source LMM for generating diverse, high-quality text prompts.             |
| **Data Storage (Images)** | Local File System        | Meets direct user requirement for local storage.                                          |
| **Data Storage (Metadata)** | SQLite                   | Lightweight, file-based, sufficient for MVP and local metadata management.                |
| **Deployment Solution** | Docker / Docker Compose  | Simplifies packaging, deployment, management of all microservices; ensures consistency.   |
| **Core ML Libraries**   | PyTorch, Diffusers, Transformers | Foundational libraries for running and serving the selected AI models.                    |

## 9. Deployment Architecture (From Part 5.3 & 5.4 of Source Whitepaper)

### 9.1. Overview
The system will be deployed using Docker and Docker Compose. This approach containerizes each component (Label Studio, FastAPI application, individual AI model servers), ensuring environment consistency, simplifying setup, and facilitating management of the interconnected services.

### 9.2. Service Definitions (in `docker-compose.yml`)
A `docker-compose.yml` file will define the following key services:

*   **`label_studio` service:**
    *   Based on an official Label Studio Docker image or a custom one if specific plugins/modifications are needed.
    *   Configured to connect to the `fastapi_app` service for its ML backend.
    *   Environment variables for database (if LS uses its own SQLite separate from the main one), hostnames, etc.
    *   Ports exposed (e.g., 8080 for Label Studio UI).
    *   Volume mounts for Label Studio's own data (projects, configs, task metadata - often an SQLite DB itself) and potentially for access to the shared image data if needed directly (though primary image access for AI tasks is via FastAPI service).

*   **`fastapi_app` service:**
    *   Based on a custom Docker image built with Python 3.10+, FastAPI, and all necessary dependencies.
    *   Contains the Business Logic/API Layer code.
    *   Environment variables for database path (SQLite file path), model server URLs, image storage base path.
    *   Ports exposed for internal communication from `label_studio` ML backend (e.g., 8000).
    *   Volume mounts for the SQLite database file and the local file system base path for images.

*   **`yolo_uniow_model_server` service:**
    *   Custom Docker image containing the YOLO-UniOW model and a serving mechanism (e.g., TorchServe, or a simple FastAPI/Flask wrapper around the model inference script).
    *   Volume mounts for model weights if not baked into the image.
    *   Exposes an internal port for inference requests from `fastapi_app`.
    *   GPU access configured if required (via Docker Compose GPU support).

*   **`grounding_dino_model_server` service:** (Similar structure to YOLO server)
    *   Custom image for Grounding DINO.

*   **`gligen_model_server` service:** (Similar structure)
    *   Custom image for GLIGEN, likely using the `diffusers` library. GPU access essential.

*   **`controlnet_model_server` service:** (Similar structure)
    *   Custom image for ControlNet + SD3. GPU access essential.

*   **`internvl2_model_server` service:** (Similar structure)
    *   Custom image for InternVL2.

### 9.3. Data Volumes and Persistence
*   **Image Data:** A Docker named volume or a host path bind-mounted into the `fastapi_app` container (and potentially `label_studio` if it needs direct read access for display, though API-driven is cleaner) to ensure image data persists across container restarts and is accessible by the FastAPI service for processing and delivery to model servers. This volume will point to the user's designated local file system storage area.
*   **SQLite Database:** The SQLite database file will be stored in a Docker named volume or a host path bind-mounted into the `fastapi_app` container to ensure metadata persistence.
*   **Label Studio Data:** Label Studio typically uses its own SQLite database for project management. This will also be persisted using a Docker volume.
*   **Model Weights:** Model weights can either be baked into their respective Docker images or mounted via volumes if they are very large and updated independently of the serving code.

### 9.4. Networking Considerations
*   Docker Compose will create a default bridge network, allowing services to discover and communicate with each other using their service names as hostnames (e.g., `fastapi_app` can reach `yolo_uniow_model_server` at `http://yolo_uniow_model_server:<port>`).
*   Only the `label_studio` service's port (e.g., 8080) needs to be published to the host machine for user access. All other inter-service communication can happen on the internal Docker network.

## 10. Scalability and Performance Considerations

### 10.1. Current Limitations (MVP Focus)
*   **Local File System:** Storage capacity is limited by the user's local disk. Concurrent access performance might be a bottleneck for very high throughput if not managed carefully (though less of an issue for single-user or few-user local setups).
*   **SQLite:** Suitable for single-process writes and many concurrent reads. Performance can degrade with very large databases or high concurrent write loads, not expected in the initial local deployment scenario.
*   **Model Serving:** Each model server, if running on shared hardware (especially single GPU), will process requests sequentially or with limited parallelism, impacting throughput for concurrent AI tasks.
*   **Single `fastapi_app` Instance:** The API layer is a single instance.

### 10.2. Future Scaling Paths
The current architecture, with its separation of concerns, allows for several scaling avenues if the system were to move to a cloud or more distributed environment:
*   **Data Storage:**
    *   Replace local file system with cloud object storage (AWS S3, Google Cloud Storage, Azure Blob Storage). The abstracted Data Access Layer in `fastapi_app` would encapsulate changes. Label Studio also supports these.
    *   Migrate SQLite to a managed relational database service (AWS RDS, Google Cloud SQL, Azure Database).
*   **Model Serving:**
    *   Deploy model servers on dedicated GPU instances.
    *   Use managed AI inference services (e.g., AWS SageMaker Endpoints, Google AI Platform Prediction, Azure ML Endpoints) which handle auto-scaling.
    *   Horizontally scale custom model servers (e.g., run multiple Docker containers for a model server behind a load balancer).
*   **FastAPI Application:**
    *   Run multiple instances of the `fastapi_app` service behind a load balancer if it becomes a bottleneck (would require stateless design or careful state management if state is introduced).
*   **Task Queues:** For long-running processes like model training or large batch generation, introduce a task queue (e.g., Celery with RabbitMQ/Redis) to decouple initiation from execution.

## 11. Security Considerations

### 11.1. Access Control
*   **Label Studio:** Provides its own user authentication and project-based access control. This will be the primary mechanism for controlling who can access which data and perform what actions.
*   **API Layer (`fastapi_app`):** Since it's primarily called by Label Studio's ML backend, direct user authentication might not be needed at this layer if the network is trusted. However, if exposed more broadly, API key authentication or OAuth2 could be implemented. For inter-service communication (LS ML Backend to FastAPI), a shared secret or token could be used.

### 11.2. API Security (Internal)
*   The model serving endpoints are internal and should not be exposed publicly. Communication is within the Docker network.

### 11.3. Data Security (Local Deployment)
*   **File System:** Security of the local file system where images and the SQLite DB are stored is the user's/deployer's responsibility (standard OS file permissions, disk encryption if needed).
*   **SQLite:** The database file itself should be protected by file system permissions.
*   No sensitive data like passwords should be hardcoded; use environment variables for configuration.

### 11.4. Container Security
*   Use official base images where possible.
*   Keep images updated to patch vulnerabilities.
*   Run containers with the least privilege necessary.

## 12. Phased Implementation Plan Summary (From Part 5.4 of Source Whitepaper)
This architecture supports the phased implementation:

*   **Phase 1 (MVP - Core Closed Loop):**
    *   Deploy `label_studio`, `fastapi_app` (with basic CRUD for SQLite), `yolo_uniow_model_server`.
    *   Integrate YOLO-UniOW for pre-annotation via LS ML Backend.
    *   Basic model fine-tuning script (manual trigger).
    *   Focus: Data upload, pre-annotation, manual correction, data saving, manual model update.
*   **Phase 2 (Intelligent Generation):**
    *   Deploy `gligen_model_server`, `controlnet_model_server`.
    *   Add corresponding API endpoints in `fastapi_app` and UI elements/actions in Label Studio for "generate object" and "edit scene."
    *   Focus: Enabling user-guided synthetic data generation.
*   **Phase 3 (Full Automation & UX Optimization):**
    *   Deploy `internvl2_model_server`.
    *   Integrate InternVL2 for prompt assistance.
    *   Develop KPI dashboard.
    *   Batch processing features.
    *   Focus: Enhancing user experience, increasing automation, providing performance visibility.

## 13. Open Issues / Future Work (Architecture specific)
*   **Detailed GPU Management:** For local deployments with multiple models needing GPU, a strategy for sharing or scheduling GPU resources might be needed if a single GPU is available (e.g., Triton's model scheduling or ensuring only one generative model runs at a time).
*   **Error Handling and Resilience:** Define robust error handling and retry mechanisms between services.
*   **Configuration Management:** Centralized or more dynamic configuration management if the number of services and parameters grows significantly.
*   **Logging and Monitoring:** Implement centralized logging (e.g., ELK stack or cloud equivalents) for easier debugging and monitoring across all services in a larger deployment.
*   **Model Training Orchestration:** For more automated and robust model adaptation, a dedicated training pipeline/orchestration tool (e.g., Kubeflow Pipelines, Apache Airflow) could be integrated in the future, replacing the simple MVP script.
```
