"""
AI Website Testing Agent
A LangGraph-based agent for automated website testing using natural language
"""

from .langgraph_agent import (
    create_agent_graph,
    run_agent,
    get_initial_state,
    AgentState,
    TOOLS,
    navigate_to_url,
    fill_input_field,
    click_element,
    get_page_text,
    verify_element_exists,
    take_screenshot,
    get_current_page_info,
    wait_for_element,
    close_browser
)

from .browser_tools import (
    BrowserManager,
    run_browser_action
)

__all__ = [
    # Agent components
    "create_agent_graph",
    "run_agent",
    "get_initial_state",
    "AgentState",
    "TOOLS",
    # Browser tools
    "BrowserManager",
    "run_browser_action",
    # Individual tools
    "navigate_to_url",
    "fill_input_field",
    "click_element",
    "get_page_text",
    "verify_element_exists",
    "take_screenshot",
    "get_current_page_info",
    "wait_for_element",
    "close_browser"
]
