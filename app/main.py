from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.endpoints import router
from app.database.connection import db
import uvicorn

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to the database on startup
    db.connect()
    yield
    # Close the database connection on shutdown
    db.close()

app = FastAPI(
    title="User & Transaction Graph API",
    description="API for managing user and transaction relationships in a graph database",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5001"],  # Allow the frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def root():
    # Serve the visualization page
    return open("static/index.html").read()

@app.get("/visualization", response_class=HTMLResponse)
async def visualization():
    # Serve the visualization page
    return open("static/index.html").read()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
