#!/usr/bin/env python3
"""
Test script for LLM-Aided OCR MCP Server
"""

import asyncio
import json
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import (
    server,
    active_jobs,
    handle_list_tools,
    handle_list_resources,
    handle_process_pdf,
    handle_get_job_status,
    handle_list_jobs,
    handle_delete_job,
    handle_read_resource,
)
from mcp.server.models import InitializationOptions


async def test_mcp_server():
    """Test MCP server functionality"""
    print("🧪 Testing LLM-Aided OCR MCP Server")
    print("=" * 50)

    # Test 1: List tools
    print("\n1. Testing list_tools...")
    try:
        tools_result = await handle_list_tools()
        print(f"✅ Found {len(tools_result.tools)} tools:")
        for tool in tools_result.tools:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        return

    # Test 2: List resources (should be empty initially)
    print("\n2. Testing list_resources...")
    try:
        resources_result = await handle_list_resources()
        print(f"✅ Found {len(resources_result.resources)} resources")
    except Exception as e:
        print(f"❌ Error listing resources: {e}")

    # Test 3: Process a PDF (if test file exists)
    test_pdf = Path("test-sample.pdf")
    if test_pdf.exists():
        print(f"\n3. Testing process_pdf with {test_pdf}...")
        try:
            process_result = await handle_process_pdf(
                {"pdf_path": str(test_pdf.absolute()), "provider": "openai"}
            )

            # Extract job ID from result
            result_text = process_result.content[0].text
            job_id_line = [
                line for line in result_text.split("\n") if "Job ID:" in line
            ][0]
            job_id = job_id_line.split("Job ID: ")[1].strip()

            print(f"✅ Job submitted with ID: {job_id}")

            # Test 4: Get job status
            print(f"\n4. Testing get_job_status for {job_id}...")
            status_result = await handle_get_job_status({"job_id": job_id})
            status_data = json.loads(status_result.content[0].text)
            print(f"✅ Job status: {status_data['status']} - {status_data['message']}")

            # Test 5: List jobs
            print(f"\n5. Testing list_jobs...")
            jobs_result = await handle_list_jobs({})
            jobs_data = json.loads(jobs_result.content[0].text)
            print(f"✅ Found {jobs_data['total']} jobs")

            # Wait a bit for processing to potentially complete
            print(f"\n6. Waiting 5 seconds for processing...")
            await asyncio.sleep(5)

            # Check status again
            status_result = await handle_get_job_status({"job_id": job_id})
            status_data = json.loads(status_result.content[0].text)
            print(f"✅ Updated job status: {status_data['status']}")

            # Test 7: List resources again (might have new resources)
            print(f"\n7. Testing list_resources after processing...")
            resources_result = await handle_list_resources()
            print(f"✅ Found {len(resources_result.resources)} resources")
            for resource in resources_result.resources:
                print(f"   - {resource.name}: {resource.description}")

            # Test 8: Clean up - delete job
            print(f"\n8. Testing delete_job...")
            delete_result = await handle_delete_job({"job_id": job_id})
            print(f"✅ {delete_result.content[0].text}")

        except Exception as e:
            print(f"❌ Error in processing test: {e}")
    else:
        print(f"\n3. Skipping process_pdf test (no test PDF found at {test_pdf})")

    print("\n" + "=" * 50)
    print("🎉 MCP Server testing completed!")


async def test_error_handling():
    """Test error handling"""
    print("\n🔧 Testing Error Handling")
    print("=" * 30)

    # Test invalid PDF path
    print("\n1. Testing invalid PDF path...")
    try:
        result = await handle_process_pdf({"pdf_path": "/nonexistent/file.pdf"})
        if result.isError:
            print("✅ Correctly handled invalid PDF path")
        else:
            print("❌ Should have returned error for invalid PDF")
    except Exception as e:
        print(f"✅ Correctly raised exception for invalid PDF: {e}")

    # Test invalid job ID
    print("\n2. Testing invalid job ID...")
    try:
        result = await handle_get_job_status({"job_id": "invalid-job-id"})
        if result.isError:
            print("✅ Correctly handled invalid job ID")
        else:
            print("❌ Should have returned error for invalid job ID")
    except Exception as e:
        print(f"✅ Correctly raised exception for invalid job ID: {e}")

    # Test invalid resource
    print("\n3. Testing invalid resource...")
    try:
        result = await handle_read_resource("ocr://job/invalid-job-id/corrected")
        print("❌ Should have raised exception for invalid resource")
    except Exception as e:
        print(f"✅ Correctly raised exception for invalid resource: {e}")


async def main():
    """Main test function"""
    try:
        await test_mcp_server()
        await test_error_handling()
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
