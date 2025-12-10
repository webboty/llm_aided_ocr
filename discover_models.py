#!/usr/bin/env python3
"""
LM Studio Model Discovery Utility
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


async def discover_models():
    """Discover all available models and test common variations"""
    print(f"🔍 Discovering models at: {LM_STUDIO_BASE_URL}")

    client = AsyncOpenAI(api_key="not-needed", base_url=f"{LM_STUDIO_BASE_URL}/v1")

    try:
        # Get available models
        response = await client.models.list()

        if response and response.data:
            models = [model.id for model in response.data]
            print(f"\n✅ Found {len(models)} model(s):")
            for i, model in enumerate(models, 1):
                print(f"   {i}. {model}")

            # Test common variations for Qwen3-VL
            qwen_variants = [
                "qwen/qwen3-vl-30b",
                "qwen2-vl-30b",
                "qwen2-vl-72b",
                "qwen-vl",
                "qwen2-vl",
                "Qwen/Qwen2-VL-7B-Instruct",
                "Qwen2-VL-7B-Instruct",
            ]

            print(f"\n🧪 Testing common Qwen model name variations...")
            for variant in qwen_variants:
                if variant in models:
                    print(f"✅ Found match: {variant}")
                    print(f"\n📝 Update your .env file:")
                    print(f"LM_STUDIO_MODEL={variant}")
                    return variant

            print(f"\n⚠️  No exact Qwen match found. Available models:")
            for model in models:
                if "qwen" in model.lower():
                    print(f"   🎯 Possible match: {model}")

            print(f"\n💡 Manual configuration:")
            print(f"1. Choose a model from the list above")
            print(f"2. Update .env: LM_STUDIO_MODEL=your-chosen-model")
            print(
                f'3. Or use config helper: python config_helper.py lm-model "your-chosen-model"'
            )

        else:
            print("❌ No models found. Make sure a model is loaded in LM Studio.")
            print("\n📋 Checklist:")
            print("□ LM Studio application is running")
            print("□ A model is loaded in the AI Chat tab")
            print("□ Server is enabled in Settings")
            print("□ Model is fully downloaded and loaded")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Verify LM Studio is running")
        print(f"2. Check URL: {LM_STUDIO_BASE_URL}")
        print("3. Ensure server is enabled in LM Studio Settings")


if __name__ == "__main__":
    asyncio.run(discover_models())
