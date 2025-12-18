# Agent Architecture

> **Note:** This is a prototype implementation. The agent architecture uses LangGraph for multi-step reasoning and tool chaining. The system prompt and workflow patterns represent architectural slots for future integration with a deployable system.

## Architecture Overview

The agent is built using **LangGraph** with native tool calling, enabling:
- Multi-step reasoning and tool chaining
- Automatic tool execution loop
- Error correction (agent can retry tools with new parameters)
- Safety checks between tool calls
- Context-aware tool execution

### Core Components

1. **LangGraph StateGraph**: Manages agent state and message flow
2. **OpenAI Chat Model**: Provides reasoning and tool selection
3. **Tool Node**: Executes tool calls in parallel
4. **Context Variables**: Thread-safe user context for tools
5. **Interaction Storage**: Automatic logging of all interactions

---

## Agent State

The agent maintains state through a `TypedDict` that persists across the execution loop:

```python
class AgentState(TypedDict, total=False):
    messages: Annotated[list, lambda x, y: x + y]  # Message history (accumulates)
    system_prompt: Optional[str]                     # Custom system prompt (optional)
    user_id: Optional[str]                          # Current user ID for context
```

**State Properties:**
- `messages`: Accumulates all messages (HumanMessage, AIMessage, ToolMessage) throughout the conversation
- `system_prompt`: Allows custom system prompts per request (defaults to `SYSTEM_PROMPT`)
- `user_id`: Sets user context for tools to access current user data

---

## System Prompt Structure

The system prompt uses hierarchical organization to reduce context confusion and improve tool calling reliability:

### Core Workflow (Priority Order)

1. **Triage First**: Mandatory for any health-related query
2. **Fulfill All Requests**: Complete all user-requested actions before ending
3. **Chain Tools**: Use tool results to determine next steps

### Risk-Based Actions

Clear rules for handling different risk levels:
- **High/Critical**: Emergency instructions → Recommend evaluation → Ask for consent → Schedule (if consented)
- **Medium**: Recommend evaluation → Ask before scheduling
- **Low**: Suggest self-care or pharmacy support

### Safety and Consent

- Prioritize user safety (emergency instructions first)
- Always ask for consent before scheduling
- Respond with questions instead of calling tools when consent/info needed

### Communication

- Clear and empathetic responses
- Provide summaries when tools complete
- Verify all requests fulfilled before ending

**Architectural Note:** The prompt structure follows context engineering best practices:
- Hierarchical sections instead of flat numbered lists
- Reduced redundancy (consolidated from 56 lines to ~43 lines)
- Clear priority emphasis (triage first)
- Grouped by concern (workflow, risk, safety, communication)

---

## Message Flow

The agent follows a loop pattern until completion:

```
User Input
    ↓
[Agent Node] → LLM decides: tool call or response?
    ↓                    ↓
[Tool Node]          [END]
    ↓
[Agent Node] → Process tool results, decide next step
    ↓
[END] or [Tool Node] (if more tools needed)
```

### Execution Steps

1. **Entry Point**: Agent node receives user input + conversation history
2. **LLM Decision**: Model decides whether to:
   - Call tools (returns `AIMessage` with `tool_calls`)
   - Provide final response (returns `AIMessage` with `content`)
3. **Tool Execution**: If tools are called, `ToolNode` executes them in parallel
4. **Result Processing**: Tool results are added as `ToolMessage` objects
5. **Loop Back**: Agent processes tool results and decides next step
6. **Completion**: Agent returns final response when all actions complete

### Conditional Edges

The `should_continue()` function determines flow:
- If last message is `AIMessage` with `tool_calls` → route to `"tools"`
- Otherwise → route to `"end"`

This creates an automatic loop that continues until the agent decides no more tools are needed.

---

## Tool Calling Mechanism

### Native Tool Binding

Tools are bound to the LLM using LangChain's native tool calling:

```python
llm = ChatOpenAI(model=llm_model, temperature=temperature)
llm_with_tools = llm.bind_tools(TOOLS)  # Binds all tools from src.tools
```

**Available Tools:**
- `triage_and_risk_flagging`
- `commodity_orders_and_fulfillment`
- `pharmacy_orders_and_fulfillment`
- `referrals_and_scheduling`
- `database_query`

### Tool Execution

The `ToolNode` (LangGraph prebuilt) handles:
- Parallel tool execution (multiple tools can be called simultaneously)
- Tool result formatting (converts to `ToolMessage`)
- Error handling (tool failures are captured in messages)

### Tool Result Processing

Tool results are automatically added to the message history:
- Structured JSON responses (triage tool) are parsed by the agent
- String responses (other tools) are included as-is
- Agent analyzes results to determine next steps

---

## Context Management

### User Context Variable

Tools access the current user via a thread-safe context variable:

```python
from contextvars import ContextVar
current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)
```

**Context Flow:**
1. `process_message()` receives `user_id` parameter
2. User ID is set in state: `state = {"messages": messages, "user_id": user_id}`
3. Before LLM call: `current_user_id.set(user_id)` in `call_model()`
4. Before tool execution: `current_user_id.set(user_id)` in `call_tools()`
5. Tools access: `user_id = current_user_id.get()`

**Benefits:**
- Thread-safe (works with async/concurrent requests)
- No need to pass user_id through every tool parameter
- Tools automatically have access to current user context

### Session Management

The Streamlit interface manages user sessions:
- User identification via email/phone lookup
- Session state stores `user_id` for all requests
- Conversation history maintained in session state

---

## Interaction Storage

All interactions are automatically stored in the database for audit and continuity of care:

**What's Stored:**
- User input and conversation history
- Tools called and their results
- Triage assessments and risk levels
- Timestamp and channel metadata

**Storage Architecture:**
- Automatic logging after each `process_message()` call
- Tool metadata extracted from message chain
- Structured storage in `interactions` table

See `docs/reference/database.md` for complete schema and query examples.

---

## Workflow Patterns

### Single Tool Call

```
User: "I have chest pain"
  ↓
Agent → triage_and_risk_flagging
  ↓
Agent → Response with risk assessment
```

### Tool Chaining

```
User: "I have symptoms and need medication"
  ↓
Agent → triage_and_risk_flagging
  ↓
Agent → commodity_orders_and_fulfillment
  ↓
Agent → Response with triage + order confirmation
```

### Multi-Step with Consent

```
User: "I'm having trouble breathing"
  ↓
Agent → triage_and_risk_flagging (high risk detected)
  ↓
Agent → "This is serious. Would you like me to schedule an appointment?"
  ↓
User: "Yes"
  ↓
Agent → referrals_and_scheduling
  ↓
Agent → Response with appointment details
```

### Error Recovery

If a tool fails or returns insufficient data:
- Agent can call the tool again with different parameters
- Agent can call alternative tools
- Agent can ask user for clarification

This is handled automatically by the LangGraph loop.

---

## Message Processing

### Input Processing

`process_message()` handles:
1. **Conversation History**: Builds message list from previous turns
2. **Current Message**: Adds new user input as `HumanMessage`
3. **State Creation**: Creates agent state with messages and user_id
4. **Agent Invocation**: Runs agent workflow
5. **Result Extraction**: Extracts final response from message chain
6. **Interaction Storage**: Saves interaction to database
7. **Response Formatting**: Adds tool execution info for debugging

### Response Format

Responses include tool execution metadata (for debugging):
```
[Main response text]

[tool execution: tool: triage_and_risk_flagging, tool executed, tool: commodity_orders_and_fulfillment, tool executed]
```

**Note:** Tool execution info is stripped from conversation history to keep it clean.

---

## Configuration

### Agent Creation

```python
agent = create_agent(
    llm_model="gpt-4o",  # or other OpenAI model
    temperature=0.7       # Controls randomness
)
```

**Model Requirements:**
- Must support native tool calling (OpenAI models: gpt-4, gpt-4-turbo, gpt-4o, etc.)
- Temperature affects tool selection consistency (lower = more consistent)

### System Prompt Customization

Custom system prompts can be passed per request:
```python
state = {
    "messages": messages,
    "user_id": user_id,
    "system_prompt": "custom prompt here"  # Overrides default
}
```

**Use Cases:**
- A/B testing different prompt strategies
- Specialized workflows for different user types
- Context-specific instructions

---

## Architectural Considerations

### Current Implementation (Prototype)

- **Tool Responses**: Mocked data (order IDs, appointment IDs, etc.)
- **Tool Schemas**: Represent architectural contracts
- **Message Flow**: Fully functional multi-step reasoning
- **Context Management**: Thread-safe user context
- **Storage**: Automatic interaction logging

### Future Integration Points

1. **Tool Integration**: Replace mocked responses with real API calls
2. **Enhanced Storage**: Add `tools` JSONB column for full audit trail
3. **Error Handling**: More sophisticated error recovery and user feedback
4. **Streaming**: Support streaming responses for better UX
5. **Multi-Modal**: Support image/voice inputs for symptom assessment
6. **Analytics**: Tool usage analytics and performance monitoring
7. **A/B Testing**: System prompt experimentation framework

### Performance Considerations

- **Token Usage**: System prompt + conversation history + tool definitions
- **Latency**: Each tool call adds round-trip time
- **Cost**: Tool calls count toward API usage
- **Caching**: Consider caching tool results for repeated queries

### Security Considerations

- **User Isolation**: Context variables ensure tools only access current user data
- **Input Validation**: Tools should validate inputs before execution
- **Audit Trail**: All interactions logged for compliance
- **Consent Management**: Explicit consent required for sensitive actions (scheduling)

---

## Debugging and Monitoring

### Logging

The agent logs:
- Tool calls: `"calling tool: {tool_name} with args: {args}"`
- Tool results: `"tool result: {content[:200]}"`
- Interaction saves: `"saved interaction: {interaction_id}"`

### Message Inspection

The message chain contains full execution history:
- `HumanMessage`: User inputs
- `AIMessage`: Agent reasoning and tool calls
- `ToolMessage`: Tool execution results

This enables:
- Debugging tool selection issues
- Understanding agent reasoning
- Analyzing tool chaining patterns

### Database Queries

Interaction history and tool usage can be queried via the `interactions` table. See `docs/reference/database.md` for query examples.

---

## Best Practices

### Tool Selection

- Always start with triage for health-related queries
- Review original user request after each tool call
- Chain tools when results indicate additional actions needed
- Ask for consent before scheduling appointments

### Error Handling

- Tools should handle missing/invalid inputs gracefully
- Agent should request clarification when information is insufficient
- Tool failures should be logged and communicated to user

### User Experience

- Provide clear, empathetic responses
- Summarize tool results in user-friendly language
- Verify all requested actions completed before ending
- Prioritize safety (emergency instructions first)

### Development

- Test tool chaining patterns thoroughly
- Monitor tool usage patterns for optimization
- Experiment with system prompt variations
- Track interaction storage for analytics

