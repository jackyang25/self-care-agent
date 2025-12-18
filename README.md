# Self-Care Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0--alpha-orange.svg)](https://github.com/yourusername/self-care-agent)
[![Status](https://img.shields.io/badge/status-proof--of--concept-blue.svg)](https://github.com/yourusername/self-care-agent)

## What This Is

AI-powered self-care navigation system for low and middle income countries. Demonstrates:
- Multi-step agent reasoning with tool orchestration
- Verified triage via formal logic (primitive POC)
- RAG-grounded clinical guidance with citations
- Multi-channel support (Streamlit, WhatsApp)
- Database-backed user context and audit trails

**Current state:** Core workflows function with mock data for external integrations (EHR, pharmacy, scheduling APIs). Architecture and integration patterns are designed for production.

## Self-Care Agent Framework (SCAF)

The long-term vision is a **standardized framework**: a set of APIs, digital self-care protocols, and safety governance layers that certified AI systems can invoke to deliver evidence-based self-care, triage, and referral services across LMIC health systems.

> *Note*: This is research and development prototype with mock data, sample guidelines, and primitive triage verifier. 

## Why This Matters

### The Problem
In low- and middle-income countries, people face significant barriers to healthcare:
- **Stigma** prevents individuals from seeking care for sensitive health concerns (HIV, TB, sexual health, mental health)
- **Cost and access** issues lead to delayed care or unnecessary clinic visits
- **Fragmented systems** mean patient context is lost across pharmacies, labs, and clinics
- **Language and literacy barriers** exclude rural and underserved communities

### The Idea
- **Stigma-free navigation and triage:** Individuals privately ask sensitive questions via voice or text on any channel, receiving validated guidance in plain, non-judgmental language.
- **Right-siting of care:** AI safely triages cases, guiding low-risk conditions to self-care while escalating urgent cases to providers, reducing costs and unnecessary visits.
- **Continuity across channels:** With user consent, a longitudinal record maintains context between pharmacies, labs, telemedicine, and clinics to improve adherence and follow-up.
- **Seamless access to services:** One interaction can order self-tests, book labs, schedule teleconsults, or arrange pharmacy pickup/delivery.
- **Equity at scale:** Works in any language, supports low-literacy users via audio/voice, runs on WhatsApp/SMS and basic mobile networks.
- **Governed safety:** Every interaction runs through certified Self-Care Protocol APIs with continuous monitoring, ensuring evidence-based, traceable, compliant advice.


## What This Demonstrates

Validates the **technical feasibility** of core architecture patterns.

### Implemented & Working

#### 1. Agent Metacognition via Dynamic Graph
- **LangGraph-based agent** with conditional routing and multi-step reasoning
- **Dynamic tool chaining**: Agent autonomously decides which tools to call and in what order based on user needs
- **Stateful conversations**: Maintains context across multi-turn interactions
- **Prompting strategies**: Context-aware system prompts with patient demographics, timezone, and current time

*Details: [docs/architecture/agent.md](docs/architecture/agent.md)*

#### 2. Dynamic Tool Calling
- **StructuredTool definitions** with Pydantic input schemas for type-safe tool invocation
- **Native tool binding** via LangChain for seamless LLM-to-tool communication
- **Tool chaining patterns**: Triage → Referral → Database queries automatically orchestrated
- **Intelligent routing**: Heart symptoms → cardiologist, pregnancy → obstetrics (prompt-based, not hardcoded rules)

*Details: [docs/reference/tools.md](docs/reference/tools.md)*

#### 3. Verified Triage via Formal Logic (Primitive POC)
- **Simplified WHO iITT protocol** implementation using compiled Lean formal logic (basic ruleset, not comprehensive)
- **Binary executable triage** demonstrates concept of verified logic (no LLM hallucination risk for acuity assessment)
- **Red/yellow/green classification** with basic rule-based recommendations
- **Vitals collection** through structured questioning before triage execution

> **Note:** Early-stage POC with limited protocol coverage. Production requires comprehensive clinical logic.

*Details: [docs/architecture/triage-verification.md](docs/architecture/triage-verification.md)*

#### 4. RAG with Clinical Grounding
- **Semantic search** over clinical guidelines using pgvector
- **Source attribution**: Every RAG response includes document citations
- **Mock guideline grounding**: Demonstrates integration pattern for real WHO/national guidelines 

*Details: [docs/architecture/rag.md](docs/architecture/rag.md)*

#### 5. Multi-Channel Support
- **Streamlit UI**: Web-based chat interface with visual source display
- **WhatsApp webhook**: Full integration with message handling and user lookup
- **Mock phone login**: E.164 phone number-based user identification
- **Channel abstraction**: Unified agent accessible via any channel with consistent behavior

*Details: [docs/guides/whatsapp.md](docs/guides/whatsapp.md)*

#### 6. Database & Memory Layer
- **PostgreSQL** with user profiles, interaction history, consents, providers, and appointments
- **User context**: Demographics (age, gender), timezone, country for localized routing
- **Audit trail**: Full interaction logging with tool calls, triage results, and risk levels
- **Provider matching**: Database-backed provider routing by specialty and location

*Details: [docs/reference/database.md](docs/reference/database.md)*

### Mocked (Architectural Slots for Production)

> **Note:** These components use **mock data** but have **real schemas and integration patterns** ready for production APIs.

**Provider availability**
- Current: Static seed data
- Production: Integrate with EHR scheduling APIs (Epic, Cerner, OpenMRS) via FHIR

**Appointment times**
- Current: User-specified or defaults
- Production: Real-time calendar availability queries

**Commodity fulfillment**
- Current: Mock order IDs
- Production: Integration with pharmacy/logistics systems (ShopRite, Dis-Chem)

**Clinical guidelines**
- Current: Sample RAG documents
- Production: Load validated WHO/national self-care protocols
- Example Reference: [South Africa APC 2023 Clinical Tool](https://knowledgehub.health.gov.za/system/files/elibdownloads/2023-10/APC_2023_Clinical_tool-EBOOK.pdf) for real-world clinical schemas

**External scheduling**
- Current: Database-only
- Production: Dual-write to local DB + external scheduling system

**Key Insight:** The tool interfaces, database schemas, and data flows are **production-ready**. Integration simply swaps mock data sources for real APIs.

## How This Differs From Generic LLMs


- **Verified triage via formal logic (Lean)** - primitive POC showing triage can be provably correct, not hallucinated
- **Cited sources for all clinical guidance** - RAG with document attribution instead of black-box responses
- **LMIC-contextualized** - user demographics (age, gender, timezone, country) inform every interaction
- **Multi-step tool chaining** - autonomous orchestration (triage → consent → schedule) instead of one-shot responses
- **Structured clinical grounding** - RAG over protocols (currently sample data) instead of pure LLM knowledge
- **Multi-channel architecture** - WhatsApp, Streamlit working; SMS/IVR patterns defined
- **Full interaction logging** - every tool call and triage decision auditable for safety monitoring
- **Self-care positioning** - deliberately avoids diagnostic language, focuses on navigation

> **Key Takeaway:** The "last 20%" of clinical correctness comes from grounding every response in validated protocols via RAG (and knowledge graphs, if feasible), verified triage logic, and governed safety layers rather than relying solely on LLM knowledge.

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (required)
- [OpenAI API Key](https://platform.openai.com/api-keys) (required)
- [VS Code](https://code.visualstudio.com/) (recommended)

### Installation

   ```bash
make setup  # First-time setup (starts containers, creates tables, seeds data)
# Open http://localhost:8501
# Login with: jack.yang@gatesfoundation.org
```

> **Note:** All services run in Docker containers. No local Python or PostgreSQL setup required. Just be sure to have an IDE! :)

<details>
<summary><b>Optional: LangSmith Integration for Observability</b></summary>

To trace LLM calls, monitor costs, and audit agent behavior:

1. Create free account at [LangSmith](https://smith.langchain.com/)
2. Add to `.env`:
   ```bash
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key
   LANGCHAIN_PROJECT=scaf-poc
   ```
3. Restart: `make change`
4. View traces at https://smith.langchain.com/

See every tool call, token usage, and conversation flow in real-time.

</details>

For detailed installation instructions, environment configuration, troubleshooting, and development workflows, see **[SETUP.md](SETUP.md)**.

## Technical Architecture

<details>
<summary><b>High-Level Flow</b></summary>

**Full System Architecture:** [View detailed diagram](https://bmgf-my.sharepoint.com/:u:/r/personal/jack_yang_gatesfoundation_org/_layouts/15/Doc.aspx?sourcedoc=%7B603ad649-8ba7-4558-855a-3f05b268c58a%7D&action=edit)

**Simplified Flow:**

```
User Input (Streamlit/WhatsApp)
           ↓
   Agent (GPT-4 + LangGraph)
           ↓
   Dynamic Tool Selection
           ↓
┌─────────────┬──────────────┬───────────────┬──────────────┬─────────┐
│   Triage    │  Scheduling  │   Database    │     RAG      │  Other  │
│ (Lean POC)  │  (Providers  │ (PostgreSQL)  │ (pgvector)   │ (Mocked)│
│             │   + Appts)   │               │              │         │
└─────────────┴──────────────┴───────────────┴──────────────┴─────────┘
           ↓
 Interaction Storage & Audit Trail
         (PostgreSQL)
           ↓
   Response with Citations
```

> **Note:** "Other" includes commodity orders and pharmacy tools (mock APIs demonstrating integration patterns).

</details>

### Key Components

- **Agent Layer**: LangGraph orchestration with GPT-4, conditional routing, multi-turn state
- **Tool Layer**: Modular, type-safe tools with structured I/O (triage, scheduling, RAG, database)
- **Verification Layer**: Lean-compiled triage binary for formal correctness
- **Memory Layer**: PostgreSQL with user profiles, interaction history, providers, appointments
- **Channel Layer**: Abstracted handlers for Streamlit, WhatsApp, future SMS/IVR

## Project Structure

<details>
<summary><b>Expand to view full directory structure</b></summary>

```
.
├── src/
│   ├── agent.py                    # LangGraph agent with tool calling
│   ├── config.py                   # Application configuration
│   ├── database.py                 # Database connection utilities
│   ├── channels/                   # Multi-channel support
│   │   ├── base.py                # Channel abstraction
│   │   ├── streamlit.py           # Web UI handler
│   │   └── whatsapp.py            # WhatsApp webhook handler
│   ├── tools/                      # Tool implementations
│   │   ├── triage.py              # Verified triage with Lean
│   │   ├── referrals.py           # Appointment scheduling
│   │   ├── rag.py                 # RAG with citations
│   │   ├── database.py            # User data queries
│   │   ├── commodity.py           # Commodity orders (mock)
│   │   └── pharmacy.py            # Pharmacy orders (mock)
│   └── utils/                     # Shared utilities
│       ├── context.py             # Thread-safe context variables
│       ├── interactions.py        # Interaction logging
│       ├── logger.py              # Logging configuration
│       └── user_lookup.py         # User identification
├── docs/                           # Technical documentation
│   ├── architecture/              # System design & concepts
│   │   ├── agent.md               # LangGraph agent architecture
│   │   ├── rag.md                 # RAG with pgvector
│   │   └── triage-verification.md # Verified triage with Lean
│   ├── reference/                 # Technical specifications
│   │   ├── database.md            # Database schema
│   │   ├── seeds.md               # Seed data structure
│   │   └── tools.md               # Tool documentation
│   └── guides/                    # How-to & integration
│       ├── testing.md             # Testing guide
│       └── whatsapp.md            # WhatsApp integration
├── bin/
│   └── triage-verifier            # Lean-compiled triage binary
├── seeds/
│   └── demo.json                  # All demo data (users, providers, appointments, RAG documents)
├── scripts/                        # Database management
│   ├── db/
│   │   ├── create_tables.py       # Create all tables (app + RAG)
│   │   ├── seed.py                # Seed all data (app + RAG)
│   │   └── test.py                # Test database connection
│   ├── dev/
│   │   └── start_ngrok.sh
│   └── tools/
│       └── test_verified_triage.py
├── streamlit_server.py             # Streamlit UI entry point
├── webhook_server.py               # WhatsApp webhook entry point
├── docker-compose.yml              # Multi-container orchestration
├── Dockerfile                      # Application container
├── Makefile                        # Development commands
├── requirements.txt                # Python dependencies
├── README.md                       # Project overview (this file)
├── SETUP.md                        # Installation & configuration
└── AGENTS.md                       # AI coding assistant instructions
```

</details>

## What's Next

### Near-Term (Production MVP)
- [ ] Integrate real EHR scheduling APIs (Epic/Cerner/OpenMRS via FHIR)
- [ ] Load validated WHO self-care protocols into RAG system
- [ ] Connect pharmacy/logistics APIs (ShopRite, Dis-Chem, or public-sector equivalents)
- [ ] Add SMS and IVR channels for low-data/low-literacy access
- [ ] Multi-language support (Swahili, Zulu, French, Portuguese)
- [ ] LangSmith integration for LLM tracing, cost analysis, and auditability
- [ ] Expand verified triage logic to ground truths (WHO guidelines)
- [ ] Safety monitoring dashboard for red-flag interactions

### Medium-Term (Scale & Governance)
- [ ] National guideline adapters for South Africa ([APC Clinical Tool](https://knowledgehub.health.gov.za/system/files/elibdownloads/2023-10/APC_2023_Clinical_tool-EBOOK.pdf)), Senegal, Malawi
- [ ] Continuous safety monitoring and audit reporting
- [ ] Integration with national health information systems
- [ ] Community health worker interface for assisted interactions
- [ ] Offline-first mobile app for low-connectivity areas
- [ ] Data residency and compliance infrastructure per jurisdiction

### Long-Term (Ecosystem)
- [ ] Certification framework for third-party AI systems
- [ ] Open API standard for self-care protocol invocation
- [ ] Multi-country deployment with localized protocols
- [ ] Integration with insurance/payment systems
- [ ] Knowledge graph for symptom → protocol → commodity routing
- [ ] Standardized SCAF platform for certified AI systems (global data MCPs?)

## Architecture Decisions

<details>
<summary><b>Why Single Agent (Not Multi-Agent)?</b></summary>

The framework uses **one agent** that orchestrates all tools rather than multiple specialized agents. This choice prioritizes:
- **Simplicity**: Easier to debug, maintain, and reason about
- **Flexibility**: Agent can dynamically chain any tool combination
- **Consistency**: Unified decision-making across all interactions
- **Tool specialization**: Complex logic lives in tools (verified triage, RAG), not agent orchestration

> **Note:** For future HIV/TB/mental health verticals, specialized logic will be added as **new tools**, not new agents, maintaining architectural simplicity.

</details>

<details>
<summary><b>Why PostgreSQL (Not Document Store)?</b></summary>

Relational database chosen for:
- **ACID compliance** for clinical data integrity
- **Structured audit trails** with foreign key relationships
- **SQL expressiveness** for complex queries (user history, provider matching)
- **pgvector extension** enables semantic search without separate vector DB

</details>

<details>
<summary><b>Why Mock Data (Not Real Integrations)?</b></summary>

POC focuses on **proving the architecture works** before tackling integration complexity. Mock data demonstrates:
- Correct data flows and schemas
- Tool chaining patterns
- Integration points (architectural slots)

> **Note:** Production swaps mock data sources for real APIs **without changing tool interfaces**.

</details>

## Data Privacy & Compliance

<details>
<summary><b>Regulatory Considerations for Production Deployment</b></summary>

**This POC demonstrates technical capabilities. Production deployment requires compliance with applicable data protection and healthcare regulations.**

### Healthcare Data Regulations

**Target Country Requirements:**
- **South Africa**: POPIA (Protection of Personal Information Act), National Health Act
- **Senegal**: Loi n°2008-12 sur la Protection des Données à Caractère Personnel
- **Malawi**: Data Protection Act 2023, National Health Act
- **General**: GDPR for EU data subjects, local healthcare information privacy laws

**Key Compliance Areas:**
- Patient consent management (implemented: `consents` table with version tracking)
- Data minimization and purpose limitation
- Right to access and erasure (architectural slots for user data export/deletion)
- Healthcare provider licensing and supervision requirements
- Cross-border data transfer restrictions

### Data Localization

Many LMIC countries require health data to be stored within national borders:
- Database deployment must respect data residency requirements
- Cloud region selection (e.g., AWS Cape Town, Azure South Africa)
- Encryption in transit and at rest (TLS 1.3, AES-256)

### Audit & Accountability

**Already implemented:**
- Full interaction logging (`interactions` table with timestamps)
- Tool call tracking for reproducibility
- User consent records with evidence trail
- Timezone-aware timestamps for legal compliance

**Production additions needed:**
- Automated compliance reporting
- Data retention policies (configurable retention periods)
- Breach notification workflows
- Regular security audits and penetration testing

### AI-Specific Regulations

**Emerging Requirements:**
- EU AI Act: High-risk system classification for healthcare AI
- Algorithmic accountability and explainability
- Model versioning and audit trails (LangSmith integration recommended)
- Human oversight requirements for clinical decisions

### Recommended Practices

1. **Conduct legal review** for each target country before deployment
2. **Implement data protection impact assessments** (DPIA) per jurisdiction
3. **Obtain appropriate licenses** for telemedicine/health information services
4. **Establish data processing agreements** with cloud providers
5. **Deploy within country-specific regulatory sandboxes** where available
6. **Partner with local health authorities** for compliance guidance

> **Note:** This provides technical infrastructure. Legal compliance requires jurisdiction-specific implementation with qualified legal counsel.

</details>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2024 Bill & Melinda Gates Foundation


## Contact

jack.yang@gatesfoundation.org
