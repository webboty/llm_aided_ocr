# LLM-Aided OCR API

This document describes REST API for LLM-Aided OCR project.

## Configuration

Add these settings to your `.env` file:

```bash
# API Authentication (optional but recommended)
API_SECRET_TOKEN=your-secret-token-here

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Output Directory
RESULTS_DIR=results
```

### Security
- **API_SECRET_TOKEN**: If set, all API requests require Bearer token authentication
- If not set, API runs without authentication (not recommended for production)

### Server Configuration
- **API_HOST**: Server bind address (default: 0.0.0.0)
- **API_PORT**: Server port (default: 8000)
- **RESULTS_DIR**: Directory for storing results (default: results)

## Starting API Server

```bash
# Install dependencies first
pip install -r requirements.txt

# Start API server
python api_server.py
```

The API will be available at `http://localhost:8000` (or your configured host/port)

## API Endpoints

### 1. Health Check
**GET** `/health`

Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-11T10:30:00"
}
```

### 2. Process PDF from Path
**POST** `/process`

Process a PDF file from a file path.

**Form Data:**
- `pdf_path` (required): Path to the PDF file
- `output_path` (optional): Output directory for results
- `provider` (optional): LLM provider (openai, claude, lm-studio)
- `model` (optional): Model name (for lm-studio)

**Response:**
```json
{
  "job_id": "12345678-1234-1234-1234-123456789abc",
  "status": "pending",
  "message": "PDF processing started",
  "pdf_path": "/path/to/file.pdf",
  "output_path": "/path/to/output"
}
```

### 3. Upload and Process PDF
**POST** `/upload`

Upload a PDF file and process it.

**Form Data:**
- `file` (required): PDF file to upload
- `output_path` (optional): Output directory for results
- `provider` (optional): LLM provider (openai, claude, lm-studio)
- `model` (optional): Model name (for lm-studio)

**Response:**
```json
{
  "job_id": "12345678-1234-1234-1234-123456789abc",
  "status": "pending",
  "message": "PDF uploaded and processing started",
  "filename": "document.pdf",
  "output_path": "/path/to/output"
}
```

### 4. Get Job Status
**GET** `/job/{job_id}`

Get the status of a processing job.

**Response:**
```json
{
  "job_id": "12345678-1234-1234-1234-123456789abc",
  "status": "completed",
  "progress": 1.0,
  "message": "Processing completed successfully",
  "output_files": {
    "raw_ocr": "/path/to/raw_ocr_output.txt",
    "corrected": "/path/to/corrected.md"
  },
  "error": null,
  "created_at": "2025-12-11T10:30:00",
  "updated_at": "2025-12-11T10:35:00"
}
```

**Job Status Values:**
- `pending`: Job is queued
- `processing`: Job is currently being processed
- `completed`: Job finished successfully
- `failed`: Job failed with an error

### 5. Download Output File
**GET** `/download/{job_id}/{filename}`

Download a processed output file.

**Parameters:**
- `job_id`: ID of the job
- `filename`: Name of the file to download

### 6. List All Jobs
**GET** `/jobs`

List all jobs and their statuses.

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "12345678-1234-1234-1234-123456789abc",
      "status": "completed",
      "progress": 1.0,
      "message": "Processing completed successfully",
      "output_files": {
        "raw_ocr": "/path/to/raw_ocr_output.txt",
        "corrected": "/path/to/corrected.md"
      },
      "error": null,
      "created_at": "2025-12-11T10:30:00",
      "updated_at": "2025-12-11T10:35:00"
    }
  ],
  "total": 1
}
```

### 7. Delete Job
**DELETE** `/job/{job_id}`

Delete a job and its associated files.

**Response:**
```json
{
  "message": "Job deleted successfully"
}
```

## Usage Examples

### Using curl

**Without Authentication (if API_SECRET_TOKEN not set):**
```bash
# Process PDF from path
curl -X POST "http://localhost:8000/process" \
  -F "pdf_path=/path/to/document.pdf" \
  -F "provider=openai"

# Upload and process PDF
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/document.pdf" \
  -F "provider=lm-studio" \
  -F "model=qwen/qwen3-vl-30b"

# Check job status
curl "http://localhost:8000/job/12345678-1234-1234-1234-123456789abc"

# Download output file
curl "http://localhost:8000/download/12345678-1234-1234-1234-123456789abc/document_llm_corrected.md" \
  -o corrected_output.md
```

**With Authentication (if API_SECRET_TOKEN is set):**
```bash
# Set token as variable
TOKEN="your-secret-token-here"

# Process PDF from path
curl -X POST "http://localhost:8000/process" \
  -H "Authorization: Bearer $TOKEN" \
  -F "pdf_path=/path/to/document.pdf" \
  -F "provider=openai"

# Upload and process PDF
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "provider=lm-studio" \
  -F "model=qwen/qwen3-vl-30b"

# Check job status
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/job/12345678-1234-1234-1234-123456789abc"

# Download output file
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/download/12345678-1234-1234-1234-123456789abc/document_llm_corrected.md" \
  -o corrected_output.md
```

### Using Python

```python
import requests

# Configuration
API_BASE_URL = "http://localhost:8000"
API_TOKEN = "your-secret-token-here"  # Set to None if no authentication

# Setup headers
headers = {}
if API_TOKEN:
    headers["Authorization"] = f"Bearer {API_TOKEN}"

# Upload and process PDF
with open("document.pdf", "rb") as f:
    files = {"file": f}
    data = {"provider": "openai"}
    response = requests.post(
        f"{API_BASE_URL}/upload", 
        files=files, 
        data=data, 
        headers=headers
    )
    response.raise_for_status()
    job_id = response.json()["job_id"]
    print(f"Job submitted with ID: {job_id}")

# Check status
status_response = requests.get(
    f"{API_BASE_URL}/job/{job_id}", 
    headers=headers
)
status_response.raise_for_status()
job_status = status_response.json()
print(f"Job status: {job_status['status']}")

if job_status["status"] == "completed":
    # Download corrected file
    corrected_url = f"{API_BASE_URL}/download/{job_id}/document_llm_corrected.md"
    corrected_response = requests.get(corrected_url, headers=headers)
    corrected_response.raise_for_status()
    with open("corrected_output.md", "wb") as f:
        f.write(corrected_response.content)
    print("File downloaded successfully!")
elif job_status["status"] == "failed":
    print(f"Processing failed: {job_status.get('error', 'Unknown error')}")
```

## Output Files

The API generates two output files for each processed PDF:

1. **Raw OCR Output** (`{filename}__raw_ocr_output.txt`): The raw text extracted by Tesseract OCR
2. **LLM Corrected Output** (`{filename}_llm_corrected.md`): The corrected and formatted text after LLM processing

## File Storage

- Uploaded files are stored in `results/uploads/{job_id}/`
- Output files are stored in:
  - Specified `output_path` if provided
  - `results/{job_id}/` if no output path is specified

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid file, missing parameters)
- `404`: Job or file not found
- `500`: Internal server error

Error responses include descriptive messages:
```json
{
  "detail": "Only PDF files are allowed"
}
```

## Testing

Use the provided test script to verify API functionality:

```bash
python test_api.py
```

Make sure the API server is running before executing the test script.