"""FastAPI application entry point"""

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import postings, auth
from app.database import engine, Base
from app.models import database_models

app = FastAPI(
    title="AI-Powered Cash Posting Agent",
    description="Proof of Concept for automated payment-to-invoice matching",
    version="1.0.0"
)

# Create database tables on startup (if they don't exist)
@app.on_event("startup")
async def startup_event():
    """Create database tables on application startup"""
    Base.metadata.create_all(bind=engine)

# Enable CORS for frontend integration (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount output directory for CSV downloads
output_path = Path("output")
if output_path.exists():
    app.mount("/output", StaticFiles(directory="output"), name="output")

# Include routers
app.include_router(auth.router)
app.include_router(postings.router)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the login page"""
    login_file = Path("static/login.html")
    if login_file.exists():
        return FileResponse(login_file)
    return {"message": "Please access /login or /app"}


@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve the login page"""
    login_file = Path("static/login.html")
    if login_file.exists():
        return FileResponse(login_file)
    return {"message": "Login page not found"}


@app.get("/signup", response_class=HTMLResponse)
async def signup_page():
    """Serve the signup page"""
    signup_file = Path("static/signup.html")
    if signup_file.exists():
        return FileResponse(signup_file)
    return {"message": "Signup page not found"}


@app.get("/app", response_class=HTMLResponse)
async def app_page():
    """Serve the main application page (protected)"""
    app_file = Path("static/index.html")
    if app_file.exists():
        return FileResponse(app_file)
    return {"message": "Application page not found"}


@app.get("/results", response_class=HTMLResponse)
async def results_page():
    """Serve the results page"""
    results_file = Path("static/results.html")
    if results_file.exists():
        return FileResponse(results_file)
    return {"message": "Results page not found"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

