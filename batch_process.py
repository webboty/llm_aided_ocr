#!/usr/bin/env python3
"""
Batch PDF Processing for LLM-Aided OCR
Processes multiple PDF files in a directory
"""

import os
import sys
import glob
import subprocess
import asyncio
from pathlib import Path


def get_script_directory():
    """Get the directory where this script is located"""
    return os.path.dirname(os.path.abspath(__file__))


def change_to_script_directory():
    """Change to script directory for relative paths"""
    script_dir = get_script_directory()
    os.chdir(script_dir)
    return script_dir


async def process_pdf(pdf_path, script_dir):
    """Process a single PDF file"""
    print(f"📄 Processing: {os.path.basename(pdf_path)}")

    # Change to script directory
    os.chdir(script_dir)

    # Run the main OCR script
    cmd = ["python", "llm_aided_ocr.py", pdf_path]
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"✅ Completed: {os.path.basename(pdf_path)}")
        # Find output files
        pdf_name = Path(pdf_path).stem
        output_files = list(Path(".").glob(f"{pdf_name}*"))
        for output in output_files:
            if output.is_file():
                print(f"   📄 {output.name}")
    else:
        print(f"❌ Failed: {os.path.basename(pdf_path)}")
        if stderr:
            print(f"   Error: {stderr.decode()}")


async def main():
    """Main batch processing function"""
    if len(sys.argv) < 2:
        print("🔧 Batch PDF Processing for LLM-Aided OCR")
        print("\nUsage:")
        print("  python batch_process.py <pdf_directory>")
        print(
            "  python batch_process.py <pdf_directory> --provider <lm-studio|openai|claude>"
        )
        print("  python batch_process.py <pdf_directory> --model <model_name>")
        print("\nExamples:")
        print("  python batch_process.py ~/Documents/PDFs")
        print("  python batch_process.py ~/Documents/PDFs --provider lm-studio")
        print(
            "  python batch_process.py ~/Documents/PDFs --provider lm-studio --model qwen/qwen3-vl-30b"
        )
        print("\nOptions:")
        print("  --provider: Set LLM provider (openai, claude, lm-studio)")
        print("  --model: Set specific model name (for lm-studio only)")
        return

    # Parse arguments
    pdf_directory = sys.argv[1]
    provider = None
    model = None

    for i, arg in enumerate(sys.argv[2:]):
        if arg == "--provider" and i + 1 < len(sys.argv):
            provider = sys.argv[i + 1]
        elif arg == "--model" and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]

    # Change to script directory
    script_dir = change_to_script_directory()

    # Find PDF files
    pdf_files = glob.glob(os.path.join(pdf_directory, "*.pdf"))

    if not pdf_files:
        print(f"❌ No PDF files found in: {pdf_directory}")
        return

    print(f"📁 Found {len(pdf_files)} PDF files to process")

    # Configure provider if specified
    if provider:
        print(f"🔧 Setting provider to: {provider}")
        subprocess.run(["python", "config_helper.py", provider])

    # Configure model if specified
    if model and provider == "lm-studio":
        print(f"🤖 Setting model to: {model}")
        subprocess.run(["python", "config_helper.py", "lm-model", model])

    # Process each PDF
    success_count = 0
    for pdf_path in pdf_files:
        await process_pdf(pdf_path, script_dir)
        success_count += 1

    print(f"\n🎉 Batch processing complete!")
    print(f"✅ Successfully processed: {success_count}/{len(pdf_files)} files")
    print(f"❌ Failed: {len(pdf_files) - success_count} files")


if __name__ == "__main__":
    asyncio.run(main())
