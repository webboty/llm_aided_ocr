# LLM-Aided OCR API Documentation

This document provides comprehensive instructions for using the LLM-Aided OCR REST API.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
5. [Usage Examples](#usage-examples)
6. [Error Handling](#error-handling)
7. [File Management](#file-management)
8. [Integration Examples](#integration-examples)
9. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create or update your `.env` file:
```bash
# Basic configuration
API_HOST=0.0.0.0
API_PORT=8000
RESULTS_DIR=results

# Optional: Enable authentication
API_SECRET_TOKEN=your-secure-token-here
```

### 3. Start Server
```bash
python api_server.py
```

The API will be available at `http://localhost:8000` (or your configured host/port).

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|----------|-------------|
| `API_HOST` | `0.0.0.0` | Server bind address |
| `API_PORT` | `8000` | Server port |
| `RESULTS_DIR` | `results` | Directory for storing results |
| `API_SECRET_TOKEN` | `None` | Authentication token (optional) |

### Security Recommendations

**For Production:**
- Always set `API_SECRET_TOKEN`
- Use HTTPS in production
- Restrict `API_HOST` to specific interfaces if needed
- Set appropriate file permissions on `RESULTS_DIR`

**For Development:**
- Leave `API_SECRET_TOKEN` unset for easier testing
- Use `localhost` or `127.0.0.1` for `API_HOST`

## Authentication

### Bearer Token Authentication

If `API_SECRET_TOKEN` is set, all API endpoints require authentication:

```bash
# Add Authorization header
Authorization: Bearer your-secret-token-here
```

### Authentication Flow

1. **Without Token** (development):
   ```bash
   curl http://localhost:8000/health
   ```

2. **With Token** (production):
   ```bash
   curl -H "Authorization: Bearer your-token" http://localhost:8000/health
   ```

### Error Response (401 Unauthorized)
```json
{
  "detail": "Invalid or missing authentication token"
}
```

## API Endpoints

### Base URL
```
http://localhost:8000
```

### 1. Health Check
**GET** `/health`

Check if the API server is running and responsive.

**Request:**
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-11T10:30:00.123456"
}
```

### 2. Process PDF from Path
**POST** `/process`

Process a PDF file from a file system path.

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|--------|----------|-------------|
| `pdf_path` | string | Yes | Absolute path to PDF file |
| `output_path` | string | No | Custom output directory |
| `provider` | string | No | LLM provider (openai, claude, lm-studio) |
| `model` | string | No | Model name (for lm-studio) |
| `ocr_languages` | string | No | OCR languages (e.g., "eng+rus+deu") |

**Request:**
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Authorization: Bearer TOKEN" \
  -F "pdf_path=/path/to/document.pdf" \
  -F "provider=openai" \
  -F "output_path=/custom/output" \
  -F "ocr_languages=eng+rus+deu"
```

**Response (200 OK):**
```json
{
  "job_id": "12345678-1234-1234-1234-123456789abc",
  "status": "pending",
  "message": "PDF processing started",
  "pdf_path": "/path/to/document.pdf",
  "output_path": "/custom/output"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid PDF path or file not found
- `400 Bad Request`: Invalid output path or insufficient permissions

### 3. Upload and Process PDF
**POST** `/upload`

Upload a PDF file and process it.

**Request Parameters:**
| Parameter | Type | Required | Description |
|-----------|--------|----------|-------------|
| `file` | file | Yes | PDF file to upload |
| `output_path` | string | No | Custom output directory |
| `provider` | string | No | LLM provider |
| `model` | string | No | Model name |

**Request:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "provider=lm-studio" \
  -F "model=qwen/qwen3-vl-30b"
```

**Response (200 OK):**
```json
{
  "job_id": "12345678-1234-1234-1234-123456789abc",
  "status": "pending",
  "message": "PDF uploaded and processing started",
  "filename": "document.pdf",
  "output_path": null
}
```

### 4. Get Job Status
**GET** `/job/{job_id}`

Get the current status and progress of a processing job.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|--------|-------------|
| `job_id` | string | Unique job identifier |

**Request:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/job/12345678-1234-1234-1234-123456789abc"
```

**Response (200 OK):**
```json
{
  "job_id": "12345678-1234-1234-1234-123456789abc",
  "status": "completed",
  "progress": 1.0,
  "message": "Processing completed successfully",
  "output_files": {
    "raw_ocr": "/path/to/document__raw_ocr_output.txt",
    "corrected": "/path/to/document_llm_corrected.md"
  },
  "error": null,
  "created_at": "2025-12-11T10:30:00",
  "updated_at": "2025-12-11T10:35:00"
}
```

**Job Status Values:**
- `pending`: Job is queued for processing
- `processing`: Job is currently being processed
- `completed`: Job finished successfully
- `failed`: Job failed with an error

### 5. Download Output File
**GET** `/download/{job_id}/{filename}`

Download a processed output file.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|--------|-------------|
| `job_id` | string | Job identifier |
| `filename` | string | Name of file to download |

**Request:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/download/12345678-1234-1234-1234-123456789abc/document_llm_corrected.md" \
  -o corrected_output.md
```

**Response:** File content with appropriate MIME type

### 6. List All Jobs
**GET** `/jobs`

Get a list of all jobs and their current statuses.

**Request:**
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8000/jobs
```

**Response (200 OK):**
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

Delete a job and all its associated files.

**Request:**
```bash
curl -X DELETE -H "Authorization: Bearer TOKEN" \
  "http://localhost:8000/job/12345678-1234-1234-1234-123456789abc"
```

**Response (200 OK):**
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

## Error Handling

### HTTP Status Codes

| Code | Description | Example Response |
|-------|-------------|-----------------|
| `200` | Success | Varies by endpoint |
| `400` | Bad Request | `{"detail": "Invalid PDF file path"}` |
| `401` | Unauthorized | `{"detail": "Invalid authentication token"}` |
| `404` | Not Found | `{"detail": "Job not found"}` |
| `500` | Internal Error | `{"detail": "Internal server error"}` |

### Common Error Scenarios

**Invalid PDF File:**
```json
{
  "detail": "Invalid PDF file path or file not found"
}
```

**Missing Authentication:**
```json
{
  "detail": "Invalid or missing authentication token"
}
```

**Job Not Found:**
```json
{
  "detail": "Job not found"
}
```

**Processing Failed:**
```json
{
  "job_id": "12345678-1234-1234-1234-123456789abc",
  "status": "failed",
  "error": "OCR processing failed: Tesseract error",
  "message": "Processing failed: OCR processing failed: Tesseract error"
}
```

## File Management

### Output File Structure

For each processed PDF, the API generates:

1. **Raw OCR Output**: `{filename}__raw_ocr_output.txt`
   - Direct output from Tesseract OCR
   - Contains all extracted text without correction

2. **LLM Corrected Output**: `{filename}_llm_corrected.md`
   - Corrected and formatted text
   - Markdown formatting applied
   - OCR errors fixed by LLM

### Storage Locations

**Default Storage:**
```
results/
├── uploads/
│   └── {job_id}/
│       └── uploaded_file.pdf
└── {job_id}/
    ├── document__raw_ocr_output.txt
    └── document_llm_corrected.md
```

**Custom Output Path:**
If `output_path` is specified, files are saved directly to that location.

### File Cleanup

- Jobs can be deleted via `DELETE /job/{job_id}`
- This removes all associated files and job data
- Use for storage management and privacy

## Integration Examples

### Python Integration

```python
import requests
import time
import json
from pathlib import Path

class LLMAidedOCRClient:
    def __init__(self, base_url="http://localhost:8000", token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def upload_and_process(self, pdf_path, provider="openai", model=None, output_path=None):
        """Upload and process a PDF file"""
        with open(pdf_path, "rb") as f:
            files = {"file": f}
            data = {
                "provider": provider,
                "output_path": output_path
            }
            if model:
                data["model"] = model
            
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                data=data,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()["job_id"]
    
    def get_job_status(self, job_id):
        """Get job status"""
        response = requests.get(
            f"{self.base_url}/job/{job_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(self, job_id, poll_interval=5, timeout=300):
        """Wait for job completion"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)
            
            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                raise Exception(f"Processing failed: {status.get('error')}")
            
            print(f"Progress: {status.get('progress', 0):.1%} - {status.get('message')}")
            time.sleep(poll_interval)
        
        raise TimeoutError("Job processing timed out")
    
    def download_file(self, job_id, filename, output_path):
        """Download output file"""
        response = requests.get(
            f"{self.base_url}/download/{job_id}/{filename}",
            headers=self.headers
        )
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return output_path

# Usage Example
client = LLMAidedOCRClient(
    base_url="http://localhost:8000",
    token="your-secret-token"
)

# Process PDF
job_id = client.upload_and_process(
    "document.pdf",
    provider="openai"
)

print(f"Job submitted: {job_id}")

# Wait for completion
result = client.wait_for_completion(job_id)
print("Processing completed!")

# Download results
client.download_file(
    job_id,
    "document_llm_corrected.md",
    "corrected_output.md"
)

client.download_file(
    job_id,
    "document__raw_ocr_output.txt",
    "raw_output.txt"
)

print("Files downloaded successfully!")
```

### Node.js Integration

```javascript
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

class LLMAidedOCRClient {
    constructor(baseUrl = 'http://localhost:8000', token = null) {
        this.baseUrl = baseUrl;
        this.token = token;
        this.config = {};
        if (token) {
            this.config.headers = { 'Authorization': `Bearer ${token}` };
        }
    }

    async uploadAndProcess(pdfPath, options = {}) {
        const formData = new FormData();
        formData.append('file', fs.createReadStream(pdfPath));
        
        if (options.provider) formData.append('provider', options.provider);
        if (options.model) formData.append('model', options.model);
        if (options.outputPath) formData.append('output_path', options.outputPath);

        const response = await axios.post(`${this.baseUrl}/upload`, formData, {
            ...this.config,
            headers: {
                ...formData.getHeaders(),
                ...this.config.headers
            }
        });

        return response.data.job_id;
    }

    async getJobStatus(jobId) {
        const response = await axios.get(`${this.baseUrl}/job/${jobId}`, this.config);
        return response.data;
    }

    async waitForCompletion(jobId, pollInterval = 5000, timeout = 300000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const status = await this.getJobStatus(jobId);
            
            if (status.status === 'completed') {
                return status;
            } else if (status.status === 'failed') {
                throw new Error(`Processing failed: ${status.error}`);
            }
            
            console.log(`Progress: ${(status.progress || 0) * 100}% - ${status.message}`);
            await new Promise(resolve => setTimeout(resolve, pollInterval));
        }
        
        throw new Error('Job processing timed out');
    }

    async downloadFile(jobId, filename, outputPath) {
        const response = await axios.get(`${this.baseUrl}/download/${jobId}/${filename}`, {
            ...this.config,
            responseType: 'stream'
        });

        const writer = fs.createWriteStream(outputPath);
        response.data.pipe(writer);

        return new Promise((resolve, reject) => {
            writer.on('finish', resolve);
            writer.on('error', reject);
        });
    }
}

// Usage Example
async function main() {
    const client = new LLMAidedOCRClient(
        'http://localhost:8000',
        'your-secret-token'
    );

    try {
        // Process PDF
        const jobId = await client.uploadAndProcess('document.pdf', {
            provider: 'openai'
        });
        console.log(`Job submitted: ${jobId}`);

        // Wait for completion
        const result = await client.waitForCompletion(jobId);
        console.log('Processing completed!');

        // Download results
        await client.downloadFile(jobId, 'document_llm_corrected.md', 'corrected_output.md');
        await client.downloadFile(jobId, 'document__raw_ocr_output.txt', 'raw_output.txt');
        
        console.log('Files downloaded successfully!');
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
```

## Troubleshooting

### Common Issues

**1. Connection Refused**
```
Error: Connection refused
```
**Solution:** Ensure the API server is running and check the host/port configuration.

**2. Authentication Failed**
```
401 Unauthorized
```
**Solution:** Verify `API_SECRET_TOKEN` in your `.env` file matches the token in your requests.

**3. File Not Found**
```
400 Bad Request: Invalid PDF file path
```
**Solution:** Check that the file path is absolute and the file exists with proper permissions.

**4. Processing Timeout**
```
Job status remains "processing" for too long
```
**Solution:** Large PDFs may take longer. Check server logs for errors.

**5. Insufficient Permissions**
```
400 Bad Request: Invalid output path
```
**Solution:** Ensure the output directory exists and is writable.

### Debug Mode

Enable debug logging by setting the log level:
```bash
export LOG_LEVEL=DEBUG
python api_server.py
```

### Server Logs

Monitor server logs for detailed information:
```bash
python api_server.py 2>&1 | tee api.log
```

### Performance Optimization

**For Large Files:**
- Increase timeout values in client code
- Monitor server resources
- Consider processing in batches

**For High Volume:**
- Use a reverse proxy (nginx) for load balancing
- Implement rate limiting
- Monitor job queue size

---

## Support

For additional support:
1. Check the server logs for error details
2. Verify your configuration in `.env`
3. Test with the provided `test_api.py` script
4. Review this documentation for common solutions

For the most up-to-date information, see the project repository.