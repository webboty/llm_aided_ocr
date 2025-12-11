#!/usr/bin/env python3
"""
LLM-Aided OCR MCP Server
Provides Model Context Protocol server for PDF OCR processing
"""

import os
import sys
import uuid
import asyncio
import logging
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    CallToolResult,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceResult,
)

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_aided_ocr import process_document_pipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
RESULTS_DIR_PATH = Path(RESULTS_DIR)
RESULTS_DIR_PATH.mkdir(exist_ok=True)

# Global variables for job tracking
active_jobs: Dict[str, Dict[str, Any]] = {}

# Initialize MCP server
server = Server("llm-aided-ocr-mcp")


class JobStatus:
    """Job status data structure"""

    def __init__(
        self,
        job_id: str,
        status: str,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        output_files: Optional[Dict[str, str]] = None,
        error: Optional[str] = None,
    ):
        self.job_id = job_id
        self.status = status  # "pending", "processing", "completed", "failed"
        self.progress = progress
        self.message = message
        self.output_files = output_files
        self.error = error
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "output_files": self.output_files,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


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
        active_jobs[job_id].status = "processing"
        active_jobs[job_id].progress = 0.1
        active_jobs[job_id].message = "Starting OCR processing..."
        active_jobs[job_id].updated_at = datetime.now()

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
            active_jobs[job_id].progress = 0.3
            active_jobs[job_id].message = "Processing document..."
            active_jobs[job_id].updated_at = datetime.now()

            # Process the document
            output_files = await process_document_pipeline(
                pdf_path=pdf_path,
                output_dir=str(output_dir),
                max_test_pages=0,
                skip_first_n_pages=0,
                reformat_as_markdown=True,
            )

            # Update job status to completed
            active_jobs[job_id].status = "completed"
            active_jobs[job_id].progress = 1.0
            active_jobs[job_id].message = "Processing completed successfully"
            active_jobs[job_id].output_files = output_files
            active_jobs[job_id].updated_at = datetime.now()

            logger.info(f"Job {job_id} completed successfully")

        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        active_jobs[job_id].status = "failed"
        active_jobs[job_id].error = str(e)
        active_jobs[job_id].message = f"Processing failed: {str(e)}"
        active_jobs[job_id].updated_at = datetime.now()


@server.list_resources()
async def handle_list_resources() -> ListResourcesResult:
    """List available resources (processed files)"""
    resources = []

    # Add job results as resources
    for job_id, job in active_jobs.items():
        if job.status == "completed" and job.output_files:
            for file_type, file_path in job.output_files.items():
                if os.path.exists(file_path):
                    resources.append(
                        Resource(
                            uri=f"ocr://job/{job_id}/{file_type}",
                            name=f"{job_id} - {file_type}",
                            description=f"OCR output file: {file_type}",
                            mimeType="text/plain"
                            if file_path.endswith(".txt")
                            else "text/markdown",
                        )
                    )

    return ListResourcesResult(resources=resources)


@server.read_resource()
async def handle_read_resource(uri: str) -> ReadResourceResult:
    """Read a specific resource"""
    try:
        # Parse OCR://job/{job_id}/{file_type} URI
        if uri.startswith("ocr://job/"):
            parts = uri.replace("ocr://job/", "").split("/", 1)
            if len(parts) == 2:
                job_id, file_type = parts

                if job_id in active_jobs and active_jobs[job_id].output_files:
                    file_path = active_jobs[job_id].output_files.get(file_type)
                    if file_path and os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        return ReadResourceResult(
                            contents=[
                                TextContent(
                                    type="text",
                                    text=content,
                                )
                            ]
                        )

        raise ValueError(f"Resource not found: {uri}")

    except Exception as e:
        logger.error(f"Error reading resource {uri}: {str(e)}")
        raise ValueError(f"Error reading resource: {str(e)}")


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available tools"""
    tools = [
        Tool(
            name="process_pdf",
            description="Process a PDF file with OCR and LLM correction",
            inputSchema={
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": "Path to the PDF file to process",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional output path for results",
                    },
                    "provider": {
                        "type": "string",
                        "enum": ["openai", "claude", "lm-studio"],
                        "description": "LLM provider to use for correction",
                    },
                    "model": {
                        "type": "string",
                        "description": "Model name (for lm-studio provider)",
                    },
                },
                "required": ["pdf_path"],
            },
        ),
        Tool(
            name="get_job_status",
            description="Get the status of a processing job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "Job ID to check status for",
                    },
                },
                "required": ["job_id"],
            },
        ),
        Tool(
            name="list_jobs",
            description="List all processing jobs",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="delete_job",
            description="Delete a job and its associated files",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "Job ID to delete",
                    },
                },
                "required": ["job_id"],
            },
        ),
    ]

    return ListToolsResult(tools=tools)


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls"""

    if name == "process_pdf":
        return await handle_process_pdf(arguments)
    elif name == "get_job_status":
        return await handle_get_job_status(arguments)
    elif name == "list_jobs":
        return await handle_list_jobs(arguments)
    elif name == "delete_job":
        return await handle_delete_job(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_process_pdf(arguments: Dict[str, Any]) -> CallToolResult:
    """Process a PDF file"""
    pdf_path = arguments.get("pdf_path")
    output_path = arguments.get("output_path")
    provider = arguments.get("provider")
    model = arguments.get("model")

    # Validate PDF file
    if not pdf_path or not validate_pdf_file(pdf_path):
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Error: Invalid PDF file path or file not found",
                )
            ],
            isError=True,
        )

    # Validate output path if provided
    if output_path and not validate_output_path(output_path):
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text="Error: Invalid output path or insufficient permissions",
                )
            ],
            isError=True,
        )

    # Create job ID
    job_id = str(uuid.uuid4())

    # Initialize job
    active_jobs[job_id] = JobStatus(
        job_id=job_id,
        status="pending",
        progress=0.0,
        message="Job queued for processing",
    )

    # Start background processing
    asyncio.create_task(process_pdf_job(job_id, pdf_path, output_path, provider, model))

    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=f"PDF processing started. Job ID: {job_id}\n"
                f"PDF path: {pdf_path}\n"
                f"Output path: {output_path or 'Default'}\n"
                f"Provider: {provider or 'Default'}\n"
                f"Model: {model or 'Default'}",
            )
        ]
    )


async def handle_get_job_status(arguments: Dict[str, Any]) -> CallToolResult:
    """Get job status"""
    job_id = arguments.get("job_id")

    if not job_id or job_id not in active_jobs:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: Job not found: {job_id}",
                )
            ],
            isError=True,
        )

    job = active_jobs[job_id]
    status_dict = job.to_dict()

    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=json.dumps(status_dict, indent=2),
            )
        ]
    )


async def handle_list_jobs(arguments: Dict[str, Any]) -> CallToolResult:
    """List all jobs"""
    jobs_list = [job.to_dict() for job in active_jobs.values()]

    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "jobs": jobs_list,
                        "total": len(jobs_list),
                    },
                    indent=2,
                ),
            )
        ]
    )


async def handle_delete_job(arguments: Dict[str, Any]) -> CallToolResult:
    """Delete a job"""
    job_id = arguments.get("job_id")

    if not job_id or job_id not in active_jobs:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: Job not found: {job_id}",
                )
            ],
            isError=True,
        )

    # Remove job from active jobs
    del active_jobs[job_id]

    # Optionally clean up job files
    job_dir = RESULTS_DIR_PATH / job_id
    if job_dir.exists():
        import shutil

        shutil.rmtree(job_dir)

    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=f"Job {job_id} deleted successfully",
            )
        ]
    )


async def main():
    """Main entry point"""
    # Log configuration
    logger.info("🚀 Starting LLM-Aided OCR MCP Server")
    logger.info(f"📁 Results directory: {RESULTS_DIR_PATH.absolute()}")

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="llm-aided-ocr-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
