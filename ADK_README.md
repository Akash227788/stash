# Stash ADK Implementation

This project now implements the **Agent Development Kit (ADK)** patterns for building sophisticated multi-agent AI systems. The Stash financial management system demonstrates various ADK architectural patterns and best practices.

## 🤖 ADK Agent Architecture

### Core Agents

1. **RootAgent** - Main coordinator implementing multi-agent orchestration
2. **ReceiptAgent** - Processes receipt images using LLM + tools
3. **AnalyticsAgent** - Provides spending insights and financial analysis
4. **GameAgent** - Manages gamification, points, and achievements
5. **WalletAgent** - Handles balances, transactions, and redemptions

### ADK Patterns Implemented

#### 1. LLM Agents (`LlmAgent`)
- **Purpose**: Intelligent reasoning and decision-making
- **Examples**: All specialized agents (Receipt, Analytics, Game, Wallet)
- **Features**: 
  - Tool integration for external API calls
  - Dynamic instruction processing
  - Context-aware responses

#### 2. Coordinator/Dispatcher Pattern
- **Implementation**: `RootAgent` routes requests to specialized agents
- **Benefits**: Clean separation of concerns, intelligent routing
- **Usage**: Root agent determines which specialist handles each request

#### 3. Sequential Workflow Pattern
- **Use Case**: Receipt processing pipeline
- **Flow**: Receipt Processing → Points Award → Wallet Update
- **Benefits**: Ensures proper order of operations, state passing

#### 4. Parallel Execution Pattern
- **Use Case**: Dashboard data gathering
- **Flow**: Analytics + Wallet + Achievements (simultaneously)
- **Benefits**: Improved performance, concurrent data fetching

#### 5. Tool Orchestration
- **Implementation**: Each agent has specialized tools
- **Examples**: 
  - ReceiptAgent: `extract_receipt_text`, `parse_receipt_data`
  - GameAgent: `calculate_points_reward`, `award_points_to_user`
  - WalletAgent: `get_user_balance`, `redeem_reward`

## 🚀 Getting Started with ADK

### Prerequisites
```bash
pip install google-adk
pip install -r requirements.txt
```

### Run ADK Server
```bash
# ADK-powered server
python adk_main.py

# Traditional FastAPI (for comparison)
python main.py
```

### Basic Usage

```python
from agents.receipt_agent import ReceiptAgent
from google.adk import Session

# Initialize agent
receipt_agent = ReceiptAgent()

# Process with ADK patterns
result = await receipt_agent.process({
    "operation": "process_receipt",
    "imageUrl": "gs://bucket/receipt.jpg",
    "userId": "user123"
})
```

## 📋 API Endpoints (ADK-powered)

### Core Operations
- `POST /adk/receipt/process` - Process receipt with full workflow
- `GET /adk/analytics/{user_id}` - Generate spending insights
- `POST /adk/game/award-points` - Award points for actions
- `GET /adk/wallet/{user_id}` - Check balance and transactions
- `GET /adk/dashboard/{user_id}` - Comprehensive user dashboard

### ADK-Specific Features
- `GET /adk/health` - Agent status and health check
- `GET /` - ADK architecture information

## 🔄 Workflow Examples

### 1. Receipt Processing Workflow (Sequential)
```python
async def process_receipt_workflow(image_url: str, user_id: str):
    # Step 1: Extract and parse receipt data
    receipt_result = await receipt_agent.process({
        "operation": "process_receipt",
        "imageUrl": image_url,
        "userId": user_id
    })
    
    # Step 2: Award points based on receipt
    game_result = await game_agent.process({
        "operation": "award_points", 
        "userId": user_id,
        "receiptData": receipt_result["data"]
    })
    
    # Step 3: Update wallet balance
    wallet_result = await wallet_agent.process({
        "operation": "get_balance",
        "userId": user_id
    })
    
    return compile_workflow_results(receipt_result, game_result, wallet_result)
```

### 2. Dashboard Generation (Parallel)
```python
async def generate_dashboard(user_id: str):
    # Execute multiple agents in parallel
    tasks = [
        analytics_agent.process({"operation": "generate_report", "userId": user_id}),
        wallet_agent.process({"operation": "get_balance", "userId": user_id}),
        game_agent.process({"operation": "get_achievements", "userId": user_id})
    ]
    
    results = await asyncio.gather(*tasks)
    return combine_dashboard_data(results)
```

## 🛠 Agent Tools Integration

Each agent uses specialized tools following ADK patterns:

### Receipt Agent Tools
```python
@tool
def extract_receipt_text(image_url: str) -> Dict[str, Any]:
    """Extracts text from receipt images using Cloud Vision AI."""
    # Implementation using Google Cloud Vision

@tool  
def parse_receipt_data(text: str) -> Dict[str, Any]:
    """Parses receipt text to extract structured data."""
    # LLM-powered parsing logic
```

### Game Agent Tools
```python
@tool
def calculate_points_reward(receipt_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates points based on receipt data with bonuses."""
    # Points calculation with merchant bonuses, streaks, etc.

@tool
def award_points_to_user(user_id: str, points: int, reason: str) -> Dict[str, Any]:
    """Awards points to user account."""
    # Firestore transaction to update user points
```

## 🧠 ADK Agent Intelligence

### Dynamic Instruction Processing
Agents use context-aware instructions that adapt to the request:

```python
instruction = """You are a Receipt Processing Agent specialized in extracting data from receipt images.

When processing a receipt:
1. Use extract_receipt_text to get OCR data
2. Use parse_receipt_data to structure the information  
3. Use store_receipt_data to save the results
4. Always provide clear summaries of extracted information

Be thorough and accurate in data extraction."""
```

### State Management
Agents share state through ADK sessions:

```python
# Agent 1 sets state
session.state["receipt_data"] = extracted_data

# Agent 2 reads state  
receipt_info = session.state.get("receipt_data", {})
```

## 📊 Monitoring and Observability

### Agent Health Checking
```bash
curl http://localhost:8080/adk/health
```

Returns:
```json
{
  "status": "healthy",
  "adk_version": "google-adk", 
  "agents": {
    "root_agent": "initialized",
    "receipt_agent": "ready",
    "analytics_agent": "ready",
    "game_agent": "ready", 
    "wallet_agent": "ready"
  },
  "patterns_supported": [
    "Sequential workflows",
    "Parallel execution", 
    "Agent coordination",
    "State management",
    "Tool orchestration"
  ]
}
```

## 🔧 Development and Testing

### Run Workflow Examples
```bash
python examples/adk_workflow_example.py
```

### Test Individual Agents
```python
# Test receipt processing
receipt_agent = ReceiptAgent()
result = await receipt_agent.process({
    "operation": "process_receipt",
    "imageUrl": "test_image.jpg",
    "userId": "test_user"
})
```

## 🏗 Architecture Benefits

### Traditional vs ADK Approach

| Traditional FastAPI | ADK Agent System |
|-------------------|------------------|
| Route-based handlers | Intelligent agent coordination |
| Manual orchestration | Built-in workflow patterns |
| Static request routing | Dynamic LLM-driven decisions |
| Limited tool integration | Rich tool ecosystem |
| Manual state management | Automatic session state |

### Scalability Features
- **Agent Hierarchy**: Clear parent-child relationships
- **Tool Reusability**: Shared tools across agents
- **State Persistence**: ADK session management
- **Error Handling**: Built-in agent error recovery
- **Observability**: Automatic agent lifecycle tracking

## 📚 Further Reading

- [ADK Documentation](https://google.github.io/adk-docs/)
- [LLM Agent Patterns](https://google.github.io/adk-docs/agents/llm-agents/)
- [Multi-Agent Systems](https://google.github.io/adk-docs/agents/multi-agents/)
- [Workflow Agents](https://google.github.io/adk-docs/agents/workflow-agents/)

## 🤝 Contributing

When adding new features:
1. Follow ADK agent patterns
2. Implement proper tool integration
3. Add comprehensive error handling
4. Update agent instructions appropriately
5. Test multi-agent coordination scenarios

The ADK implementation provides a more robust, scalable, and intelligent approach to building the Stash financial management system.
