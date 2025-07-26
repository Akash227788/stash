# Stash - AI-Powered Financial Management System

**A comprehensive, gamified AI receipt management system built with Google Agent Devcurl "http://localhost:8080/adk/health"
```

## 📁 Project Structure

```
stash/
├── 📄 README.md                          # This file
├── 📄 requirements.txt                   # Python dependencies
├── 📄 Dockerfile                         # Container configuration
├── 📄 .env.example                       # Environment template
├── 📄 .env                              # Your environment config (create from .env.example)
│
├── 🚀 Entry Points
│   ├── main.py                          # Traditional FastAPI server
│   ├── adk_main.py                      # Google ADK-powered server
│   └── adk_server.py                    # ADK server implementation
│
├── 🤖 Agent System
│   └── agents/
│       ├── base_agent.py                # ADK agent base classes
│       ├── root_agent.py                # Multi-agent coordinator
│       ├── receipt_agent.py             # Receipt processing agent
│       ├── analytics_agent.py           # Financial analytics agent
│       ├── game_agent.py                # Gamification agent
│       ├── wallet_agent.py              # Digital wallet agent
│       └── tools/                       # Agent-specific tools
│           ├── receipt_tools.py         # OCR and parsing tools
│           ├── analytics_tools.py       # Analytics computation
│           ├── game_tools.py            # Points and achievements
│           └── wallet_tools.py          # Balance and transactions
│
├── 🛠️ Utilities
│   └── utils/
│       ├── env_loader.py                # Environment configuration system
│       ├── genai_client.py              # Google AI client
│       ├── vision_utils.py              # Vision API utilities
│       ├── firestore_client.py          # Database client
│       ├── storage_client.py            # Cloud Storage client
│       └── pubsub_client.py             # Pub/Sub messaging
│
├── 🧪 Testing & Examples
│   ├── test_env.py                      # Environment validation
│   ├── test_adk_agents.py               # Agent testing
│   ├── validate_env.py                  # Configuration validator
│   └── examples/
│       └── adk_workflow_example.py      # ADK workflow demonstrations
│
├── 📚 Documentation
│   ├── ADK_README.md                    # ADK implementation guide
│   ├── ENV_IMPLEMENTATION_SUMMARY.md   # Environment system documentation
│   └── GEMINI.md                        # Gemini AI integration guide
│
└── 🔧 Scripts & Configuration
    ├── cloud_run.sh                     # Cloud Run deployment
    ├── devserver.sh                     # Development server
    ├── setup_env.sh                     # Environment setup
    ├── cloudbuild.yaml                  # Cloud Build configuration
    └── .vscode/                         # VS Code settings
```

## 🔧 Troubleshooting

### **Common Issues**

#### **Environment Configuration**
```bash
# ❌ Error: Missing required environment variables
python test_env.py
# ✅ Fix: Update .env file with missing values

# ❌ Error: Invalid API key
# ✅ Fix: Get new key from https://makersuite.google.com/app/apikey
```

#### **Google Cloud Authentication**
```bash
# ❌ Error: Application Default Credentials not found
gcloud auth application-default login

# ❌ Error: Permission denied
# ✅ Fix: Check service account permissions in Google Cloud Console
```

#### **Mock Mode for Development**
```bash
# Enable mock mode in .env for testing without API keys
MOCK_EXTERNAL_APIS="true"
MOCK_VISION_API="true" 
MOCK_GENAI_API="true"
```

### **Debug Mode**
```bash
# Enable detailed logging
DEBUG="true"
LOG_LEVEL="DEBUG"
DEBUG_AGENT_RESPONSES="true"
```

### **Health Checks**
```bash
# Check system health
curl http://localhost:8080/adk/health

# Expected response:
{
  "status": "healthy",
  "adk_version": "google-adk",
  "agents": {
    "root_agent": "initialized",
    "receipt_agent": "ready",
    "analytics_agent": "ready",
    "game_agent": "ready",
    "wallet_agent": "ready"
  }
}
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow ADK patterns** for new agents
4. **Add environment variables** to `.env.example`
5. **Update tests**: Add tests for new functionality
6. **Update documentation**: Keep README.md current
7. **Create Pull Request**

## 📋 Environment Variables Checklist

Before deploying, ensure these are configured:

**✅ Essential (Required)**
- [ ] `GENAI_API_KEY` - Google AI API key
- [ ] `FIRESTORE_PROJECT_ID` - Google Cloud Project ID
- [ ] `GCLOUD_STORAGE_BUCKET` - Storage bucket name
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` - Service account path
- [ ] `SECRET_KEY` - Application security key

**⚙️ Server Configuration**
- [ ] `HOST` - Server host (default: 0.0.0.0)
- [ ] `PORT` - Server port (default: 8080)
- [ ] `DEBUG` - Debug mode (default: false)
- [ ] `ENVIRONMENT` - Environment identifier

**🎮 Gamification Settings**
- [ ] `POINTS_PER_RECEIPT` - Base points per receipt
- [ ] `BONUS_POINTS_MULTIPLIER` - Bonus calculation multiplier
- [ ] `LARGE_PURCHASE_THRESHOLD` - Large purchase trigger
- [ ] `GAMIFICATION_ENABLED` - Enable gamification

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud Platform** - Cloud infrastructure
- **Google AI/Gemini** - Advanced language model
- **Google Agent Development Kit** - Multi-agent framework
- **FastAPI** - Modern Python web framework

---

**🚀 Ready to get started?** Run `python test_env.py` to validate your setup!opment Kit (ADK) and modern cloud architecture.**

This project implements a sophisticated multi-agent system using both traditional FastAPI and Google's Agent Development Kit (ADK) patterns, designed for scalable deployment on Google Cloud Run with comprehensive environment configuration management.

## 🚀 Features

### Core Functionality
- **🧾 Intelligent Receipt Processing**: Upload receipt images and extract detailed information using Cloud Vision AI and Gemini Pro
- **📊 Advanced Financial Analytics**: AI-powered spending insights, categorization, and budget forecasting
- **🎮 Dynamic Gamification**: Configurable points system with bonuses, streaks, and achievements
- **💰 Digital Wallet Management**: Point balance tracking, transaction history, and reward redemption
- **🤖 Multi-Agent Architecture**: Both traditional FastAPI and Google ADK agent patterns

### Advanced Features
- **⚙️ Comprehensive Environment Configuration**: 60+ configurable environment variables
- **🔧 Flexible Deployment Options**: Support for development, staging, and production environments
- **🧪 Mock Mode Support**: Test without API keys using mock responses
- **📈 Real-time Analytics**: Dynamic spending reports with AI-generated insights
- **🛡️ Enterprise Security**: JWT authentication, rate limiting, and secure credential management

## 🏗️ Architecture

### Agent System Design

#### **Traditional FastAPI Agents** (`main.py`)
- **Root Agent**: Application coordinator and welcome interface
- **Receipt Agent**: Image processing, OCR, and data extraction
- **Analytics Agent**: Financial analysis and reporting
- **Game Agent**: Gamification logic and point management  
- **Wallet Agent**: Balance tracking and transaction management

#### **Google ADK Agents** (`adk_main.py`)
- **Sequential Workflows**: Receipt → Points → Wallet (step-by-step processing)
- **Parallel Execution**: Simultaneous data gathering for dashboards
- **Coordinator Patterns**: Intelligent request routing between specialized agents
- **State Management**: Session-based data sharing between agents

### Technology Stack
- **Backend**: FastAPI + Google Agent Development Kit (ADK)
- **AI/ML**: Google Gemini Pro, Cloud Vision AI
- **Database**: Google Firestore (NoSQL)
- **Storage**: Google Cloud Storage
- **Messaging**: Google Pub/Sub
- **Deployment**: Google Cloud Run (Serverless)
- **Configuration**: Comprehensive environment variable system

## 📋 Prerequisites

### Required Accounts & Tools
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured
- Google Cloud project with billing enabled
- Google AI API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `gcloud` CLI authenticated with your Google Cloud account

### System Requirements
- Python 3.8+
- Docker (for deployment)
- 1GB+ available memory for local development

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone and navigate to the project
cd stash

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

**Essential variables to configure:**
```bash
# Google AI API Key (Get from https://makersuite.google.com/app/apikey)
GENAI_API_KEY="your-google-ai-api-key"

# Google Cloud Project Configuration
FIRESTORE_PROJECT_ID="your-gcp-project-id"
GCLOUD_STORAGE_BUCKET="your-unique-bucket-name"
GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# Application Security
SECRET_KEY="your-secure-random-key"

# Server Configuration (Optional - defaults provided)
HOST="0.0.0.0"
PORT="8080"
DEBUG="true"
```

### 3. Validate Configuration

```bash
# Test your environment setup
python test_env.py

# Should show: ✅ Environment configuration test PASSED
```

### 4. Choose Your Server Mode

#### **Option A: Traditional FastAPI Server**
```bash
python main.py
```

#### **Option B: Google ADK-Powered Server**
```bash
python adk_main.py
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8080/

# ADK health check (if using ADK server)
curl http://localhost:8080/adk/health
```

## ⚙️ Environment Configuration

The system supports **60+ environment variables** for comprehensive configuration:

### **Core Configuration**
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GENAI_API_KEY` | ✅ | - | Google AI API key for Gemini Pro |
| `FIRESTORE_PROJECT_ID` | ✅ | - | Google Cloud Project ID |
| `GCLOUD_STORAGE_BUCKET` | ✅ | - | GCS bucket for receipt storage |
| `SECRET_KEY` | ✅ | - | Application security key |

### **Server Settings**
| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8080` | Server port |
| `DEBUG` | `false` | Enable debug mode |
| `ENVIRONMENT` | `development` | Environment identifier |

### **AI/ML Configuration**
| Variable | Default | Description |
|----------|---------|-------------|
| `GENAI_MODEL` | `gemini-pro` | Gemini model to use |
| `GENAI_TEMPERATURE` | `0.7` | Model creativity (0-1) |
| `VISION_API_ENABLED` | `true` | Enable Vision API |
| `VISION_CONFIDENCE_THRESHOLD` | `0.7` | OCR confidence threshold |

### **Gamification Settings**
| Variable | Default | Description |
|----------|---------|-------------|
| `POINTS_PER_RECEIPT` | `10` | Base points per receipt |
| `BONUS_POINTS_MULTIPLIER` | `1.5` | Bonus calculation multiplier |
| `LARGE_PURCHASE_THRESHOLD` | `100` | Large purchase bonus trigger |
| `LARGE_PURCHASE_BONUS` | `10` | Bonus points for large purchases |

### **Feature Flags**
| Variable | Default | Description |
|----------|---------|-------------|
| `MOCK_EXTERNAL_APIS` | `false` | Use mock responses for testing |
| `ANALYTICS_ENABLED` | `true` | Enable analytics features |
| `GAMIFICATION_ENABLED` | `true` | Enable gamification system |
| `WALLET_ENABLED` | `true` | Enable wallet functionality |

For complete list, see [ENV_IMPLEMENTATION_SUMMARY.md](ENV_IMPLEMENTATION_SUMMARY.md)

## 🔧 Development Tools

### **Configuration Management**
```bash
# Validate environment variables
python test_env.py

# Print configuration summary
python -c "from utils.env_loader import print_config_summary; print_config_summary()"

# Check for missing required variables
python -c "from utils.env_loader import validate_required_config; print(validate_required_config())"
```

### **Testing & Validation**
```bash
# Test ADK agent functionality
python test_adk_agents.py

# Validate environment setup
python validate_env.py

# Run ADK workflow examples
python examples/adk_workflow_example.py
```
## ☁️ Google Cloud Deployment

### 1. Set up your Google Cloud Project

```bash
# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    storage.googleapis.com \
    firestore.googleapis.com \
    pubsub.googleapis.com \
    vision.googleapis.com \
    iam.googleapis.com \
    aiplatform.googleapis.com
```

run.googleapis.com 
    cloudbuild.googleapis.com 
    storage.googleapis.com 
    firestore.googleapis.com 
    pubsub.googleapis.com 
    vision.googleapis.com 
    iam.googleapis.com 
    aiplatform.googleapis.com

### 5. Create a Google Cloud Storage Bucket

Create a bucket to store the receipt images. Make sure the bucket name is globally unique.

```bash
gsutil mb gs://your-unique-bucket-name
```

### 6. Set Up Environment Variables

Create a `.env` file by copying the `.env.example` file:

```bash
cp .env.example .env
```

Now, edit the `.env` file and replace the placeholder values with your actual configuration:

```
GENAI_API_KEY="your-google-ai-api-key"
GCLOUD_STORAGE_BUCKET="your-unique-bucket-name"
FIRESTORE_PROJECT_ID="your-gcp-project-id"
```

### 7. Deploy to Cloud Run

Run the deployment script:

```bash
./cloud_run.sh
```

This script will use Cloud Build to build the Docker image, push it to Google Container Registry, and deploy it to Cloud Run.

## API Endpoints

Once deployed, you can interact with the API at the URL provided by Cloud Run.

*   `GET /`: Welcome message.
*   `POST /receipt/process-receipt`: Process a receipt image.
    *   **Body**: `{ "imageUrl": "gs://your-bucket/image.jpg", "userId": "user123" }`
*   `GET /analytics/spending-report/{user_id}`: Get a spending report for a user.
*   `POST /game/award-points`: Award points to a user.
    *   **Body**: `{ "userId": "user123", "receiptId": "receipt456" }`
*   `GET /wallet/balance/{user_id}`: Get the point balance for a user.

## Local Development

To run the application locally, follow these steps:

1.  **Activate the virtual environment**:
    ```bash
    source .venv/bin/activate
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Application Default Credentials (ADC)** for local authentication:
    ```bash
    gcloud auth application-default login
    ```

4.  **Run the development server**:
    ```bash
    ./devserver.sh
    ```

The application will be available at `http://127.0.0.1:8080`.
