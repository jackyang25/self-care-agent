# Self-Care Agent Prototype v0

Simple intent-based routing using LangGraph.

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
python main.py
```

Then wait for interface to launch...

## Structure

- `main.py` - Entry point
- `src/orchestrator.py` - Intent classification and routing
- `src/tools.py` - tool implementations
- `src/agent.py` - LangGraph agent
- `src/interface.py` - Gradio UI
