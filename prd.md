```markdown
# Product Requirements Document: Agile AI Vision Application

## 1. Introduction

### 1.1. Purpose
This document outlines the requirements for an Agile AI Vision Application designed for non-technical users. The primary purpose of this application is to empower users to rapidly develop, deploy, and iteratively improve AI vision models by establishing a self-improving "living system" rather than relying on static, periodically trained models. It aims to democratize AI model enhancement by directly involving domain experts in the optimization loop.

### 1.2. Scope
The scope of this project includes the development of a full-stack application encompassing:
*   A user-friendly web interface for data upload, annotation, model interaction, and data generation.
*   Backend services for object detection, data synthesis, and model adaptation.
*   Integration of advanced AI models for open-vocabulary detection, unknown object identification, and controllable image generation.
*   A data management system for storing images and their associated metadata.
*   Mechanisms for rapid model fine-tuning and performance tracking.

The initial deployment will focus on local file system storage as per user requirements, with an architecture designed for future scalability.

### 1.3. Background and Rationale
Traditional AI model development follows a linear, costly, and time-consuming "collect-annotate-train-deploy" cycle, heavily reliant on technical specialists. This makes model updates slow and misaligned with dynamic business needs. The proposed system addresses these limitations by creating a "Data Flywheel" – a sustainable, self-driven AI ecosystem. This approach shifts the focus from mere data annotation to strategic data synthesis, enabling the system to proactively generate valuable training data. The core rationale is to significantly reduce the "value realization time" from problem discovery to solution deployment, thereby achieving cost reduction, increased efficiency, and rapid iteration capabilities for AI vision tasks.

## 2. Goals and Objectives

### 2.1. Primary Goals
*   **Empower Non-Technical Users:** Enable domain experts, without requiring deep AI/coding knowledge, to directly contribute to and guide the improvement of AI vision models.
*   **Achieve Rapid Iteration:** Drastically shorten the cycle time for model updates, corrections, and the introduction of new detection capabilities.
*   **Reduce Costs and Increase Efficiency:** Minimize reliance on manual data collection/annotation and specialized AI personnel through intelligent automation and data synthesis.
*   **Build a Self-Improving System:** Create a "Data Flywheel" where user interactions and AI-generated data continuously enhance model performance and robustness over time.
*   **Shift from Data Consumption to Data Creation:** Transition from passively labeling existing data to actively synthesizing high-quality, targeted training data to address specific model deficiencies or new requirements.

### 2.2. Secondary Objectives
*   Provide a flexible and extensible platform capable of incorporating new AI models and techniques as they emerge.
*   Offer clear metrics to track system performance and the effectiveness of the Data Flywheel.
*   Ensure a high-quality user experience through an intuitive and responsive interface.

## 3. Target Audience

### 3.1. Primary Users
*   **Non-technical domain experts:** Individuals with deep knowledge of specific business areas and visual data (e.g., quality control specialists, inventory managers, agricultural experts, security personnel) but without programming or AI modeling expertise. They are the primary users who will interact with the system to correct model outputs, define new object categories, and guide data generation.
*   **Business analysts or operations managers:** Users who need to quickly adapt AI vision systems to changing business requirements, new products, or evolving operational environments without lengthy development cycles.

### 3.2. Secondary Users (if any)
*   **AI/ML Engineers (for setup and maintenance):** While the system is designed for non-technical end-users, AI/ML engineers may be involved in the initial setup, deployment, advanced configuration, and maintenance of the underlying models and infrastructure.
*   **Data Curators/Managers (potentially):** Individuals responsible for overall data governance and quality, who might use the system's outputs and capabilities as part of a broader data strategy.

## 4. User Needs & Pain Points Addressed

The system aims to address the following key user needs and pain points:

*   **Need for Speed and Agility:**
    *   **Pain Point:** Current AI model development is too slow; adapting to new products or fixing errors takes weeks or months.
    *   **Solution:** Enable rapid model updates, correction of misdetections, and addition of new object categories in significantly less time.
*   **Ease of Use for Non-Experts:**
    *   **Pain Point:** AI tools are complex and require specialized technical skills, creating a bottleneck.
    *   **Solution:** Provide an intuitive, user-friendly interface that allows non-technical users to effectively guide AI model improvement without coding.
*   **High Cost of AI Development and Maintenance:**
    *   **Pain Point:** Extensive data collection, manual labeling, and reliance on AI experts are expensive.
    *   **Solution:** Reduce costs through automated pre-annotation, AI-powered data synthesis (reducing manual labeling), and empowering existing domain experts.
*   **Data Scarcity for Specific Needs:**
    *   **Pain Point:** Lack of sufficient, diverse, and high-quality training data, especially for new or rare object categories or specific scenarios.
    *   **Solution:** Enable users to guide the generation of synthetic data tailored to fill these gaps, effectively creating necessary data on demand.
*   **Inefficient Error Correction Process:**
    *   **Pain Point:** Identifying and correcting model errors (漏检 - missed detections, 错检 - false positives) is a tedious and manual process.
    *   **Solution:** Streamline error correction through AI-assisted identification of potential errors (e.g., "unknown" objects) and intuitive tools for users to make corrections.
*   **Static Models Unable to Cope with Change:**
    *   **Pain Point:** Models trained once become outdated as real-world conditions, products, or requirements evolve.
    *   **Solution:** Create a "living system" that continuously learns and adapts based on user feedback and new data, maintaining high performance over time.
*   **Difficulty in Quantifying Model Improvement:**
    *   **Pain Point:** It's hard to see if changes are actually making the AI better in a tangible way.
    *   **Solution:** Provide clear KPIs to track model improvement and the efficiency of the data iteration process.

## 5. Proposed Solution Overview

### 5.1. Core Concept (Data Flywheel)
The proposed solution is centered around a "Data Flywheel" model, a closed-loop feedback system designed to create a virtuous cycle of continuous model improvement through user-AI interaction. This model aims to transform traditional AI development into a dynamic, self-optimizing process. The flywheel consists of four key stages:

1.  **Detect & Identify Gaps:** The system's core object detection model processes new, real-world business data. Any performance deficiencies (e.g., missed detections, incorrect identifications) are captured not as mere errors, but as valuable signals ("fuel") indicating areas for model improvement.
2.  **User-Guided Correction & Augmentation:** Non-technical users interact with the system via an intuitive web interface. They correct model errors and, crucially, guide data augmentation by initiating data generation tasks, especially for new object categories or to address specific deficiencies.
3.  **Intelligent Data Synthesis:** Based on user corrections and requests, the system's "Intelligent Data Synthesis Engine" employs generative AI techniques to create high-quality, precisely annotated training samples on demand. This includes generating variations of existing objects or synthesizing entirely new objects within specified contexts.
4.  **Rapid Model Adaptation:** New data (user-corrected and AI-synthesized) is used to efficiently fine-tune or adapt the existing AI model. This process utilizes techniques like incremental learning or few-shot adaptation to quickly incorporate new knowledge without full retraining, ensuring the model continuously improves and avoids catastrophic forgetting.

This cycle ensures that each iteration not only addresses immediate issues but also enhances the model's overall capability and generalization, reducing future manual intervention.

### 5.2. Key Innovations
*   **Shift from Annotation to Synthesis:** Moving beyond manual labeling to AI-assisted and AI-driven creation of core data assets.
*   **Non-Technical User Empowerment:** Placing domain experts directly in the loop of model optimization.
*   **Integrated Open-World and Generative AI:** Combining advanced detection models (capable of identifying "unknowns") with controllable generation techniques for targeted data creation.
*   **Focus on "Time to Value":** Drastically reducing the time from problem identification/new need to a deployed, improved solution.

## 6. Functional Requirements

### 6.1. FR1: Data Ingestion and Management
*   **6.1.1:** Users shall be able to upload image data (individual files and batches) into the system.
*   **6.1.2:** The system shall store uploaded images on a local file system as per initial requirements.
*   **6.1.3:** The system shall manage metadata associated with images, including file paths, annotations, and project configurations, using a lightweight database (SQLite).
*   **6.1.4:** The system should provide basic project management capabilities (e.g., creating new projects, organizing data within projects).

### 6.2. FR2: Object Detection Core
The system must incorporate advanced object detection capabilities to serve as the foundation of the Data Flywheel.

*   **6.2.1. Real-time Interactive Detection (YOLO-UniOW):**
    *   **6.2.1.1:** The system shall use an efficient model (recommended: YOLO-UniOW) for real-time or near real-time pre-annotation of uploaded images in the user interface.
    *   **6.2.1.2:** This model must provide immediate feedback to the user, suggesting bounding boxes and class labels for known objects.
*   **6.2.2. High-Accuracy Offline Analysis (Grounding DINO):**
    *   **6.2.2.1:** The system shall incorporate a high-accuracy model (recommended: Grounding DINO) for backend analysis tasks where precision is paramount.
    *   **6.2.2.2:** This model can be used for batch processing or as a "locator" tool for the intelligent synthesis engine, especially when precise object localization is critical for generation.
*   **6.2.3. Open Vocabulary Detection (OVD):**
    *   **6.2.3.1:** The detection models shall support Open Vocabulary Detection, allowing users to define new object categories using natural language text dynamically.
    *   **6.2.3.2:** The system must be able to detect these newly defined categories in images, even if the categories were not part of the model's original training set. This is crucial for "Time to New Capability."
*   **6.2.4. Unknown Object Identification (Open World Object Detection - OWOD):**
    *   **6.2.4.1:** The primary real-time detection model (YOLO-UniOW) shall possess Open World Detection capabilities, specifically the ability to identify and flag objects that do not belong to any of the currently known/defined categories as "unknown."
    *   **6.2.4.2:** This "unknown object" flagging is critical for proactively identifying model blind spots (漏检) and guiding users to areas needing attention or new category definition, transforming error discovery from a manual search to a guided review.

### 6.3. FR3: User-Guided Correction and Annotation
The system must provide intuitive tools for users to correct AI model outputs and perform manual annotations when necessary.

*   **6.3.1. Manual Annotation Tools:**
    *   **6.3.1.1:** The user interface (Label Studio) shall provide standard annotation tools (e.g., bounding boxes, polygons if feasible in later stages).
    *   **6.3.1.2:** Users shall be able to create, modify, and delete annotations.
*   **6.3.2. Review and Correction of AI Outputs:**
    *   **6.3.2.1:** Users shall be able to easily review pre-annotations and "unknown" object suggestions from the detection models.
    *   **6.3.2.2:** Users shall be able to accept, reject, or modify these AI-generated suggestions (e.g., adjust bounding box coordinates, change or assign class labels).
*   **6.3.3. Label Management:**
    *   **6.3.3.1:** Users shall be able to define and manage a list of object categories (class labels) for each project.
    *   **6.3.3.2:** This includes adding new categories, renaming existing ones, and potentially assigning colors or other visual aids for labels in the UI.
    *   **6.3.3.3:** Corrected "unknown" objects should seamlessly be assignable to existing or newly created categories.

### 6.4. FR4: Intelligent Data Synthesis Engine
This engine is core to the system's innovation, enabling proactive data creation.

*   **6.4.1. Automated Pre-annotation (covered by FR2.1):**
    *   **6.4.1.1:** When new images are uploaded, the system (via YOLO-UniOW) shall automatically provide initial bounding boxes and labels as a starting point for the user, fulfilling the "automatic pre-annotation" need.
*   **6.4.2. Controllable Object Generation (GLIGEN-based):**
    *   **6.4.2.1:** The system shall allow users to generate new object instances within existing or new images, based on textual descriptions and user-specified locations (bounding boxes). (Recommended model: GLIGEN).
    *   **6.4.2.2:** This feature is key for "为现有数据集快速增加新的检测类别" (adding new detection categories to existing datasets).
    *   **6.4.2.3:** Generated objects should be realistically blended with the background image.
    *   **6.4.2.4:** The system must automatically create and save the annotation (bounding box and class label) for the newly synthesized object.
*   **6.4.3. Scene-Aware Inpainting/Modification (ControlNet-based):**
    *   **6.4.3.1:** The system shall provide tools for more complex image editing, such as replacing an incorrectly identified object or modifying parts of an image while maintaining scene consistency (Recommended model: ControlNet + SD3).
    *   **6.4.3.2:** Users should be able to define a region (mask) for modification and provide a textual prompt for the desired change.
    *   **6.4.3.3:** The generation should respect the original image's context (e.g., lighting, perspective) using control signals like depth maps or edge maps.
    *   **6.4.3.4:** This is crucial for correcting complex misdetections or augmenting scenes in a fine-grained manner.
*   **6.4.4. Prompt Assistance (Prompt Co-pilot - InternVL2):**
    *   **6.4.4.1:** To aid non-technical users in creating effective textual prompts for generative models, the system shall integrate a "Prompt Co-pilot" (Recommended LMM: InternVL2).
    *   **6.4.4.2:** When a user provides a simple class name or concept for generation, the Prompt Co-pilot shall suggest a list of diverse, descriptive, and high-quality prompt templates.
    *   **6.4.4.3:** Users should be able to select from these suggestions or use them as inspiration to refine their own prompts, improving the quality and diversity of generated data.

### 6.5. FR5: Model Adaptation and Training
The system must facilitate the rapid incorporation of new knowledge (from corrections and synthesis) into the AI models.

*   **6.5.1. Rapid Model Fine-tuning/Adaptation:**
    *   **6.5.1.1:** The system shall include mechanisms to trigger model fine-tuning or adaptation using the newly acquired/corrected annotated data and synthetically generated data.
    *   **6.5.1.2:** This process should be efficient, focusing on incremental learning or few-shot adaptation techniques to minimize training time and computational cost, and to avoid catastrophic forgetting.
*   **6.5.2. Mechanism to Trigger Re-training/Adaptation:**
    *   **6.5.2.1:** While full automation of re-training triggers might be complex for MVP, the system should at least provide a straightforward way for an administrator or designated user to initiate the model adaptation process using the accumulated new data.
    *   **6.5.2.2:** (Future) The system could explore heuristics to suggest when re-training might be beneficial (e.g., after a certain volume of new data is collected).

### 6.6. FR6: User Interface and Workflow (Label Studio as Core)
The application layer, centered around Label Studio, must provide a seamless and intuitive experience.

*   **6.6.1. Integrated Platform:**
    *   **6.6.1.1:** Label Studio shall serve as the primary user interface, orchestrating the entire human-in-the-loop workflow.
    *   **6.6.1.2:** All user interactions – data upload, viewing pre-annotations, manual correction, triggering data synthesis, initiating prompt assistance – shall occur within this unified environment.
*   **6.6.2. Intuitive Controls for Non-technical Users:**
    *   **6.6.2.1:** The interface, including any custom actions for generation or prompt assistance, must be designed for users without a technical background.
    *   **6.6.2.2:** Workflows for correcting detections, adding new classes, and generating data should be straightforward and require minimal training.
*   **6.6.3. ML Backend Integration:**
    *   **6.6.3.1:** Label Studio's ML Backend mechanism shall be used to integrate all custom AI model services (YOLO-UniOW for pre-annotation, GLIGEN/ControlNet for generation, InternVL2 for prompt assistance).
    *   **6.6.3.2:** This integration should allow for bidirectional communication: Label Studio sending requests to the model services and receiving results (predictions, generated images, prompt suggestions) for display.
*   **6.6.4. Custom UI Elements for AI Interactions:**
    *   **6.6.4.1:** The Label Studio interface may need to be customized with specific buttons or controls to trigger data generation ("Generate Object with GLIGEN", "Edit with ControlNet") or prompt assistance ("Get Prompt Suggestions").
*   **6.6.5. Visualization of Model Performance/KPIs (Basic):**
    *   **6.6.5.1:** (Phase 3/Future) The system should provide a simple dashboard or view within Label Studio (or linked from it) to display the key performance indicators (KPIs) outlined in Section 8, allowing users to track model improvement over time.

## 7. Non-Functional Requirements

### 7.1. NFR1: Performance
*   **7.1.1. Real-time Detection Latency (YOLO-UniOW):**
    *   Pre-annotation of an image upon upload should ideally complete within a few seconds (e.g., < 5 seconds for typical image sizes) to ensure a fluid user experience. Target FPS for the model itself is high (e.g., YOLO-UniOW-L ~64.8 FPS on A100), but end-to-end latency including data transfer will be higher.
*   **7.1.2. Data Generation Time (GLIGEN, ControlNet):**
    *   Generation of a single new object instance (GLIGEN) or a scene modification (ControlNet) should ideally complete within a reasonable timeframe for interactive use (e.g., < 30-60 seconds). Batch generation can have longer timelines.
*   **7.1.3. Model Adaptation Time:**
    *   Rapid model adaptation/fine-tuning should be significantly faster than full retraining, ideally completable within hours rather than days, depending on the volume of new data.
*   **7.1.4. UI Responsiveness:**
    *   The Label Studio interface must be responsive, with minimal lag during common operations like drawing bounding boxes, changing labels, or navigating between tasks.

### 7.2. NFR2: Usability
*   **7.2.1. Ease of Use for Non-Technical Users:** The system must be highly intuitive and usable by individuals without a background in AI or software development. Workflows for common tasks (correction, generation) should be self-explanatory or require minimal documentation/training.
*   **7.2.2. Clarity of AI Suggestions:** Pre-annotations and "unknown" object highlights must be clearly presented to the user.
*   **7.2.3. Feedback Mechanisms:** The system should provide clear feedback to users on the status of operations (e.g., "generation in progress," "model training complete").

### 7.3. NFR3: Data Management and Storage
*   **7.3.1. Local File System Storage:** All raw image data and generated image files must be stored on the user's specified local file system.
*   **7.3.2. Metadata Integrity (SQLite):** Annotation data, file paths, project configurations, and other metadata stored in SQLite must be accurate and consistently maintained.
*   **7.3.3. Data Privacy:** Since data is stored locally, the system itself does not introduce new external data privacy concerns, but best practices for securing local data access should be considered by the user/deployer.
*   **7.3.4. Data Backup:** The system itself will not provide automated backup of the local file system or SQLite database; this will be the user's responsibility. (This should be clearly communicated).

### 7.4. NFR4: Scalability (Future Considerations)
*   **7.4.1. Architectural Design for Scalability:** While initial deployment is local, the architecture (especially the separation of the Business Logic/API layer and Model Serving layer) should allow for future migration to cloud storage (e.g., S3) and more scalable database solutions with manageable effort. The use of an abstracted data access layer is recommended.
*   **7.4.2. Model Serving Scalability:** The model serving layer should be designed to potentially scale independently, e.g., by deploying more instances of model servers if demand increases in a future cloud-based scenario.

### 7.5. NFR5: Extensibility
*   **7.5.1. Model Agnosticism (within reason):** The system should be designed to facilitate the integration of new or updated detection or generation models in the future with reasonable development effort, primarily by modifying the API/Business Logic Layer and Model Serving Layer.
*   **7.5.2. Label Studio Customization:** Leverage Label Studio's inherent flexibility for adding new labeling configurations or custom UI elements as needed.

### 7.6. NFR6: Maintainability
*   **7.6.1. Code Modularity:** Backend services (FastAPI, model servers) should be developed with modularity in mind for easier updates and bug fixing.
*   **7.6.2. Clear APIs:** APIs between Label Studio ML Backend, FastAPI service, and model servers must be well-defined and documented.
*   **7.6.3. Configuration Management:** Key parameters (model paths, server addresses) should be configurable.

### 7.7. NFR7: Deployment
*   **7.7.1. Dockerized Deployment:** The entire system (Label Studio, FastAPI backend, model serving components) should be deployable using Docker and Docker Compose to simplify setup and ensure environment consistency.
*   **7.7.2. Clear Installation Instructions:** Comprehensive documentation must be provided for setting up and running the system.

## 8. Success Metrics (KPIs)
The success of the Agile AI Vision Application will be measured against the following Key Performance Indicators (KPIs), as defined in Part 1.3 of the source document. These KPIs directly reflect the system's ability to deliver on its core promises of "降本增效" (cost reduction and efficiency increase) and "快速迭代" (rapid iteration).

*   **8.1. Problem修正时间 (Time to Correct):**
    *   **Definition:** The total time elapsed from the moment a business user identifies a model detection error in a practical application to the successful deployment of an updated model that includes the correction.
    *   **Measures:** System agility and responsiveness to errors.
*   **8.2. 新能力上线时间 (Time to New Capability):**
    *   **Definition:** The end-to-end time taken from when a business or sales department requests the detection of a completely new object category to the point where the model possesses this new capability and is ready for operational use.
    *   **Measures:** Efficiency in supporting business expansion and adapting to new requirements.
*   **8.3. 标注效率 (Annotation Efficiency):**
    *   **Definition:** The ratio of annotations generated or assisted by AI (including pre-annotations and synthesized data annotations) to the number of annotations that need to be created manually from scratch by a human, throughout the data iteration cycle.
    *   **Measures:** The efficiency gains brought by the "Intelligent Data Synthesis Engine" and automated pre-annotation.
*   **8.4. 模型性能提升率 (Model Performance Lift):**
    *   **Definition:** The percentage increase in key model performance metrics (e.g., mean Average Precision - mAP) on a standardized evaluation dataset after each full cycle of the Data Flywheel.
    *   **Measures:** The effectiveness of the Data Flywheel in driving continuous, measurable self-improvement of the AI model.

These KPIs will serve as "North Star" metrics during development and operational phases to ensure all technical decisions align with the ultimate goals of enhancing system responsiveness, reducing operational costs, and continually improving core AI capabilities.

## 9. Future Considerations / Potential Enhancements
*   Cloud storage integration (e.g., AWS S3, Azure Blob Storage) for improved scalability and data management.
*   More sophisticated database solutions for larger-scale deployments.
*   Automated triggers for model re-training based on data volume or performance degradation.
*   Advanced analytics and visualization of model performance trends.
*   Support for a wider range of annotation types (e.g., semantic segmentation, instance segmentation).
*   Integration with MLOps platforms for more robust model versioning, deployment, and monitoring.
*   Multi-user collaboration features with role-based access control.

## 10. Assumptions and Dependencies
*   **Assumption:** Users will have access to hardware (potentially with GPUs) suitable for running the AI models, especially for model training/adaptation and efficient inference for generative models.
*   **Assumption:** Non-technical users can be adequately trained to use the Label Studio interface and understand the concepts of correcting annotations and guiding data generation.
*   **Dependency:** Availability and stability of the chosen open-source models (YOLO-UniOW, Grounding DINO, GLIGEN, ControlNet, InternVL2) and their underlying libraries (PyTorch, Diffusers, etc.).
*   **Dependency:** Label Studio's ML backend functionality and its compatibility with the custom FastAPI service.
*   **Dependency:** Python environment and necessary libraries can be consistently managed, likely via Docker.

## 11. Out of Scope (for MVP / Initial Phases)
*   Fully automated model retraining triggers without any human intervention.
*   Advanced user management and role-based access control beyond basic Label Studio project separation.
*   Direct integration with cloud-based managed AI training services.
*   Real-time collaborative annotation by multiple users on the same task simultaneously (standard Label Studio behavior for task locking will apply).
*   Support for data types other than images.
*   Detailed performance optimization for extremely large datasets (tens of millions of images) – focus is on local, manageable datasets initially.
*   Automated data backup and disaster recovery solutions (user responsibility for local deployments).
```
