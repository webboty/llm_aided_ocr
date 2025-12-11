#!/usr/bin/env python3
"""
LLM-Aided OCR API Server
Provides REST API endpoints for PDF OCR processing
"""

import os
import sys
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks,
    Form,
    Depends,
    Security,
)
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from decouple import config

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_aided_ocr import process_document_pipeline
from config_helper import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
API_SECRET_TOKEN = config("API_SECRET_TOKEN", default=None, cast=str)
API_PORT = config("API_PORT", default=8000, cast=int)
API_HOST = config("API_HOST", default="0.0.0.0", cast=str)
RESULTS_DIR = config("RESULTS_DIR", default="results", cast=str)

# Security
security = HTTPBearer(auto_error=False)


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API token if configured"""
    if API_SECRET_TOKEN:
        if not credentials or credentials.credentials != API_SECRET_TOKEN:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return credentials


# Initialize FastAPI app
app = FastAPI(
    title="LLM-Aided OCR API",
    description="API for advanced OCR processing with LLM correction",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for job tracking
active_jobs: Dict[str, Dict[str, Any]] = {}

# Ensure results directory exists
RESULTS_DIR_PATH = Path(RESULTS_DIR)
RESULTS_DIR_PATH.mkdir(exist_ok=True)


class JobStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: Optional[float] = None
    message: Optional[str] = None
    output_files: Optional[Dict[str, str]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProcessRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    output_path: Optional[str] = None


def validate_pdf_file(file_path: str) -> bool:
    """Validate that the file is a PDF and exists"""
    if not os.path.exists(file_path):
        return False
    if not file_path.lower().endswith(".pdf"):
        return False
    return True


def validate_output_path(output_path: str) -> bool:
    """Validate that the output path is accessible"""
    try:
        path = Path(output_path)
        # Check if parent directory exists or can be created
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        # Test write permissions
        test_file = path.parent / f".test_write_{uuid.uuid4().hex[:8]}"
        test_file.touch()
        test_file.unlink()
        return True
    except Exception:
        return False


async def process_pdf_job(
    job_id: str,
    pdf_path: str,
    output_path: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
):
    """Background task to process PDF"""
    try:
        # Update job status
        active_jobs[job_id]["status"] = "processing"
        active_jobs[job_id]["progress"] = 0.1
        active_jobs[job_id]["message"] = "Starting OCR processing..."
        active_jobs[job_id]["updated_at"] = datetime.now()

        # Determine output directory
        if output_path and validate_output_path(output_path):
            output_dir = Path(output_path).parent
        else:
            output_dir = RESULTS_DIR_PATH / job_id
            output_dir.mkdir(exist_ok=True)

        # Change to script directory for relative paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        original_cwd = os.getcwd()
        os.chdir(script_dir)

        try:
            # Configure provider if specified
            if provider:
                import subprocess

                logger.info(f"Setting provider to: {provider}")
                subprocess.run(["python", "config_helper.py", provider], check=True)

            # Configure model if specified
            if model and provider == "lm-studio":
                import subprocess

                logger.info(f"Setting model to: {model}")
                subprocess.run(
                    ["python", "config_helper.py", "lm-model", model], check=True
                )

            # Update progress
            active_jobs[job_id]["progress"] = 0.3
            active_jobs[job_id]["message"] = "Processing document..."
            active_jobs[job_id]["updated_at"] = datetime.now()

            # Process the document
            output_files = await process_document_pipeline(
                pdf_path=pdf_path,
                output_dir=str(output_dir),
                max_test_pages=0,
                skip_first_n_pages=0,
                reformat_as_markdown=True,
            )

            # Output files are already returned by the pipeline function

            # Update job status to completed
            active_jobs[job_id]["status"] = "completed"
            active_jobs[job_id]["progress"] = 1.0
            active_jobs[job_id]["message"] = "Processing completed successfully"
            active_jobs[job_id]["output_files"] = output_files
            active_jobs[job_id]["updated_at"] = datetime.now()

            logger.info(f"Job {job_id} completed successfully")

        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)
        active_jobs[job_id]["message"] = f"Processing failed: {str(e)}"
        active_jobs[job_id]["updated_at"] = datetime.now()


@app.get("/")
async def root(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Root endpoint with API information"""
    return {
        "name": "LLM-Aided OCR API",
        "version": "1.0.0",
        "description": "API for advanced OCR processing with LLM correction",
        "endpoints": {
            "process_pdf": "POST /process",
            "upload_and_process": "POST /upload",
            "job_status": "GET /job/{job_id}",
            "download_file": "GET /download/{job_id}/{filename}",
            "health": "GET /health",
        },
    }


@app.get("/health")
async def health_check(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/process")
async def process_pdf_from_path(
    credentials: HTTPAuthorizationCredentials = Security(security),
    background_tasks: BackgroundTasks,
    pdf_path: str = Form(...),
    output_path: Optional[str] = Form(None),
    provider: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
):
    """
    Process a PDF file from file path

    Args:
        pdf_path: Path to the PDF file to process
        output_path: Optional output path for results
        provider: Optional LLM provider (openai, claude, lm-studio)
        model: Optional model name (for lm-studio)

    Returns:
        Job ID for tracking processing status
    """
    # Validate PDF file
    if not validate_pdf_file(pdf_path):
        raise HTTPException(
            status_code=400, detail="Invalid PDF file path or file not found"
        )

    # Validate output path if provided
    if output_path and not validate_output_path(output_path):
        raise HTTPException(
            status_code=400, detail="Invalid output path or insufficient permissions"
        )

    # Create job ID
    job_id = str(uuid.uuid4())

    # Initialize job
    active_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0.0,
        "message": "Job queued for processing",
        "output_files": None,
        "error": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # Start background processing
    background_tasks.add_task(
        process_pdf_job, job_id, pdf_path, output_path, provider, model
    )

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "PDF processing started",
        "pdf_path": pdf_path,
        "output_path": output_path,
    }


@app.post("/upload")
async def upload_and_process_pdf(
    credentials: HTTPAuthorizationCredentials = Security(security),
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    output_path: Optional[str] = Form(None),
    provider: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
):
    """
    Upload and process a PDF file

    Args:
        file: PDF file to upload and process
        output_path: Optional output path for results
        provider: Optional LLM provider (openai, claude, lm-studio)
        model: Optional model name (for lm-studio)

    Returns:
        Job ID for tracking processing status
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Create job ID
    job_id = str(uuid.uuid4())

    # Create upload directory
    upload_dir = RESULTS_DIR_PATH / "uploads" / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save uploaded file
    pdf_path = upload_dir / file.filename
    try:
        with open(pdf_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Validate output path if provided
    if output_path and not validate_output_path(output_path):
        raise HTTPException(
            status_code=400, detail="Invalid output path or insufficient permissions"
        )

    # Initialize job
    active_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0.0,
        "message": "File uploaded, queued for processing",
        "output_files": None,
        "error": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # Start background processing
    background_tasks.add_task(
        process_pdf_job, job_id, str(pdf_path), output_path, provider, model
    )

    return {
        "job_id": job_id,
        "status": "pending",
        "message": "PDF uploaded and processing started",
        "filename": file.filename,
        "output_path": output_path,
    }


@app.get("/job/{job_id}")
async def get_job_status(job_id: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    """Get the status of a processing job"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]
    return JobStatus(**job)


@app.get("/download/{job_id}/{filename}")
async def download_file(job_id: str, filename: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    """Download a processed file"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = active_jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    # Look for the file in output files or results directory
    file_path = None
    if job["output_files"]:
        for file_type, path in job["output_files"].items():
            if Path(path).name == filename:
                file_path = path
                break

    if not file_path:
        # Try to find in results directory
        potential_path = RESULTS_DIR_PATH / job_id / filename
        if potential_path.exists():
            file_path = str(potential_path)
        else:
            raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path, filename=filename, media_type="application/octet-stream"
    )


@app.get("/jobs")
async def list_jobs(credentials: HTTPAuthorizationCredentials = Security(security)):
    """List all jobs"""
    return {"jobs": list(active_jobs.values()), "total": len(active_jobs)}


@app.delete("/job/{job_id}")
async def delete_job(job_id: str, credentials: HTTPAuthorizationCredentials = Security(security)):
    """Delete a job and its associated files"""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    # Remove job from active jobs
    del active_jobs[job_id]

    # Optionally clean up job files
    job_dir = RESULTS_DIR_PATH / job_id
    if job_dir.exists():
        import shutil

        shutil.rmtree(job_dir)

    return {"message": "Job deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    
    # Log configuration
    if API_SECRET_TOKEN:
        logger.info("🔒 API authentication is enabled")
    else:
        logger.warning("⚠️  API authentication is DISABLED - anyone can access the API")
    
    logger.info(f"🚀 Starting API server on {API_HOST}:{API_PORT}")
    logger.info(f"📁 Results directory: {RESULTS_DIR_PATH.absolute()}")
    
    uvicorn.run(app, host=API_HOST, port=API_PORT)
