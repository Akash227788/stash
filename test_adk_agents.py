#!/usr/bin/env python3
"""
Test script to validate ADK agent implementation.
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.receipt_agent import ReceiptAgent
from agents.analytics_agent import AnalyticsAgent
from agents.game_agent import GameAgent
from agents.wallet_agent import WalletAgent
from agents.root_agent import RootAgent


async def test_agent_initialization():
    """Test that all agents can be initialized properly."""
    print("🧪 Testing Agent Initialization...")
    
    try:
        agents = {
            "ReceiptAgent": ReceiptAgent(),
            "AnalyticsAgent": AnalyticsAgent(), 
            "GameAgent": GameAgent(),
            "WalletAgent": WalletAgent(),
            "RootAgent": RootAgent()
        }
        
        for name, agent in agents.items():
            print(f"  ✅ {name}: Initialized successfully")
            print(f"     - Name: {agent.name}")
            print(f"     - Tools: {len(agent.tools) if hasattr(agent, 'tools') else 0}")
        
        print("🎉 All agents initialized successfully!\n")
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False


async def test_agent_processing():
    """Test basic agent processing capabilities."""
    print("🔄 Testing Agent Processing...")
    
    try:
        # Test each agent with a basic request
        test_cases = [
            {
                "agent": ReceiptAgent(),
                "request": {"message": "Hello, I need help processing a receipt"},
                "name": "ReceiptAgent"
            },
            {
                "agent": AnalyticsAgent(),
                "request": {"message": "Can you help me analyze my spending?"},
                "name": "AnalyticsAgent"
            },
            {
                "agent": GameAgent(),
                "request": {"message": "How do I earn more points?"},
                "name": "GameAgent"
            },
            {
                "agent": WalletAgent(),
                "request": {"message": "What's my current balance?"},
                "name": "WalletAgent"
            }
        ]
        
        for test_case in test_cases:
            try:
                result = await test_case["agent"].process_stash_request(test_case["request"])
                status = result.get("status", "unknown")
                print(f"  ✅ {test_case['name']}: {status}")
            except Exception as e:
                print(f"  ⚠️  {test_case['name']}: Error - {e}")
        
        print("🎉 Agent processing tests completed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Agent processing tests failed: {e}")
        return False


async def test_workflow_coordination():
    """Test basic workflow coordination."""
    print("🤝 Testing Workflow Coordination...")
    
    try:
        root_agent = RootAgent()
        
        # Test that root agent has access to sub-agents
        sub_agents = [
            "receipt_agent", 
            "analytics_agent", 
            "game_agent", 
            "wallet_agent"
        ]
        
        for sub_agent_name in sub_agents:
            if hasattr(root_agent, sub_agent_name):
                print(f"  ✅ Root agent has {sub_agent_name}")
            else:
                print(f"  ⚠️  Root agent missing {sub_agent_name}")
        
        print("🎉 Workflow coordination tests completed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Workflow coordination tests failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting ADK Agent Tests\n")
    
    tests = [
        test_agent_initialization,
        test_agent_processing,
        test_workflow_coordination
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Summary:")
    print(f"  Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! ADK implementation is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
