from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    """A placeholder endpoint to confirm the service is running."""
    return {"status": "ok", "message": "Welcome to the AI Visual Application Backend"}
