"""
LangGraph Agent with MCP Integration for Expense Tracker
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_react_agent
from config import settings

class ExpenseTrackerAgent:
    """LangGraph agent that uses MCP tools for expense tracking"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or settings.openai_api_key
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=self.openai_api_key,
            temperature=0.1
        )
        self.agent = None
        self.tools = None
        
    async def initialize(self):
        """Initialize the MCP client and create the agent"""
        # Configure MCP client to connect to your FastAPI MCP server
        client = MultiServerMCPClient(
            {
                "expense_tracker": {
                    "transport": "streamable_http",
                    "url": "http://localhost:8000/mcp",  # Your FastAPI MCP endpoint
                    "headers": {
                        "Content-Type": "application/json"
                    }
                }
            }
        )
        
        # Get tools from MCP server
        self.tools = await client.get_tools()
        
        # Create LangChain agent
        self.agent = create_react_agent(self.model, self.tools)
        
        return self.agent
    
    async def chat(self, message: str) -> str:
        """Process a user message and return AI response"""
        if not self.agent:
            await self.initialize()
        
        try:
            # Process the message with LangChain agent
            response = await self.agent.ainvoke({"input": message})
            
            # Extract the output
            if isinstance(response, dict) and "output" in response:
                return response["output"]
            elif isinstance(response, str):
                return response
            
            return "I'm sorry, I couldn't process your request properly."
            
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools"""
        if not self.tools:
            await self.initialize()
        
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "args": tool.args if hasattr(tool, 'args') else {}
            }
            for tool in self.tools
        ]

# Global agent instance
agent_instance = None

async def get_agent():
    """Get or create the agent instance"""
    global agent_instance
    if agent_instance is None:
        agent_instance = ExpenseTrackerAgent()
        await agent_instance.initialize()
    return agent_instance
