#!/usr/bin/env python3
"""
LM Studio Connection Test and Model Listing Utility
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openai import AsyncOpenAI
from decouple import Config as DecoupleConfig, RepositoryEnv

# Load configuration
config = DecoupleConfig(RepositoryEnv(".env"))
LM_STUDIO_BASE_URL = config.get(
    "LM_STUDIO_BASE_URL", default="http://192.168.1.107:11435", cast=str
)
LM_STUDIO_MODEL = config.get("LM_STUDIO_MODEL", default="", cast=str)


async def test_connection():
    """Test LM Studio connection and list models"""
    print(f"Testing connection to LM Studio at: {LM_STUDIO_BASE_URL}")

    client = AsyncOpenAI(api_key="not-needed", base_url=f"{LM_STUDIO_BASE_URL}/v1")

    try:
        # Test basic connection
        print("\n1. Testing basic connection...")
        response = await client.models.list()

        if response and response.data:
            models = [model.id for model in response.data]
            print(f"✅ Found {len(models)} model(s):")
            for i, model in enumerate(models, 1):
                print(f"   {i}. {model}")
        else:
            print("❌ No models found. Make sure a model is loaded in LM Studio.")
            print("\nTroubleshooting:")
            print("1. Open LM Studio")
            print("2. Load a model (click 'AI Chat' tab, then select a model)")
            print("3. Make sure the model is fully loaded")
            print("4. Check that the server is running on the correct port")
            return False

        # Test completion
        print("\n2. Testing completion...")
        model_to_use = (
            LM_STUDIO_MODEL if LM_STUDIO_MODEL else models[0] if models else "default"
        )

        completion_response = await client.chat.completions.create(
            model=model_to_use,
            messages=[{"role": "user", "content": "Say 'Hello from LM Studio!'"}],
            max_tokens=50,
            temperature=0.7,
        )

        if completion_response and completion_response.choices:
            result = completion_response.choices[0].message.content
            print(f"✅ Completion test successful!")
            print(f"Response: {result}")
            return True
        else:
            print("❌ Completion test failed - no response received")
            return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure LM Studio is running")
        print(f"2. Check the URL: {LM_STUDIO_BASE_URL}")
        print("3. Verify the server is enabled in LM Studio settings")
        return False


async def main():
    success = await test_connection()
    if success:
        print("\n🎉 LM Studio is ready to use with LLM-Aided OCR!")
        print("\nTo use LM Studio, update your .env file:")
        print("API_PROVIDER=LM_STUDIO")
        print("LM_STUDIO_BASE_URL=http://192.168.1.107:11435")
        print("LM_STUDIO_MODEL=your-model-name  # Optional - leave empty for default")
    else:
        print("\n❌ Please fix the connection issues before using LM Studio.")


if __name__ == "__main__":
    asyncio.run(main())
