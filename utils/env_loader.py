# utils/env_loader.py
"""
Environment variable loader utility for Stash project.
Loads environment variables from .env file and validates required settings.
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional


def load_env_from_file(env_file_path: str = ".env") -> bool:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file_path: Path to the .env file
        
    Returns:
        bool: True if file was loaded successfully, False otherwise
    """
    env_file = Path(env_file_path)
    if not env_file.exists():
        print(f"⚠️  Environment file {env_file_path} not found")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')  # Remove quotes
                    
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
                else:
                    print(f"⚠️  Invalid line format in {env_file_path}:{line_num}: {line}")
        
        print(f"✅ Environment variables loaded from {env_file_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error loading environment file {env_file_path}: {e}")
        return False


def get_config() -> Dict[str, Any]:
    """
    Get application configuration from environment variables.
    
    Returns:
        Dict containing configuration values with defaults
    """
    return {
        # Server configuration
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8080")),
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "environment": os.getenv("ENVIRONMENT", "development"),
        
        # Google Cloud configuration
        "project_id": os.getenv("FIRESTORE_PROJECT_ID") or os.getenv("PROJECT_ID"),
        "gcs_bucket": os.getenv("GCLOUD_STORAGE_BUCKET") or os.getenv("GCS_BUCKET_NAME"),
        "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        
        # AI/ML configuration
        "genai_api_key": os.getenv("GENAI_API_KEY") or os.getenv("GEMINI_API_KEY"),
        "genai_model": os.getenv("GENAI_MODEL", "gemini-pro"),
        "genai_temperature": float(os.getenv("GENAI_TEMPERATURE", "0.7")),
        
        # Vision API configuration
        "vision_enabled": os.getenv("VISION_API_ENABLED", "true").lower() == "true",
        "vision_confidence": float(os.getenv("VISION_CONFIDENCE_THRESHOLD", "0.7")),
        "vision_max_results": int(os.getenv("VISION_MAX_RESULTS", "50")),
        
        # Gamification configuration
        "points_per_receipt": int(os.getenv("POINTS_PER_RECEIPT", "10")),
        "bonus_multiplier": float(os.getenv("BONUS_POINTS_MULTIPLIER", "1.5")),
        "max_daily_receipts": int(os.getenv("MAX_DAILY_RECEIPTS", "20")),
        "streak_bonus_enabled": os.getenv("STREAK_BONUS_ENABLED", "true").lower() == "true",
        
        # Purchase bonuses
        "large_purchase_threshold": float(os.getenv("LARGE_PURCHASE_THRESHOLD", "100")),
        "medium_purchase_threshold": float(os.getenv("MEDIUM_PURCHASE_THRESHOLD", "50")),
        "large_purchase_bonus": int(os.getenv("LARGE_PURCHASE_BONUS", "10")),
        "medium_purchase_bonus": int(os.getenv("MEDIUM_PURCHASE_BONUS", "5")),
        "grocery_bonus": int(os.getenv("GROCERY_BONUS_POINTS", "3")),
        
        # Security configuration
        "secret_key": os.getenv("SECRET_KEY"),
        "jwt_secret": os.getenv("JWT_SECRET_KEY"),
        
        # Feature flags
        "mock_external_apis": os.getenv("MOCK_EXTERNAL_APIS", "false").lower() == "true",
        "analytics_enabled": os.getenv("ANALYTICS_ENABLED", "true").lower() == "true",
        "gamification_enabled": os.getenv("GAMIFICATION_ENABLED", "true").lower() == "true",
        "wallet_enabled": os.getenv("WALLET_ENABLED", "true").lower() == "true",
        
        # Logging configuration
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "log_format": os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    }


def validate_required_config() -> tuple[bool, list[str]]:
    """
    Validate that all required configuration is present.
    
    Returns:
        Tuple of (is_valid, missing_keys)
    """
    config = get_config()
    required_keys = [
        "genai_api_key",
        "project_id", 
        "gcs_bucket",
        "secret_key"
    ]
    
    missing_keys = []
    for key in required_keys:
        value = config.get(key)
        if not value or (isinstance(value, str) and value.startswith("your-")):
            missing_keys.append(key)
    
    return len(missing_keys) == 0, missing_keys


def print_config_summary():
    """Print a summary of the current configuration."""
    config = get_config()
    is_valid, missing_keys = validate_required_config()
    
    print("🔧 Configuration Summary")
    print("=" * 50)
    print(f"Environment: {config['environment']}")
    print(f"Server: {config['host']}:{config['port']}")
    print(f"Debug mode: {config['debug']}")
    print(f"Project ID: {config['project_id'] or 'Not set'}")
    print(f"GCS Bucket: {config['gcs_bucket'] or 'Not set'}")
    print(f"Vision API: {'Enabled' if config['vision_enabled'] else 'Disabled'}")
    print(f"Gamification: {'Enabled' if config['gamification_enabled'] else 'Disabled'}")
    print(f"Mock APIs: {'Enabled' if config['mock_external_apis'] else 'Disabled'}")
    
    if missing_keys:
        print(f"\n❌ Missing required configuration: {', '.join(missing_keys)}")
    else:
        print("\n✅ All required configuration present")


# Auto-load environment variables when module is imported
if __name__ != "__main__":
    load_env_from_file()


if __name__ == "__main__":
    # When run directly, show configuration summary
    load_env_from_file()
    print_config_summary()
