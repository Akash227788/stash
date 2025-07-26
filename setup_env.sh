#!/bin/bash
# setup_env.sh - Environment Setup Script for Stash Project

echo "🚀 Setting up Stash Financial Management System Environment"
echo "=========================================================="

# Check if .env file exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Backing up to .env.backup"
    cp .env .env.backup
fi

# Copy example to .env
echo "📄 Creating .env file from template..."
cp .env.example .env

echo ""
echo "✅ Environment file created successfully!"
echo ""
echo "🔧 Next Steps:"
echo "1. Edit .env file with your actual configuration values"
echo "2. Get Google AI API key from: https://makersuite.google.com/app/apikey"
echo "3. Set up Google Cloud Project and enable required APIs:"
echo "   - Firestore"
echo "   - Cloud Vision API"
echo "   - Cloud Storage"
echo "   - Pub/Sub"
echo "4. Create service account and download JSON key"
echo "5. Create Cloud Storage bucket for receipt storage"
echo ""
echo "📝 Essential variables to configure:"
echo "   - GENAI_API_KEY"
echo "   - FIRESTORE_PROJECT_ID"
echo "   - GCLOUD_STORAGE_BUCKET"
echo "   - GOOGLE_APPLICATION_CREDENTIALS"
echo "   - SECRET_KEY"
echo ""
echo "🔍 For detailed setup instructions, see README.md"
echo ""

# Check if python virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
    echo "💡 Activate with: source .venv/bin/activate"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "🎉 Setup complete! Don't forget to:"
echo "   1. Activate virtual environment: source .venv/bin/activate"
echo "   2. Install dependencies: pip install -r requirements.txt"
echo "   3. Configure your .env file with actual values"
echo "   4. Run the application: python main.py"
