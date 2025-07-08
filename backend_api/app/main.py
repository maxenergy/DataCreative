```python
from fastapi import FastAPI

app = FastAPI(
    title="Agile AI Vision Backend API",
    description="API for supporting the Agile AI Vision application, interfacing with Label Studio and AI Model Servers.",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Agile AI Vision Backend API"}

# Further router includes will go here
from .api import endpoints
from .db import database # Import database module

# Create database tables on startup
@app.on_event("startup")
async def startup_db_client():
    database.create_db_and_tables()
    print("Database tables checked/created.")

app.include_router(endpoints.router, prefix="/api/v1", tags=["ML Backend"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
