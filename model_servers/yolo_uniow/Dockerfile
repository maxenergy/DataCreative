```dockerfile
# Start with a Python base image that includes appropriate ML libraries or is built upon an NVIDIA CUDA image
# For CPU:
FROM python:3.10-slim
# For GPU (example, choose one that matches your PyTorch/CUDA needs):
# FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

WORKDIR /model_server

# Copy requirements first
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the server code
COPY ./serve.py /model_server/serve.py
# If you have model weights or other assets, copy them too
# COPY ./model_weights /model_server/model_weights

EXPOSE 8001

# Command to run the server
# Ensure this matches how you want to run your FastAPI app (e.g., if serve.py is the entrypoint)
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8001"]
```
