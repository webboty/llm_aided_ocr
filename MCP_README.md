# LLM-Aided OCR MCP Server

This document provides comprehensive instructions for using the LLM-Aided OCR Model Context Protocol (MCP) server.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [MCP Tools](#mcp-tools)
4. [MCP Resources](#mcp-resources)
5. [Usage Examples](#usage-examples)
6. [Integration with Claude Desktop](#integration-with-claude-desktop)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create or update your `.env` file:
```bash
RESULTS_DIR=results
```

### 3. Start MCP Server
The MCP server runs via stdio and is typically started by an MCP client (like Claude Desktop).

### 4. Configure Claude Desktop
Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "llm-aided-ocr": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/llm_aided_ocr",
      "env": {
        "RESULTS_DIR": "results"
      }
    }
  }
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|----------|-------------|
| `RESULTS_DIR` | `results` | Directory for storing results |

### MCP Configuration

The MCP server can be configured through the standard MCP client configuration format. See `mcp_config.json` for an example configuration.

## MCP Tools

### 1. process_pdf
Process a PDF file with OCR and LLM correction.

**Parameters:**
- `pdf_path` (required, string): Path to the PDF file to process
- `output_path` (optional, string): Custom output path for results
- `provider` (optional, string): LLM provider (openai, claude, lm-studio)
- `model` (optional, string): Model name (for lm-studio provider)
- `ocr_languages` (optional, string): OCR languages to use (e.g., "eng+rus+deu")

**Returns:**
Job ID for tracking processing status

**Example:**
```python
# Process a PDF file with custom OCR languages
result = await client.call_tool("process_pdf", {
    "pdf_path": "/path/to/document.pdf",
    "provider": "openai",
    "output_path": "/custom/output",
    "ocr_languages": "eng+rus+deu+fra"
})
```

### 2. get_job_status
Get the status of a processing job.

**Parameters:**
- `job_id` (required, string): Job ID to check status for

**Returns:**
Detailed job status including progress, output files, and error information

**Example:**
```python
# Check job status
result = await client.call_tool("get_job_status", {
    "job_id": "12345678-1234-1234-1234-123456789abc"
})
```

### 3. list_jobs
List all processing jobs.

**Parameters:**
None

**Returns:**
List of all jobs with their current statuses

**Example:**
```python
# List all jobs
result = await client.call_tool("list_jobs", {})
```

### 4. delete_job
Delete a job and its associated files.

**Parameters:**
- `job_id` (required, string): Job ID to delete

**Returns:**
Confirmation message

**Example:**
```python
# Delete a job
result = await client.call_tool("delete_job", {
    "job_id": "12345678-1234-1234-1234-123456789abc"
})
```

## MCP Resources

The MCP server exposes processed files as resources that can be read by MCP clients.

### Resource Format
Resources are available in the format: `ocr://job/{job_id}/{file_type}`

**File Types:**
- `raw_ocr`: Raw OCR output text file
- `corrected`: LLM-corrected markdown file

**Example:**
```
ocr://job/12345678-1234-1234-1234-123456789abc/raw_ocr
ocr://job/12345678-1234-1234-1234-123456789abc/corrected
```

### Reading Resources
Resources can be read using the standard MCP resource reading interface:

```python
# Read a resource
result = await client.read_resource("ocr://job/12345678-1234-1234-1234-123456789abc/corrected")
```

## Usage Examples

### Basic PDF Processing

```python
# Process a PDF file
job_result = await client.call_tool("process_pdf", {
    "pdf_path": "/path/to/document.pdf",
    "provider": "openai"
})

job_id = job_result.content[0].text.split("Job ID: ")[1].split("\n")[0]
print(f"Job submitted: {job_id}")

# Wait for completion (polling)
import time
while True:
    status_result = await client.call_tool("get_job_status", {"job_id": job_id})
    status_data = json.loads(status_result.content[0].text)
    
    if status_data["status"] == "completed":
        print("Processing completed!")
        break
    elif status_data["status"] == "failed":
        print(f"Processing failed: {status_data['error']}")
        break
    
    print(f"Progress: {status_data.get('progress', 0):.1%} - {status_data.get('message')}")
    time.sleep(5)

# Read the corrected output
corrected_result = await client.read_resource(f"ocr://job/{job_id}/corrected")
corrected_text = corrected_result.contents[0].text
print("Corrected text:", corrected_text[:500] + "...")
```

### Advanced Processing with Custom Settings

```python
# Process with custom provider and model
job_result = await client.call_tool("process_pdf", {
    "pdf_path": "/path/to/document.pdf",
    "provider": "lm-studio",
    "model": "qwen/qwen3-vl-30b",
    "output_path": "/custom/output/document_processed"
})

job_id = job_result.content[0].text.split("Job ID: ")[1].split("\n")[0]

# Monitor progress
while True:
    status_result = await client.call_tool("get_job_status", {"job_id": job_id})
    status_data = json.loads(status_result.content[0].text)
    
    if status_data["status"] in ["completed", "failed"]:
        break
    
    print(f"Status: {status_data['status']} - {status_data['message']}")
    time.sleep(3)

# List all output files for the job
if status_data["status"] == "completed":
    print("Output files:", status_data["output_files"])
    
    # Read both raw and corrected outputs
    raw_result = await client.read_resource(f"ocr://job/{job_id}/raw_ocr")
    corrected_result = await client.read_resource(f"ocr://job/{job_id}/corrected")
    
    print("Raw OCR:", raw_result.contents[0].text[:200] + "...")
    print("Corrected:", corrected_result.contents[0].text[:200] + "...")
```

### Job Management

```python
# List all jobs
jobs_result = await client.call_tool("list_jobs", {})
jobs_data = json.loads(jobs_result.content[0].text)

print(f"Total jobs: {jobs_data['total']}")
for job in jobs_data['jobs']:
    print(f"Job {job['job_id']}: {job['status']} - {job['message']}")

# Clean up old completed jobs
for job in jobs_data['jobs']:
    if job['status'] == 'completed':
        # Delete old completed jobs (optional cleanup)
        delete_result = await client.call_tool("delete_job", {
            "job_id": job['job_id']
        })
        print(f"Deleted job: {job['job_id']}")
```

## Integration with Claude Desktop

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Claude Desktop
Edit your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "llm-aided-ocr": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/absolute/path/to/llm_aided_ocr",
      "env": {
        "RESULTS_DIR": "results"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop
Restart Claude Desktop to load the new MCP server.

### Step 4: Use in Claude
You can now use the OCR tools directly in Claude:

```
Please process the PDF file at /path/to/document.pdf using OpenAI for correction.
```

Claude will automatically:
1. Call the `process_pdf` tool
2. Monitor the job status
3. Retrieve the corrected output
4. Present the results to you

### Example Claude Conversations

**Basic Processing:**
```
User: Process this PDF for me: /Users/me/Documents/report.pdf

Claude: I'll process that PDF file for you using OCR and LLM correction.

[Claude calls process_pdf tool]

Claude: I've started processing your PDF. The job ID is 12345678-1234-1234-1234-123456789abc. Let me check the status...

[Claude monitors job status]

Claude: Your PDF has been processed successfully! Here's the corrected text:

[Corrected text content]
```

**Advanced Processing:**
```
User: Process this scanned contract using LM Studio with the Qwen model: /path/to/contract.pdf

Claude: I'll process your contract PDF using LM Studio with the Qwen model for OCR correction.

[Claude calls process_pdf with custom provider and model]

Claude: The contract has been processed with LM Studio. Here are the results:

[Corrected contract text]
```

## Troubleshooting

### Common Issues

**1. MCP Server Not Starting**
```
Error: ModuleNotFoundError: No module named 'mcp'
```
**Solution:** Install MCP dependencies:
```bash
pip install mcp
```

**2. PDF File Not Found**
```
Error: Invalid PDF file path or file not found
```
**Solution:** Ensure the PDF path is absolute and the file exists with proper permissions.

**3. Job Processing Fails**
```
Error: Processing failed: Tesseract error
```
**Solution:** Check that Tesseract OCR is installed and accessible:
```bash
tesseract --version
```

**4. Resource Not Found**
```
Error: Resource not found: ocr://job/123/corrected
```
**Solution:** Ensure the job has completed successfully before trying to read resources.

**5. Claude Desktop Integration Issues**
```
Error: MCP server failed to start
```
**Solution:** 
- Check the absolute path in the configuration
- Ensure Python is in the system PATH
- Verify all dependencies are installed
- Check Claude Desktop logs for detailed errors

### Debug Mode

Enable debug logging by setting the log level:
```bash
export LOG_LEVEL=DEBUG
python mcp_server.py
```

### Testing the MCP Server

You can test the MCP server independently using the MCP CLI:

```bash
# Install MCP CLI
pip install mcp-cli

# Test the server
mcp-cli stdio python mcp_server.py
```

### Performance Optimization

**For Large Files:**
- Monitor job progress regularly
- Consider processing in batches for multiple files
- Ensure sufficient disk space for output files

**For High Volume:**
- Clean up completed jobs regularly
- Monitor the RESULTS_DIR size
- Consider using custom output paths for better organization

---

## Support

For additional support:
1. Check the server logs for error details
2. Verify your configuration in `.env`
3. Test with the provided examples
4. Review this documentation for common solutions

For the most up-to-date information, see the project repository.