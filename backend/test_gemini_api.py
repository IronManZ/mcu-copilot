#!/usr/bin/env python3
"""
Test Gemini API connectivity and performance
"""

import sys
import os
sys.path.append('app')

from services.llm.gemini_provider import GeminiProvider
from services.llm.base import LLMProviderType

def test_gemini_connectivity():
    """Test basic Gemini API connectivity"""

    api_key = "AIzaSyBhcJQYnSqO7uuQeCQo2qig3IO69CvgAOg"

    print("🔍 Testing Gemini API connectivity...")
    print("="*50)

    # Test with latest Gemini 2.5 Flash model
    try:
        provider = GeminiProvider(
            provider_type=LLMProviderType.GEMINI,
            model_name="gemini-2.5-flash",
            api_key=api_key
        )

        print(f"✅ Provider created successfully")
        print(f"📊 Provider info: {provider.get_provider_info()}")
        print(f"🔧 Available: {provider.is_available()}")

        # Test simple API call
        print("\n🚀 Testing simple API call...")
        response = provider.generate(
            messages=[{"role": "user", "content": "Hello! Please respond with exactly 'API working correctly'"}],
            temperature=0.1,
            max_tokens=50
        )

        if response.success:
            print(f"✅ API call successful!")
            print(f"📝 Response: {response.content}")
            print(f"🔢 Token usage: {response.token_usage}")
        else:
            print(f"❌ API call failed: {response.error_message}")

    except Exception as e:
        print(f"❌ Provider creation failed: {e}")
        return False

    # Test with assembly code generation
    print("\n🔧 Testing assembly code generation...")
    try:
        assembly_response = provider.generate(
            messages=[{
                "role": "user",
                "content": "Generate ZH5001 assembly code to blink an LED on pin P03. Use DATA and CODE sections."
            }],
            system_prompt="You are an expert in ZH5001 16-bit RISC microcontroller assembly programming. Generate only valid ZH5001 assembly code with proper DATA and CODE sections.",
            temperature=0.3,
            max_tokens=500
        )

        if assembly_response.success:
            print(f"✅ Assembly generation successful!")
            print(f"📝 Generated code preview:\n{assembly_response.content[:200]}...")
            print(f"🔢 Token usage: {assembly_response.token_usage}")
            return True
        else:
            print(f"❌ Assembly generation failed: {assembly_response.error_message}")
            return False

    except Exception as e:
        print(f"❌ Assembly generation error: {e}")
        return False

def test_model_comparison():
    """Test different Gemini models"""

    api_key = "AIzaSyBhcJQYnSqO7uuQeCQo2qig3IO69CvgAOg"

    models_to_test = [
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-pro"
    ]

    print("\n🔬 Testing different Gemini models...")
    print("="*50)

    results = {}

    for model_name in models_to_test:
        print(f"\n📊 Testing {model_name}...")

        try:
            provider = GeminiProvider(
                provider_type=LLMProviderType.GEMINI,
                model_name=model_name,
                api_key=api_key
            )

            if not provider.is_available():
                print(f"⚠️  {model_name} not available")
                results[model_name] = {"available": False}
                continue

            response = provider.generate(
                messages=[{"role": "user", "content": "Say 'Hello' in exactly 3 words"}],
                temperature=0.1,
                max_tokens=20
            )

            results[model_name] = {
                "available": True,
                "success": response.success,
                "content": response.content[:50] if response.success else None,
                "error": response.error_message if not response.success else None
            }

            if response.success:
                print(f"✅ {model_name}: {response.content[:50]}")
            else:
                print(f"❌ {model_name}: {response.error_message}")

        except Exception as e:
            print(f"❌ {model_name} error: {e}")
            results[model_name] = {"available": False, "error": str(e)}

    print(f"\n📈 Model Test Summary:")
    for model, result in results.items():
        status = "✅ Working" if result.get("success") else "❌ Failed"
        print(f"  {model}: {status}")

    return results

if __name__ == "__main__":
    print("🚀 Gemini API Testing Suite")
    print("="*50)

    # Test basic connectivity
    connectivity_success = test_gemini_connectivity()

    # Test different models
    model_results = test_model_comparison()

    print(f"\n🎯 Final Results:")
    print(f"  Basic connectivity: {'✅ Success' if connectivity_success else '❌ Failed'}")
    print(f"  Working models: {sum(1 for r in model_results.values() if r.get('success', False))}/{len(model_results)}")

    if connectivity_success:
        print(f"\n🎉 Gemini API is ready for MCU-Copilot integration!")
    else:
        print(f"\n⚠️  Gemini API needs troubleshooting before integration")