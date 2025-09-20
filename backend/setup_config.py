#!/usr/bin/env python3
"""
Setup script to initialize MCU-Copilot configuration

This script creates a default configuration file and validates the setup.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.config import config_manager, get_default_config, get_development_config, get_production_config

def setup_configuration(config_type: str = "default"):
    """Setup configuration based on environment"""

    print(f"Setting up MCU-Copilot configuration ({config_type})...")

    # Get appropriate configuration
    if config_type == "development":
        config_data = get_development_config()
    elif config_type == "production":
        config_data = get_production_config()
    else:
        config_data = get_default_config()

    # Parse and load the configuration
    config_manager._parse_config_data(config_data)
    config_manager._load_from_environment()

    # Validate configuration
    validation = config_manager.validate_configuration()

    print("\n=== Configuration Validation ===")
    if validation["valid"]:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has issues:")
        for error in validation["errors"]:
            print(f"  ERROR: {error}")

    if validation["warnings"]:
        print("\nWarnings:")
        for warning in validation["warnings"]:
            print(f"  WARNING: {warning}")

    # Show provider status
    print("\n=== Provider Status ===")
    for provider_key, status in validation["provider_status"].items():
        status_icon = "✅" if status["enabled"] and status["has_api_key"] else "⚠️"
        print(f"{status_icon} {provider_key}:")
        print(f"   Enabled: {status['enabled']}")
        print(f"   API Key: {'✅' if status['has_api_key'] else '❌'}")
        if status["issues"]:
            print(f"   Issues: {', '.join(status['issues'])}")

    # Save configuration to file
    config_file = "mcu_copilot_config.json"
    try:
        config_manager.save_config(config_file)
        print(f"\n✅ Configuration saved to {config_file}")
    except Exception as e:
        print(f"\n❌ Failed to save configuration: {e}")

    # Show setup instructions
    print("\n=== Setup Instructions ===")
    print("1. Configure API keys in environment variables:")
    print("   export QIANWEN_APIKEY=your_qianwen_api_key")
    print("   export GEMINI_API_KEY=your_gemini_api_key")
    print("")
    print("2. Or create a .env file in the backend directory with:")
    print("   QIANWEN_APIKEY=your_qianwen_api_key")
    print("   GEMINI_API_KEY=your_gemini_api_key")
    print("")
    print("3. Start the server:")
    print("   uvicorn app.main:app --reload")

    return validation["valid"]

def test_configuration():
    """Test the current configuration"""
    print("Testing MCU-Copilot configuration...")

    try:
        from app.services.nl_to_assembly_new import get_provider_status, nl_to_assembly

        # Test provider status
        status = get_provider_status()
        print("\n=== Provider Test Results ===")

        working_providers = []
        for provider_key, provider_status in status.items():
            if provider_status.get("available", False):
                working_providers.append(provider_key)
                print(f"✅ {provider_key}: Available")
            else:
                error = provider_status.get("error", "Not available")
                print(f"❌ {provider_key}: {error}")

        if working_providers:
            print(f"\n✅ {len(working_providers)} provider(s) available: {', '.join(working_providers)}")

            # Test a simple generation
            print("\nTesting assembly generation...")
            try:
                thought, code = nl_to_assembly("让LED灯闪烁", session_id="test_session")
                if code:
                    print("✅ Assembly generation test successful")
                    print(f"Generated {len(code)} characters of assembly code")
                else:
                    print("⚠️ Assembly generation returned empty code")
            except Exception as e:
                print(f"❌ Assembly generation test failed: {e}")
        else:
            print("\n❌ No working providers found")
            return False

    except ImportError as e:
        print(f"❌ Failed to import modules: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Setup MCU-Copilot configuration")
    parser.add_argument(
        "--type",
        choices=["default", "development", "production"],
        default="default",
        help="Configuration type to setup"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test the configuration after setup"
    )

    args = parser.parse_args()

    # Setup configuration
    success = setup_configuration(args.type)

    # Run test if requested
    if args.test and success:
        print("\n" + "="*50)
        success = test_configuration()

    sys.exit(0 if success else 1)