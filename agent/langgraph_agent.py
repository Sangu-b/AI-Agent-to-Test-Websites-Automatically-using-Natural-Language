"""
LangGraph Agent Configuration
Handles user inputs and orchestrates website testing using natural language
"""

import os
import asyncio
from typing import TypedDict, Annotated, Sequence, Literal, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .browser_tools import BrowserManager

# Load environment variables
load_dotenv()

# Global browser manager instance
_browser_manager: Optional[BrowserManager] = None


def get_browser_manager() -> BrowserManager:
    """Get or create the browser manager instance"""
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager()
    return _browser_manager


async def ensure_browser_initialized():
    """Ensure the browser is initialized"""
    manager = get_browser_manager()
    if manager.browser is None:
        await manager.initialize(headless=False)
    return manager


# Define tools for the agent
@tool
def navigate_to_url(url: str) -> str:
    """Navigate to a specified URL in the browser.
    
    Args:
        url: The URL to navigate to (e.g., 'http://localhost:5000')
    
    Returns:
        Result of the navigation including page title
    """
    async def _navigate():
        manager = await ensure_browser_initialized()
        result = await manager.navigate(url)
        return f"Navigated to {url}. Page title: {result['title']}"
    
    return asyncio.get_event_loop().run_until_complete(_navigate())


@tool
def fill_input_field(selector: str, value: str) -> str:
    """Fill a text input field with a value.
    
    Args:
        selector: CSS selector for the input field (e.g., '#username', '#password')
        value: The text value to enter into the field
    
    Returns:
        Confirmation of the fill action
    """
    async def _fill():
        manager = await ensure_browser_initialized()
        await manager.fill(selector, value)
        return f"Filled '{selector}' with value '{value}'"
    
    return asyncio.get_event_loop().run_until_complete(_fill())


@tool
def click_element(selector: str) -> str:
    """Click on an element on the page.
    
    Args:
        selector: CSS selector for the element to click (e.g., '#loginBtn', '.submit-btn')
    
    Returns:
        Confirmation of the click action
    """
    async def _click():
        manager = await ensure_browser_initialized()
        await manager.click(selector)
        return f"Clicked on element '{selector}'"
    
    return asyncio.get_event_loop().run_until_complete(_click())


@tool
def get_page_text(selector: str) -> str:
    """Get the text content of an element on the page.
    
    Args:
        selector: CSS selector for the element to read
    
    Returns:
        The text content of the element
    """
    async def _get_text():
        manager = await ensure_browser_initialized()
        text = await manager.get_text(selector)
        return f"Text content of '{selector}': {text}"
    
    return asyncio.get_event_loop().run_until_complete(_get_text())


@tool
def verify_element_exists(selector: str) -> str:
    """Verify if an element exists on the page.
    
    Args:
        selector: CSS selector for the element to check
    
    Returns:
        Whether the element exists or not
    """
    async def _verify():
        manager = await ensure_browser_initialized()
        result = await manager.verify_element_exists(selector)
        exists = result['exists']
        return f"Element '{selector}' {'exists' if exists else 'does not exist'} on the page"
    
    return asyncio.get_event_loop().run_until_complete(_verify())


@tool
def take_screenshot(filename: str = "screenshot.png") -> str:
    """Take a screenshot of the current page.
    
    Args:
        filename: Name of the file to save the screenshot (default: screenshot.png)
    
    Returns:
        Confirmation that the screenshot was saved
    """
    async def _screenshot():
        manager = await ensure_browser_initialized()
        await manager.screenshot(filename)
        return f"Screenshot saved as '{filename}'"
    
    return asyncio.get_event_loop().run_until_complete(_screenshot())


@tool
def get_current_page_info() -> str:
    """Get information about the current page.
    
    Returns:
        Current URL and page title
    """
    async def _get_info():
        manager = await ensure_browser_initialized()
        info = await manager.get_page_info()
        return f"Current URL: {info['url']}, Title: {info['title']}"
    
    return asyncio.get_event_loop().run_until_complete(_get_info())


@tool
def wait_for_element(selector: str, timeout: int = 5000) -> str:
    """Wait for an element to appear on the page.
    
    Args:
        selector: CSS selector for the element to wait for
        timeout: Maximum time to wait in milliseconds (default: 5000)
    
    Returns:
        Whether the element appeared or timed out
    """
    async def _wait():
        manager = await ensure_browser_initialized()
        result = await manager.wait_for_selector(selector, timeout)
        if result['success']:
            return f"Element '{selector}' appeared on the page"
        else:
            return f"Timeout waiting for element '{selector}': {result.get('error', 'Unknown error')}"
    
    return asyncio.get_event_loop().run_until_complete(_wait())


@tool
def close_browser() -> str:
    """Close the browser and cleanup resources.
    
    Returns:
        Confirmation that the browser was closed
    """
    global _browser_manager
    
    async def _close():
        global _browser_manager
        if _browser_manager:
            await _browser_manager.close()
            _browser_manager = None
        return "Browser closed successfully"
    
    return asyncio.get_event_loop().run_until_complete(_close())


# List of all available tools
TOOLS = [
    navigate_to_url,
    fill_input_field,
    click_element,
    get_page_text,
    verify_element_exists,
    take_screenshot,
    get_current_page_info,
    wait_for_element,
    close_browser
]


class AgentState(TypedDict):
    """State definition for the LangGraph agent"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    current_url: str
    test_results: list
    browser_state: dict


# System prompt for the testing agent
SYSTEM_PROMPT = """You are an AI agent specialized in testing websites automatically using natural language commands.

You have access to browser automation tools that let you:
1. Navigate to web pages using navigate_to_url
2. Fill out forms using fill_input_field (use CSS selectors like '#username', '#password')
3. Click buttons and links using click_element
4. Verify page content using verify_element_exists and get_page_text
5. Take screenshots using take_screenshot
6. Get current page info using get_current_page_info
7. Wait for elements using wait_for_element
8. Close browser using close_browser

When testing a login page at http://localhost:5000:
- The username field has selector '#username'
- The password field has selector '#password'  
- The login button has selector '#loginBtn'
- Success/error messages appear in '#message'

Always execute the browser actions using the available tools. After each action, report what happened.
When the user says they are done or wants to stop, close the browser.
"""


def create_llm():
    """Create and configure the LLM instance with tools"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError(
            "OpenAI API key not configured. "
            "Please set OPENAI_API_KEY in your .env file"
        )
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key
    )
    
    # Bind tools to the LLM
    return llm.bind_tools(TOOLS)


def agent_node(state: AgentState) -> AgentState:
    """
    The main agent node that processes messages and decides on actions.
    """
    messages = state["messages"]
    
    # Get the LLM with tools
    llm = create_llm()
    
    # Add system message for context
    system_message = SystemMessage(content=SYSTEM_PROMPT)
    full_messages = [system_message] + list(messages)
    
    response = llm.invoke(full_messages)
    
    return {
        **state,
        "messages": list(messages) + [response]
    }


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """
    Determine if the agent should continue executing tools or end.
    """
    messages = state["messages"]
    
    if not messages:
        return "end"
    
    last_message = messages[-1]
    
    # Check if the LLM wants to call tools
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    return "end"


def create_agent_graph():
    """
    Create the LangGraph workflow for the testing agent with tool support.
    
    Graph structure:
    1. Agent node → Decides what action to take
    2. Tool node → Executes browser automation tools
    3. Loop back to agent or end
    """
    # Initialize the graph with our state schema
    workflow = StateGraph(AgentState)
    
    # Create tool node
    tool_node = ToolNode(TOOLS)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Set the entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges from agent
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # Tools always go back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    return workflow.compile()


def get_initial_state() -> AgentState:
    """Create the initial state for a new testing session"""
    return AgentState(
        messages=[],
        current_url="",
        test_results=[],
        browser_state={}
    )


def run_agent(user_input: str, state: AgentState = None) -> AgentState:
    """
    Run the agent with a user input.
    
    Args:
        user_input: Natural language command from the user
        state: Optional existing state to continue from
    
    Returns:
        Updated agent state after processing
    """
    if state is None:
        state = get_initial_state()
    
    # Add the user message to state
    state["messages"] = list(state["messages"]) + [HumanMessage(content=user_input)]
    
    # Create and run the graph
    graph = create_agent_graph()
    result = graph.invoke(state)
    
    return result


# Interactive mode for testing
if __name__ == "__main__":
    print("=" * 60)
    print("AI Website Testing Agent - Interactive Mode")
    print("=" * 60)
    print("\nType your testing commands in natural language.")
    print("Type 'quit' or 'exit' to end the session.")
    print("Type 'clear' to start a new testing session.\n")
    
    state = get_initial_state()
    
    while True:
        try:
            user_input = input("\n🧪 Test Command > ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("\nGoodbye! 👋")
                break
            
            if user_input.lower() == 'clear':
                state = get_initial_state()
                print("\n✨ Session cleared. Starting fresh.")
                continue
            
            print("\n🔄 Processing...")
            state = run_agent(user_input, state)
            
            # Display the last AI response
            if state["messages"]:
                last_message = state["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(f"\n🤖 Agent Response:\n{last_message.content}")
                    
        except ValueError as e:
            print(f"\n⚠️ Configuration Error: {e}")
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
