#!/usr/bin/env python3
"""
LLM-Aided OCR Configuration Helper
"""

import os
import sys
from decouple import Config as DecoupleConfig, RepositoryEnv


def update_env_file(key, value):
    """Update a value in the .env file"""
    env_file = ".env"

    # Read current content
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()
    else:
        lines = []

    # Update or add the key
    key_found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_found = True
            break

    if not key_found:
        lines.append(f"{key}={value}\n")

    # Write back
    with open(env_file, "w") as f:
        f.writelines(lines)

    print(f"✅ Updated {key}={value}")


def show_current_config():
    """Show current configuration"""
    config = DecoupleConfig(RepositoryEnv(".env"))

    print("📋 Current LLM-Aided OCR Configuration:")
    print(f"API Provider: {config.get('API_PROVIDER', default='OPENAI')}")
    print(f"Use Local LLM: {config.get('USE_LOCAL_LLM', default=False)}")
    print(
        f"LM Studio URL: {config.get('LM_STUDIO_BASE_URL', default='http://192.168.1.107:11435')}"
    )
    print(f"LM Studio Model: {config.get('LM_STUDIO_MODEL', default='Default')}")
    print(
        f"OpenAI Model: {config.get('OPENAI_COMPLETION_MODEL', default='gpt-4o-mini')}"
    )
    print(
        f"Claude Model: {config.get('CLAUDE_MODEL_STRING', default='claude-3-5-sonnet-20241022')}"
    )


def main():
    if len(sys.argv) < 2:
        print("🔧 LLM-Aided OCR Configuration Helper")
        print("\nUsage:")
        print("  python config_helper.py show                    # Show current config")
        print("  python config_helper.py openai                  # Use OpenAI")
        print("  python config_helper.py claude                  # Use Claude")
        print("  python config_helper.py lm-studio              # Use LM Studio")
        print("  python config_helper.py local                  # Use local GGUF model")
        print(
            "  python config_helper.py lm-model <model_name>   # Set specific LM Studio model"
        )
        print("\nExamples:")
        print("  python config_helper.py lm-studio")
        print('  python config_helper.py lm-model "llama-3.1-8b-instruct"')
        return

    command = sys.argv[1].lower()

    if command == "show":
        show_current_config()

    elif command == "openai":
        update_env_file("API_PROVIDER", "OPENAI")
        update_env_file("USE_LOCAL_LLM", "False")
        print("🚀 Switched to OpenAI. Make sure OPENAI_API_KEY is set in .env")

elif command == "claude":
        update_env_file("API_PROVIDER", "CLAUDE")
        update_env_file("USE_LOCAL_LLM", "False")
        print("🚀 Switched to Claude. Make sure ANTHROPIC_API_KEY is set in .env")
    
    elif command == "lm-studio":
        update_env_file("API_PROVIDER", "LM_STUDIO")
        update_env_file("USE_LOCAL_LLM", "False")
        print("🚀 Switched to LM Studio. Make sure LM Studio is running with a model loaded")
        print("   Recommended model: qwen/qwen3-vl-30b")
        print("   Run 'python discover_models.py' to see available models")
        print("   Run 'python test_lm_studio.py' to verify connection")

    elif command == "local":
        update_env_file("USE_LOCAL_LLM", "True")
        print("🚀 Switched to local GGUF model. Make sure LOCAL_LLM_MODEL_PATH is set")

    elif command == "lm-model" and len(sys.argv) > 2:
        model_name = sys.argv[2]
        update_env_file("LM_STUDIO_MODEL", model_name)
        print(f"🚀 Set LM Studio model to: {model_name}")

    else:
        print("❌ Unknown command. Use 'python config_helper.py' for help")


if __name__ == "__main__":
    main()
