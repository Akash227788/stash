#!/usr/bin/env python3
"""
Environment Configuration Test Script
Tests that all environment variables are properly loaded and configured.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.env_loader import load_env_from_file, get_config, validate_required_config, print_config_summary


def test_env_loading():
    """Test environment variable loading."""
    print("🧪 Testing Environment Variable Loading")
    print("=" * 50)
    
    # Test .env file loading
    env_loaded = load_env_from_file()
    if env_loaded:
        print("✅ .env file loaded successfully")
    else:
        print("⚠️  .env file not found or failed to load")
    
    # Get configuration
    config = get_config()
    print(f"\n📋 Configuration loaded: {len(config)} settings")
    
    # Validate required configuration
    is_valid, missing_keys = validate_required_config()
    if is_valid:
        print("✅ All required configuration is present")
    else:
        print(f"❌ Missing required keys: {', '.join(missing_keys)}")
    
    return config, is_valid


def test_individual_settings():
    """Test individual configuration settings."""
    print("\n🔧 Testing Individual Settings")
    print("=" * 50)
    
    config = get_config()
    
    # Test server settings
    print(f"Server: {config['host']}:{config['port']} (debug: {config['debug']})")
    
    # Test Google Cloud settings
    print(f"Project ID: {config['project_id'] or 'Not configured'}")
    print(f"GCS Bucket: {config['gcs_bucket'] or 'Not configured'}")
    print(f"Credentials: {'Configured' if config['credentials_path'] else 'Not configured'}")
    
    # Test AI settings
    print(f"GenAI API Key: {'Configured' if config['genai_api_key'] and not config['genai_api_key'].startswith('your-') else 'Not configured'}")
    print(f"GenAI Model: {config['genai_model']}")
    
    # Test gamification settings
    print(f"Points per receipt: {config['points_per_receipt']}")
    print(f"Bonus multiplier: {config['bonus_multiplier']}")
    
    # Test feature flags
    print(f"Vision API: {'Enabled' if config['vision_enabled'] else 'Disabled'}")
    print(f"Mock APIs: {'Enabled' if config['mock_external_apis'] else 'Disabled'}")
    print(f"Gamification: {'Enabled' if config['gamification_enabled'] else 'Disabled'}")


def test_environment_specific_values():
    """Test environment-specific value parsing."""
    print("\n🌍 Testing Environment-Specific Values")
    print("=" * 50)
    
    # Test boolean parsing
    test_cases = [
        ("DEBUG", "debug", bool),
        ("VISION_API_ENABLED", "vision_enabled", bool),
        ("STREAK_BONUS_ENABLED", "streak_bonus_enabled", bool),
        ("MOCK_EXTERNAL_APIS", "mock_external_apis", bool),
    ]
    
    config = get_config()
    
    for env_var, config_key, expected_type in test_cases:
        env_value = os.getenv(env_var, "not_set")
        config_value = config.get(config_key)
        
        print(f"{env_var}: '{env_value}' -> {config_value} ({type(config_value).__name__})")
        
        if not isinstance(config_value, expected_type):
            print(f"  ⚠️  Expected {expected_type.__name__}, got {type(config_value).__name__}")
    
    # Test numeric parsing
    numeric_tests = [
        ("PORT", "port", int),
        ("POINTS_PER_RECEIPT", "points_per_receipt", int),
        ("GENAI_TEMPERATURE", "genai_temperature", float),
        ("VISION_CONFIDENCE_THRESHOLD", "vision_confidence", float),
    ]
    
    for env_var, config_key, expected_type in numeric_tests:
        env_value = os.getenv(env_var, "not_set")
        config_value = config.get(config_key)
        
        print(f"{env_var}: '{env_value}' -> {config_value} ({type(config_value).__name__})")
        
        if not isinstance(config_value, expected_type):
            print(f"  ⚠️  Expected {expected_type.__name__}, got {type(config_value).__name__}")


def main():
    """Run all environment tests."""
    print("🚀 Stash Environment Configuration Test")
    print("=" * 60)
    
    # Test basic loading
    config, is_valid = test_env_loading()
    
    # Test individual settings
    test_individual_settings()
    
    # Test value parsing
    test_environment_specific_values()
    
    # Print summary
    print("\n📊 Configuration Summary")
    print("=" * 50)
    print_config_summary()
    
    # Final result
    print("\n🏁 Test Results")
    print("=" * 50)
    
    if is_valid:
        print("✅ Environment configuration test PASSED")
        print("   All required variables are configured")
        return 0
    else:
        print("❌ Environment configuration test FAILED")
        print("   Some required variables are missing or misconfigured")
        print("   Please update your .env file with the missing values")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
