#!/usr/bin/env python3
"""
env_to_cloudrun.py - Convert .env file to Google Cloud Run environment variables

This script extracts environment variables from .env file and formats them 
for Google Cloud Run deployment, separating sensitive data for Secret Manager.
"""

import os
import re
import json
from typing import Dict, List, Tuple

def load_env_file(env_file_path: str = ".env") -> Dict[str, str]:
    """Load environment variables from .env file."""
    env_vars = {}
    
    if not os.path.exists(env_file_path):
        print(f"❌ Error: {env_file_path} file not found!")
        return {}
    
    with open(env_file_path, 'r', encoding='utf-8') as f:
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
                env_vars[key] = value
            else:
                print(f"⚠️  Invalid line format in {env_file_path}:{line_num}: {line}")
    
    return env_vars

def categorize_variables(env_vars: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Separate environment variables into regular and sensitive categories."""
    
    sensitive_keys = {
        'GENAI_API_KEY', 'GEMINI_API_KEY', 'SECRET_KEY', 'JWT_SECRET_KEY', 
        'WEBHOOK_SECRET', 'GOOGLE_APPLICATION_CREDENTIALS', 'SMTP_PASSWORD',
        'SENDGRID_API_KEY', 'REDIS_PASSWORD', 'SENTRY_DSN'
    }
    
    regular_vars = {}
    sensitive_vars = {}
    
    for key, value in env_vars.items():
        if key in sensitive_keys or 'password' in key.lower() or 'secret' in key.lower() or 'key' in key.lower():
            sensitive_vars[key] = value
        else:
            regular_vars[key] = value
    
    return regular_vars, sensitive_vars

def generate_cloud_run_env_string(env_vars: Dict[str, str]) -> str:
    """Generate environment variables string for Cloud Run deployment."""
    env_pairs = []
    for key, value in env_vars.items():
        # Escape special characters for Cloud Run
        escaped_value = value.replace(',', '\\,').replace('=', '\\=')
        env_pairs.append(f"{key}={escaped_value}")
    
    return ','.join(env_pairs)

def generate_secret_commands(sensitive_vars: Dict[str, str], project_id: str) -> List[str]:
    """Generate gcloud commands to create secrets."""
    commands = []
    
    secret_mappings = {
        'GENAI_API_KEY': 'genai-api-key',
        'SECRET_KEY': 'stash-secret-key',
        'JWT_SECRET_KEY': 'jwt-secret-key',
        'WEBHOOK_SECRET': 'webhook-secret',
        'SMTP_PASSWORD': 'smtp-password',
        'SENDGRID_API_KEY': 'sendgrid-api-key',
        'REDIS_PASSWORD': 'redis-password',
        'SENTRY_DSN': 'sentry-dsn'
    }
    
    for key, value in sensitive_vars.items():
        if key in secret_mappings:
            secret_name = secret_mappings[key]
            # Create command to create/update secret
            create_cmd = f'echo "{value}" | gcloud secrets create {secret_name} --data-file=- --project={project_id} 2>/dev/null || echo "{value}" | gcloud secrets versions add {secret_name} --data-file=- --project={project_id}'
            commands.append(create_cmd)
    
    return commands

def generate_secrets_string(sensitive_vars: Dict[str, str]) -> str:
    """Generate secrets string for Cloud Run deployment."""
    secret_mappings = {
        'GENAI_API_KEY': 'genai-api-key',
        'SECRET_KEY': 'stash-secret-key',
        'JWT_SECRET_KEY': 'jwt-secret-key',
        'WEBHOOK_SECRET': 'webhook-secret',
        'SMTP_PASSWORD': 'smtp-password',
        'SENDGRID_API_KEY': 'sendgrid-api-key',
        'REDIS_PASSWORD': 'redis-password',
        'SENTRY_DSN': 'sentry-dsn'
    }
    
    secret_pairs = []
    for key in sensitive_vars.keys():
        if key in secret_mappings:
            secret_name = secret_mappings[key]
            secret_pairs.append(f"{key}={secret_name}:latest")
    
    return ','.join(secret_pairs)

def main():
    """Main function to process environment variables."""
    print("🔧 Converting .env file to Google Cloud Run format")
    print("=" * 60)
    
    # Load environment variables
    env_vars = load_env_file()
    if not env_vars:
        return
    
    print(f"📋 Loaded {len(env_vars)} environment variables")
    
    # Categorize variables
    regular_vars, sensitive_vars = categorize_variables(env_vars)
    
    print(f"📊 Regular variables: {len(regular_vars)}")
    print(f"🔒 Sensitive variables: {len(sensitive_vars)}")
    
    # Generate Cloud Run environment string
    env_string = generate_cloud_run_env_string(regular_vars)
    
    # Generate secrets
    project_id = env_vars.get('PROJECT_ID', env_vars.get('FIRESTORE_PROJECT_ID', 'your-project-id'))
    secret_commands = generate_secret_commands(sensitive_vars, project_id)
    secrets_string = generate_secrets_string(sensitive_vars)
    
    # Output results
    print("\n🚀 CLOUD RUN DEPLOYMENT CONFIGURATION")
    print("=" * 60)
    
    print("\n📝 Environment Variables String:")
    print("(Use with --set-env-vars flag)")
    print("-" * 40)
    print(env_string)
    
    print("\n🔒 Secret Manager Commands:")
    print("(Run these commands first)")
    print("-" * 40)
    for cmd in secret_commands:
        print(cmd)
    
    print("\n🔑 Secrets String:")
    print("(Use with --set-secrets flag)")
    print("-" * 40)
    print(secrets_string)
    
    print("\n🏗️  Complete Cloud Run Deploy Command:")
    print("-" * 40)
    print(f"""gcloud run deploy stash-api \\
    --image gcr.io/{project_id}/stash-api \\
    --platform managed \\
    --region us-central1 \\
    --project {project_id} \\
    --allow-unauthenticated \\
    --port 8080 \\
    --memory 1Gi \\
    --cpu 1 \\
    --max-instances 100 \\
    --service-account "stash-api-service@{project_id}.iam.gserviceaccount.com" \\
    --set-env-vars "{env_string}" \\
    --set-secrets "{secrets_string}"
""")
    
    # Save to files for easy use
    with open('cloud-run-env-vars.txt', 'w') as f:
        f.write(env_string)
    
    with open('cloud-run-secrets.txt', 'w') as f:
        f.write(secrets_string)
    
    with open('secret-manager-commands.sh', 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Commands to create secrets in Secret Manager\n\n")
        for cmd in secret_commands:
            f.write(cmd + "\n")
    
    os.chmod('secret-manager-commands.sh', 0o755)
    
    print("\n💾 Files created:")
    print("  • cloud-run-env-vars.txt - Environment variables string")
    print("  • cloud-run-secrets.txt - Secrets string")
    print("  • secret-manager-commands.sh - Commands to create secrets")
    
    print("\n✅ Conversion complete!")

if __name__ == "__main__":
    main()
