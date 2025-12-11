#!/usr/bin/env python3
"""
Test script for LLM-Aided OCR API
"""

import requests
import json
import time
import os

API_BASE_URL = "http://localhost:8000"
API_TOKEN = None  # Set to your token if authentication is enabled


def get_headers():
    """Get headers with authentication if token is set"""
    headers = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    return headers


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{API_BASE_URL}/health", headers=get_headers())
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_process_pdf_from_path():
    """Test processing PDF from file path"""
    print("Testing PDF processing from path...")

    # Use the sample PDF that comes with the project
    pdf_path = os.path.abspath("160301289-Warren-Buffett-Katharine-Graham-Letter.pdf")

    if not os.path.exists(pdf_path):
        print(f"Sample PDF not found at: {pdf_path}")
        return

    data = {
        "pdf_path": pdf_path,
        "provider": "openai",  # Change as needed
        "output_path": None,  # Use default results directory
    }

    response = requests.post(
        f"{API_BASE_URL}/process", data=data, headers=get_headers()
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 200:
        job_id = response.json()["job_id"]
        print(f"Job started with ID: {job_id}")

        # Poll for completion
        print("Polling for job completion...")
        while True:
            status_response = requests.get(
                f"{API_BASE_URL}/job/{job_id}", headers=get_headers()
            )
            if status_response.status_code == 200:
                job_status = status_response.json()
                print(
                    f"Status: {job_status['status']}, Progress: {job_status.get('progress', 0):.1%}"
                )

                if job_status["status"] in ["completed", "failed"]:
                    print(f"Final status: {job_status['status']}")
                    if job_status["status"] == "completed":
                        print(f"Output files: {job_status.get('output_files', {})}")
                    else:
                        print(f"Error: {job_status.get('error', 'Unknown error')}")
                    break
            else:
                print(f"Error checking status: {status_response.status_code}")
                break

            time.sleep(5)
    print()


def test_upload_pdf():
    """Test uploading and processing PDF"""
    print("Testing PDF upload and processing...")

    pdf_path = "160301289-Warren-Buffett-Katharine-Graham-Letter.pdf"

    if not os.path.exists(pdf_path):
        print(f"Sample PDF not found at: {pdf_path}")
        return

    with open(pdf_path, "rb") as f:
        files = {"file": f}
        data = {
            "provider": "openai",  # Change as needed
            "output_path": None,  # Use default results directory
        }

        response = requests.post(
            f"{API_BASE_URL}/upload", files=files, data=data, headers=get_headers()
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            job_id = response.json()["job_id"]
            print(f"Job started with ID: {job_id}")
    print()


def test_list_jobs():
    """Test listing all jobs"""
    print("Testing job listing...")
    response = requests.get(f"{API_BASE_URL}/jobs", headers=get_headers())
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


if __name__ == "__main__":
    print("LLM-Aided OCR API Test Script")
    print("=" * 40)

    try:
        test_health()
        test_list_jobs()

        # Uncomment the tests you want to run
        # test_process_pdf_from_path()
        # test_upload_pdf()

        print("Tests completed!")

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Make sure the API server is running with: python api_server.py")
    except Exception as e:
        print(f"Error: {e}")
