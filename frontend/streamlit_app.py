"""
Streamlit App for Expense Tracker with LangGraph and MCP Integration
"""
import streamlit as st
import asyncio
import os
from app.agents.expense_agent import get_agent

# Page configuration
st.set_page_config(
    page_title="Expense Tracker AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .ai-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .tool-info {
        background-color: #e8f5e8;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "tools" not in st.session_state:
        st.session_state.tools = []

async def load_agent():
    """Load the LangGraph agent"""
    try:
        agent = await get_agent()
        st.session_state.agent = agent
        st.session_state.tools = await agent.get_available_tools()
        return True
    except Exception as e:
        st.error(f"Failed to load agent: {str(e)}")
        return False

def display_tools():
    """Display available MCP tools"""
    if st.session_state.tools:
        st.subheader("🔧 Available Tools")
        for tool in st.session_state.tools:
            with st.expander(f"**{tool['name']}**"):
                st.write(f"**Description:** {tool['description']}")
                if tool.get('args'):
                    st.write(f"**Parameters:** {tool['args']}")

def display_chat_history():
    """Display chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show tool usage if available
            if message.get("tools_used"):
                st.markdown("**Tools Used:**")
                for tool in message["tools_used"]:
                    st.markdown(f"• {tool}")

def main():
    """Main Streamlit app"""
    st.markdown('<h1 class="main-header">💰 Expense Tracker AI</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # OpenAI API Key input
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key to enable AI features"
        )
        
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        
        # Load agent button
        if st.button("🔄 Load Agent", type="primary"):
            with st.spinner("Loading LangGraph agent with MCP tools..."):
                success = asyncio.run(load_agent())
                if success:
                    st.success("✅ Agent loaded successfully!")
                else:
                    st.error("❌ Failed to load agent")
        
        # Display tools
        if st.session_state.tools:
            display_tools()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    st.subheader("💬 Chat with Your Expense Tracker")
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    if prompt := st.chat_input("Ask me about your expenses..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        if st.session_state.agent:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = asyncio.run(st.session_state.agent.chat(prompt))
                        st.markdown(response)
                        
                        # Add AI response to chat history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response
                        })
                        
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_msg
                        })
        else:
            st.warning("Please load the agent first using the sidebar.")
    
    # Quick action buttons
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 View All Expenses"):
            if st.session_state.agent:
                prompt = "Show me all my expenses"
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()
    
    with col2:
        if st.button("📈 Monthly Summary"):
            if st.session_state.agent:
                prompt = "Give me a summary of this month's expenses by category"
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()
    
    with col3:
        if st.button("➕ Add Expense"):
            if st.session_state.agent:
                prompt = "Help me add a new expense"
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()
    
    with col4:
        if st.button("🔍 Search Expenses"):
            if st.session_state.agent:
                prompt = "Help me search for specific expenses"
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Expense Tracker AI** powered by LangGraph, MCP, and Streamlit | "
        "Make sure your FastAPI MCP server is running on http://localhost:8000"
    )

if __name__ == "__main__":
    main()
