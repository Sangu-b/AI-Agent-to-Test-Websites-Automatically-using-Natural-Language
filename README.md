# AI Website Testing Agent _[in development]_

An AI-powered agent that tests websites automatically using natural language commands. Built with LangGraph, Playwright, and Flask.

## Project Structure

```
├── agent/
│   ├── __init__.py           # Package initialization with exports
│   ├── langgraph_agent.py    # LangGraph agent with tool bindings
│   └── browser_tools.py      # Playwright browser automation tools
├── templates/
│   ├── login.html            # Test login page
│   └── dashboard.html        # Test dashboard page
├── app.py                    # Flask server for test website
├── test_login.py             # Comprehensive Playwright test suite
├── demo_playwright.py        # Simple Playwright demo script
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
├── .env                      # Your environment configuration
└── README.md                 # This file
```

## Features

- **Natural Language Testing**: Use plain English commands to test websites
- **Playwright Integration**: Robust browser automation with Chromium
- **LangGraph Agent**: AI-powered decision making for test execution
- **Comprehensive Test Suite**: Pre-built tests for login functionality
- **Visual Demo Mode**: Watch the automation in action
- **Screenshot Capture**: Automatic documentation of test results

## Quick Start

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
python -m playwright install
```

### 5. Configure Environment (Optional - for AI Agent)

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI API key:
```
OPENAI_API_KEY=your_actual_api_key_here
```

## Usage

### Step 1: Start the Test Website

Run the Flask server to start the test login page:

```bash
python app.py
```

The server will start at `http://localhost:5000`

**Test Credentials:**
- Username: `testuser`
- Password: `testpass`

### Step 2: Run Tests

You have three options:

#### Option A: Simple Playwright Demo (No API Key Needed)

```bash
python demo_playwright.py
```

This runs a visual demonstration of the login flow with step-by-step output.

Quick headless test:
```bash
python demo_playwright.py --quick
```

#### Option B: Comprehensive Test Suite

```bash
python test_login.py
```

This runs all tests with a visible browser. For headless mode:
```bash
python test_login.py --headless
```

For a quick visual demo:
```bash
python test_login.py --demo
```

#### Option C: AI Agent (Requires OpenAI API Key)

```bash
python -m agent.langgraph_agent
```

### Example AI Agent Commands

Once the agent is running, you can give it natural language commands like:

- "Navigate to http://localhost:5000"
- "Fill in the username field with 'testuser'"
- "Enter 'testpass' in the password field"
- "Click the login button"
- "Verify we are on the dashboard"
- "Take a screenshot"
- "Test the login with invalid credentials"

## Test Suite Results

The test suite (`test_login.py`) includes the following tests:

| Test | Description |
|------|-------------|
| Login Page Loads | Verifies the page loads with all required elements |
| Empty Form Validation | Checks HTML5 required field validation |
| Invalid Credentials Rejected | Verifies error handling for wrong credentials |
| Valid Login Succeeds | Tests successful authentication |
| Redirect to Dashboard | Verifies navigation after login |
| Dashboard Logout | Tests the logout functionality |
| Screenshot Capture | Documents the test flow with screenshots |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Login page |
| `/login` | POST | Handle login submission |
| `/dashboard` | GET | Dashboard page (after login) |
| `/health` | GET | Health check endpoint |

## Project Components

### Browser Tools (`agent/browser_tools.py`)

The `BrowserManager` class provides:
- `navigate(url)` - Navigate to a URL
- `fill(selector, value)` - Fill form fields
- `click(selector)` - Click elements
- `get_text(selector)` - Read element text
- `verify_element_exists(selector)` - Check element presence
- `screenshot(path)` - Capture screenshots
- `wait_for_selector(selector)` - Wait for elements

### LangGraph Agent (`agent/langgraph_agent.py`)

AI-powered testing agent with:
- Natural language understanding
- Tool-based browser control
- State management for multi-step tests
- Automatic action planning

### Available Tools for AI Agent

| Tool | Description |
|------|-------------|
| `navigate_to_url` | Navigate browser to URL |
| `fill_input_field` | Fill text into input fields |
| `click_element` | Click on page elements |
| `get_page_text` | Read text from elements |
| `verify_element_exists` | Check if element exists |
| `take_screenshot` | Capture page screenshot |
| `get_current_page_info` | Get current URL and title |
| `wait_for_element` | Wait for element to appear |
| `close_browser` | Close browser session |

## Troubleshooting

### Flask Server Not Starting
- Ensure port 5000 is not in use
- Check if Flask is installed: `pip install flask`

### Playwright Not Working
- Install browsers: `python -m playwright install`
- On Linux, install dependencies: `python -m playwright install-deps`

### AI Agent Not Responding
- Verify OpenAI API key is set in `.env`
- Check API key validity
- Ensure you have API credits

### Tests Failing
- Make sure Flask server is running on port 5000
- Wait a few seconds after starting the server

## License

This project is for educational and demonstration purposes.
- "Fill in the password field with 'testpass'"
- "Click the login button"
- "Verify that the login was successful"
- "Take a screenshot of the current page"

## Architecture

### LangGraph Agent

The agent uses LangGraph to orchestrate the testing workflow:

1. **Parse Input Node**: Analyzes natural language commands to understand testing intent
2. **Execute Action Node**: Performs browser automation using Playwright
3. **Conditional Edge**: Determines if more actions are needed or if testing is complete

### Browser Tools

Playwright-based utilities for:
- Page navigation
- Form filling
- Button clicking
- Element verification
- Screenshot capture
- Content validation

## Development

### Running Tests

```bash
# Test browser tools
python -m agent.browser_tools
```

### Adding New Capabilities

1. Add new action methods to `BrowserManager` in `browser_tools.py`
2. Update the agent's system prompt in `langgraph_agent.py`
3. Extend the graph nodes as needed

## License

MIT License
