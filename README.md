# Self-Care Agent Framework

General-purpose healthcare self-care agent framework with core functionalities for triage, commodity ordering, pharmacy services, and referrals. Built with LangGraph for multi-step reasoning and tool chaining.

## P0: Core Framework

The current implementation provides a foundational agent framework with essential self-care capabilities:

### Core Features

- **Multi-Channel Support**: Unified agent accessible via multiple channels
  - Streamlit UI for web-based interactions
  - WhatsApp webhook integration for messaging
  - Extensible channel architecture for future integrations

- **Agent Architecture**:
  - LangGraph-based agent with native tool calling
  - Multi-step reasoning and automatic tool chaining
  - Context-aware tool execution with user session management

- **Core Tools**:
  - **Triage & Risk Assessment**: Symptom evaluation and risk flagging
  - **Commodity Orders**: Self-test kits and health commodity fulfillment
  - **Pharmacy Services**: Prescription refills and medication orders
  - **Referrals & Scheduling**: Clinical appointment booking and referrals
  - **Database Queries**: User data and interaction history access

- **Infrastructure**:
  - PostgreSQL database for user data and interactions
  - Docker-based development environment
  - Separate containers for UI and webhook services
  - Automatic interaction logging and storage

### Architecture Highlights

- **Channel Abstraction**: Base channel handler class for consistent agent access
- **Shared Agent Core**: Single agent instance used across all channels
- **Tool-Based Workflow**: Modular tools that can be chained based on user needs
- **User Context Management**: Thread-safe user context for multi-user scenarios

### Design Decision: Single Agent Architecture

The framework uses a **single agent** approach where one agent orchestrates all interactions and tool calls. This design choice offers:

- **Simplicity**: Single agent is easier to manage, debug, and maintain
- **Flexibility**: Agent can dynamically chain any combination of tools based on user needs
- **Consistency**: Unified reasoning and decision-making across all interactions
- **Tool Specialization**: Specialized functionality lives in tools, not separate agents

**Alternative Consideration (Multi-Agent)**: For P1 HIV use case, we could consider a specialized HIV agent that collaborates with the main agent, but the current single-agent design with specialized tools is likely sufficient and maintains simplicity.

## P1: HIV Use Case Extension

Building on the core framework, the next phase will add HIV-specific modules without changing the underlying architecture:

### Planned Modules

- **HIV-Specific Tools**:
  - HIV risk assessment and testing guidance
  - PrEP/PEP information and access
  - ART medication management
  - HIV care navigation and support

- **Clinical Protocols**:
  - HIV testing protocols and recommendations
  - Treatment adherence support
  - Stigma reduction and counseling guidance
  - Linkage to care workflows

- **Data & Analytics**:
  - HIV-specific interaction tracking
  - Testing and treatment outcome metrics
  - Care pathway analytics

### Implementation Approach

- **No Architectural Changes**: All HIV functionality will be added as new tools and protocols
- **Reuse Existing Infrastructure**: Leverage current channel architecture, database, and agent framework
- **Modular Design**: HIV tools will follow the same pattern as existing tools
- **Backward Compatible**: Core self-care functionality remains unchanged
- **Single Agent Continuation**: HIV functionality will be integrated into the existing single agent through specialized tools, maintaining the current architecture's simplicity and flexibility

## Setup

1. Create and activate virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Create `.env` file and add your OpenAI API key:

```
cp .env.example .env
```

Then edit `.env` and set `OPENAI_API_KEY=your_key_here`

## Usage

```
source venv/bin/activate
python streamlit_server.py
```

Then wait for interface to launch...

## Structure

- `streamlit_server.py` - Streamlit UI server entry point
- `webhook_server.py` - FastAPI webhook server entry point
- `src/agent.py` - LangGraph agent with tool calling
- `src/channels/` - Channel handlers
  - `base.py` - Base channel handler class
  - `streamlit.py` - Streamlit UI channel
  - `whatsapp.py` - WhatsApp webhook channel
- `src/tools/` - Tool implementations
  - `triage.py` - Triage and risk assessment
  - `commodity.py` - Commodity orders
  - `pharmacy.py` - Pharmacy services
  - `referrals.py` - Referrals and scheduling
  - `database.py` - Database queries
- `src/utils/` - Shared utilities (logger, context, user lookup, etc.)
- `src/config.py` - Application configuration defaults
