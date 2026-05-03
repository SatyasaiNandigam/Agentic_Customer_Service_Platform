# ShopEasy — Agentic AI Customer Service Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.136+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/LangGraph-Stateful%20Agent-FF6B35?style=for-the-badge" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/OpenAI-gpt--4o--mini-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Redis-7%20%28Cache%20%2F%20Rate%20Limit%29-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis"/>
  <img src="https://img.shields.io/badge/FastMCP-2.0%20SSE-00B4AB?style=for-the-badge" alt="FastMCP"/>
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
  <img src="https://img.shields.io/badge/Status-Active%20Development-22C55E?style=for-the-badge" alt="Status"/>
</p>

<p align="center">
  A production-ready agentic customer service platform built on a deterministic LangGraph DAG — with hierarchical intent classification, a custom FastMCP tool server, LangGraph Checkpointer-backed session state, multi-modal API (REST / SSE / WebSocket), role-based access control, and defense-in-depth input/output guardrails.
</p>

> **Disclaimer:** This project is a reference implementation built for learning and demonstration purposes. "ShopEasy" is a fictional brand. All customer records, orders, products, reviews, and API responses are entirely **synthetic and auto-generated** — they do not represent any real business, individual, or organization. No proprietary data or third-party APIs are used.

---

## Project Status

This is an **actively running project**. The core agent pipeline is fully operational end-to-end. Ongoing work is focused on:

- **Node quality improvements** — refining classifier few-shot prompts, tightening guardrail thresholds, and improving response grounding accuracy
- **New capabilities** — expanding the MCP tool surface, adding new intent classes, and enhancing the long-term memory summarization pipeline
- **Evaluation framework** — building automated eval harnesses to measure intent accuracy, tool selection precision, and guardrail recall across regression suites

Expect frequent iteration on `app/agent/prompts/`, `app/guardrails/`, and `tools_mcp/tools/` as the system matures.

---

## Highlights

| Capability | Details |
|---|---|
| **Agentic Orchestration** | LangGraph state machine with 8 nodes, hierarchical classification, conditional routing, retry budgets, and hard conversation limits |
| **Hierarchical Classification** | Two-stage intent pipeline: `customer_delegator` (domain) → `classifier` (intent), reducing misclassification before tool dispatch |
| **Custom MCP Tool Server** | FastMCP 2.0 SSE server exposing 10 typed ecommerce tools with RBAC-enforced access |
| **Persistent Checkpointing** | LangGraph `AsyncPostgresSaver` — full session history and state checkpoint recovery via PostgreSQL |
| **Cross-Session Memory** | Every ~10 messages, session is compressed into a cumulative PostgreSQL summary and injected on the next session |
| **Guardrails Pipeline** | Input/output safety checks: PII detection, prompt injection blocking, hallucination grounding — regex-first with LLM fallback |
| **Multi-Modal API** | REST, Server-Sent Events (SSE), and WebSocket endpoints in a single FastAPI service |
| **Production-Ready Auth** | JWT-based authentication with HS256, role-based access control (customer / support_agent / admin) |
| **Structured Observability** | `structlog` JSON logging + optional LangSmith tracing integration |

---

## Architecture

<p align="center">
  <img src="assets/architecture_v1.png" alt="ShopEasy Architecture Diagram" width="900"/>
</p>

---

## Request Lifecycle

```
User Message
  └─► guardrails_in      ──  PII redaction, injection detection (regex → Haiku fallback),
  │                           rate limit (20 msg/min/user)
  │
  └─► customer_delegator ──  Hierarchical domain classification (gpt-4o-mini)
  │      │                    need_information · need_assistance · need_advice
  │      └─► [escalate / block] → human_handoff ──────────────────────────┐
  │                                                                        │
  └─► classifier         ──  13-class intent detection, confidence check  │
         ├─► [direct]   ──────────────────────────────────────────────┐   │
         ├─► [tool]     → tool_planner → tool_executor (SSE → MCP)   │   │
         │                      └─► [retry ≤ 2]  ───────────────────  │   │
         └─► [complaint] → human_handoff ──────────────────────────── │ ──┘
                                                                       ▼
                                                              memory (summarizer)
                                                                       │
                                                             response_generator
                                                                       │
                                                             guardrails_out  ──  PII leak, grounding check
                                                                  └─► [rewrite ≤ 2]
                                                                       │
                                                               HTTP / SSE / WS
```

---

## Features

### Agentic Intelligence
- **Hierarchical classification** — `customer_delegator` first assigns a broad domain (`need_information`, `need_assistance`, `need_advice`, `escalate`, `block`), then `classifier` resolves the precise intent within that domain — reducing misrouting before any tool is selected
- **13-class intent classifier** — `order_status`, `order_cancel`, `shipment_tracking`, `refund_request`, `refund_status`, `product_inquiry`, `product_search`, `account_info`, `review_lookup`, `chitchat`, `faq_policy`, `complaint`, `unknown`
- **Structured LLM outputs** — Pydantic-validated responses prevent hallucinated tool calls
- **Retry budgets** — Up to 2 tool retries and 2 output rewrites per turn before fail-safe response
- **Hard turn limit** — 5-turn ceiling prevents runaway loops
- **Complaint escalation** — Automatic routing to human handoff at both the delegator and classifier layers

### Custom MCP Tool Server
- **10 typed tools** — 8 read-only, 2 write (confirmation flag required)
- **RBAC enforcement** — Tool schemas are role-keyed; user identity is injected via verified headers, never via LLM
- **Cache-aside strategy** — Redis caches tool results with domain-aware TTLs (5 min → 6 hr)
- **Write limits** — Destructive: 1/turn · Write: 3/turn · Read: 10/turn

### Guardrails (Defense in Depth)
- **Input guard** — Message length cap (4 000 chars), rate limiting, hard injection patterns (jailbreak, SQL, template injection), soft patterns with Haiku LLM fallback above confidence threshold
- **Output guard** — PII leak detection (credit cards, SSNs, API keys), internal field patterns, system leak patterns, grounding verification against tool results
- **Cheap-first architecture** — Fast regex runs first; LLM fallback invoked only when pattern confidence is below threshold

### Memory System
- **Session state (LangGraph Checkpointer)** — `AsyncPostgresSaver` persists the full conversation state (all messages, tool results, guardrail flags) to PostgreSQL after every graph turn. On reconnect, the checkpoint is loaded automatically — no explicit session reconstruction needed
- **Cross-session context (PostgreSQL)** — After every ~10 messages the in-graph summarizer compresses the current history into a cumulative `ConversationSummary`. On the next session the last 5 summaries are retrieved and injected into the system prompt, giving the LLM continuity across sessions without token bloat
- **Redis** — Used exclusively for rate-limit sliding windows and MCP tool-result caching

### API Surface
| Endpoint | Protocol | Description |
|---|---|---|
| `POST /api/v1/chat` | HTTP | Synchronous single-turn request/response |
| `POST /api/v1/chat/stream` | SSE | Token-by-token streaming response |
| `WS /api/v1/chat/ws` | WebSocket | Stateful multi-turn session with live tool events |
| `GET /api/v1/chat/history/{id}` | HTTP | Retrieve session message history |
| `GET /api/v1/chat/sessions` | HTTP | List all sessions for authenticated user |
| `POST /api/v1/auth/login` | HTTP | Obtain JWT access + refresh tokens |
| `POST /api/v1/auth/refresh` | HTTP | Rotate access token using refresh token |
| `POST /api/v1/feedback` | HTTP | Submit satisfaction rating |
| `GET /health` | HTTP | Liveness probe |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Agent Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) 1.1.9 |
| **LLM** | OpenAI `gpt-4o-mini` (classification + response generation) |
| **Tool Protocol** | [FastMCP](https://github.com/jlowin/fastmcp) 2.0 over SSE |
| **API Framework** | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn (ASGI) |
| **Cache / Rate Limit** | Redis 7 (async, connection pool — tool cache + rate limiting) |
| **Persistent Store** | PostgreSQL 16 + SQLAlchemy 2.0 (async / psycopg3) |
| **Checkpointing** | `langgraph-checkpoint-postgres` + psycopg connection pool |
| **Authentication** | JWT HS256 (`python-jose`) |
| **Validation** | Pydantic v2 + Pydantic Settings |
| **Logging** | `structlog` (JSON in production, colorized in dev) |
| **Observability** | LangSmith tracing (optional) |
| **Package Manager** | [uv](https://github.com/astral-sh/uv) |
| **Containerization** | Docker Compose (multi-stage build) |
| **Language** | Python 3.12, async/await throughout |

---

## Project Structure

```
.
├── app/                          # FastAPI + LangGraph agent service
│   ├── main.py                   # App factory, lifespan (DB/Redis/MCP warmup)
│   ├── config.py                 # Pydantic Settings — all runtime config
│   ├── agent/
│   │   ├── graph.py              # StateGraph: nodes, edges, compilation
│   │   ├── state.py              # AgentState TypedDict (21 fields)
│   │   ├── edges.py              # 4 routing functions, retry budgets
│   │   ├── nodes/                # 8 async node implementations (+ 1 stub)
│   │   │   ├── customer_delegator.py  # Hierarchical domain classifier (runs before classifier)
│   │   │   ├── classifier.py
│   │   │   ├── tool_planner.py
│   │   │   ├── tool_executor.py
│   │   │   └── response_generator.py
│   │   └── prompts/              # System prompt + classifier few-shots
│   ├── api/v1/                   # Endpoints: chat, auth, feedback, health
│   ├── auth/                     # JWT service, middleware, RBAC
│   ├── guardrails/               # input_guard, output_guard, PII patterns, rate limiter
│   ├── memory/                   # long_term (PostgreSQL), summarizer (LangGraph state)
│   ├── mcp_client/               # SSE client factory, role-keyed tool registry
│   ├── cache/                    # Redis utilities, cache-aside strategy
│   └── db/                       # SQLAlchemy async engine + session factory
│
├── tools_mcp/                    # FastMCP tool server (separate process)
│   ├── server.py                 # FastMCP entry point, tool registration
│   ├── auth.py                   # Header-based user context extraction
│   ├── db/
│   │   ├── models.py             # ORM (24 tables: users, orders, products, ...)
│   │   └── queries/              # Parameterized queries per domain
│   └── tools/                    # 10 tool implementations
│       ├── order_lookup.py
│       ├── order_cancel.py       # WRITE — requires confirmation
│       ├── shipment_tracking.py
│       ├── product_search.py
│       ├── product_detail.py
│       ├── refund_status.py
│       ├── refund_initiate.py    # WRITE — requires confirmation
│       ├── review_lookup.py
│       └── account_info.py
│
├── dumps/                        # SQL seed files (Docker auto-init)
│   ├── 00_roles.sql
│   ├── ecommerce_dump.sql        # 100+ synthetic records — fictional data only, not affiliated with any real entity
│   └── z_agent_tables.sql
│
├── Dockerfile                    # Multi-stage build (builder -> runtime)
├── docker-compose.yml            # 4 services: postgres, redis, mcp-tools, agent
└── pyproject.toml                # uv-managed dependencies
```

---

## Quick Start

### Option 1 — Docker (Recommended)

```bash
# 1. Clone and set up environment
git clone <repo-url>
cd sample
cp .env.example .env          # Fill in OPENAI_API_KEY and secrets

# 2. Start all services (PostgreSQL, Redis, MCP server, Agent API)
docker compose up --build

# Agent API:   http://localhost:8000
# MCP Server:  http://localhost:8001
# Swagger UI:  http://localhost:8000/docs  (development only)
```

The database is seeded automatically on first startup from `./dumps/`.

### Option 2 — Local Development

**Prerequisites:** Python 3.12, [uv](https://github.com/astral-sh/uv), PostgreSQL 16, Redis 7

```bash
# 1. Install dependencies
uv sync --frozen

# 2. Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL, REDIS_URL, OPENAI_API_KEY

# 3. Seed the database
psql -U dev_user -d ecommerce -f dumps/00_roles.sql
psql -U dev_user -d ecommerce -f dumps/ecommerce_dump.sql
psql -U dev_user -d ecommerce -f dumps/z_agent_tables.sql

# 4. Terminal 1 — MCP tool server
python -m tools_mcp.server

# 5. Terminal 2 — FastAPI agent
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Configuration

All configuration is managed by Pydantic Settings in `app/config.py` and read from environment variables / `.env`.

### Required

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key for classifier and response generation |
| `DATABASE_URL` | PostgreSQL DSN (`postgresql+psycopg://user:pass@host:5432/db`) |
| `REDIS_URL` | Redis DSN (`redis://host:6379/0`) |
| `JWT_SECRET_KEY` | HS256 signing secret — **must be overridden in production** |

### Key Optional Variables

| Variable | Default | Notes |
|---|---|---|
| `ENVIRONMENT` | `development` | `production` disables reload, SQL echo, Swagger |
| `MCP_TOOLS_URL` | `http://localhost:8001/sse` | `http://mcp-tools:8001/sse` in Docker |
| `classifier_model` | `gpt-4o-mini` | Intent classification + delegator model |
| `openai_model` | `gpt-4o-mini` | Response generation model |
| `LANGCHAIN_TRACING_V2` | `false` | Set `true` + `LANGCHAIN_API_KEY` for LangSmith |
| `RATE_LIMIT_MESSAGES_PER_MINUTE` | `20` | Per-user message rate limit (Redis sliding window) |
| `AGENT_MAX_TURNS` | `5` | Hard conversation turn ceiling |
| `CHECKPOINT_POOL_MIN_SIZE` | `1` | LangGraph PostgreSQL checkpointer min pool size |
| `CHECKPOINT_POOL_MAX_SIZE` | `5` | LangGraph PostgreSQL checkpointer max pool size |

Full variable reference: [`app/config.py`](app/config.py)

---

## API Usage

### Authenticate

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "customer@example.com", "password": "password123"}'
```

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Send a Message (Sync)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Where is my order #ORD-1234?"}'
```

```json
{
  "message": "Your order #ORD-1234 is currently in transit...",
  "session_id": "550e8400-e29b-41d4-a716",
  "intent": "order_status",
  "run_id": "..."
}
```

### Stream a Response (SSE)

```bash
curl -N -X POST http://localhost:8000/api/v1/chat/stream \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me laptops under $800", "session_id": "550e8400-..."}'
```

### WebSocket Session

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/chat/ws");

ws.onopen = () => {
  ws.send(JSON.stringify({ message: "What is your return policy?" }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // { type: "token",      content: "..." }
  // { type: "tool_start", tool: "search_products" }
  // { type: "tool_end",   tool: "search_products" }
  // { type: "done",       message: "...", intent: "faq_policy" }
};
```

---

## Intent Classification

| Intent | Routing | Tool |
|---|---|---|
| `order_status` | tool_planner | `get_orders`, `get_order_detail` |
| `order_cancel` | tool_planner | `cancel_order` ✎ |
| `shipment_tracking` | tool_planner | `get_shipment_tracking` |
| `refund_request` | tool_planner | `initiate_refund` ✎ |
| `refund_status` | tool_planner | `get_refund_status` |
| `product_inquiry` | tool_planner | `get_product_detail` |
| `product_search` | tool_planner | `search_products` |
| `account_info` | tool_planner | `get_account_info` |
| `review_lookup` | tool_planner | `search_reviews` |
| `faq_policy` | response_generator | — |
| `chitchat` | response_generator | — |
| `unknown` | response_generator | — |
| `complaint` | human_handoff | — |

> ✎ Write operations require a `confirmation: true` flag and are subject to per-turn limits (write: 3/turn, destructive: 1/turn).

---

## Security Model

### Authentication & Authorization
- All endpoints (except `/health` and `/auth/login`) require a valid JWT Bearer token
- Roles: `customer`, `support_agent`, `admin` — enforced at both API and MCP tool layers
- User identity (`X-User-Id`, `X-User-Role`) is injected by the framework, never sourced from LLM output

### Guardrails
- **Rate limiting** — 20 messages per minute per user (Redis sliding window in `guardrails_in`)
- **Input validation** — Hard blocks on SQL injection, template injection, jailbreak keywords; soft blocks (LLM fallback) for instruction-override attempts
- **Output validation** — Blocks PII leakage (credit cards, SSNs, API keys), internal field exposure, and LLM hallucinations that contradict tool data
- **Write operation limits** — Destructive: 1/turn · Write: 3/turn · Read: 10/turn

### Production Checklist
- [ ] Replace `JWT_SECRET_KEY` with a long random value from a secrets manager
- [ ] Set `ENVIRONMENT=production` (disables Swagger, SQL echo, reload)
- [ ] Update `CORS_ALLOWED_ORIGINS` to your production domain
- [ ] Store `OPENAI_API_KEY` in a secrets manager, not `.env`
- [ ] Remove port `8001` exposure for the MCP server (internal-only in production)
- [ ] Enable `LANGCHAIN_TRACING_V2` for production observability

---

## Memory Architecture

```
Every Turn (automatic)
     │
     ▼
LangGraph AsyncPostgresSaver ──────────── Live Session State
  • Full AgentState saved to checkpoint     messages, tool results,
    after every graph node                  guardrail flags, intent,
  • Loaded at request start                 customer_domain, summaries
  • Enables crash recovery and replay
     │
     │  Every ~10 messages (in-graph)
     ▼
Summarizer node ───────────────────────── Compression
  • Cumulative summary merges prior +       stored in AgentState as
    new messages into one coherent text     context_summary
  • Persisted via checkpointer              (never removes raw messages)
     │
     │  On session close / archival
     ▼
PostgreSQL (long-term tables) ──────────── Cross-Session Storage
  • conversations                           Session header
  • messages                                Full message log
  • conversation_summaries                  Compressed context per session
     │
     │  On next session start
     ▼
System Prompt Injection ───────────────── Context Continuity
  • Last 5 archived summaries injected      Customer sees continuity
    into LLM context                        across sessions without
                                            token bloat
```
---

## Cache Strategy

| Resource | TTL | Rationale |
|---|---|---|
| Product detail | 1 hour | Stable data |
| Product search | 15 minutes | Inventory fluctuates |
| Order status | 5 minutes | Changes frequently |
| Categories / Brands | 6 hours | Rarely changes |

---

## Development

### Logs

Structured logging is provided by `structlog`. In development the output is colorized; in production it emits JSON for log aggregators.

```bash
# Example production log line
{"event": "agent.turn.complete", "intent": "order_status", "latency_ms": 842, "session_id": "..."}
```

### LangSmith Tracing

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__...
LANGCHAIN_PROJECT=ecommerce-customer-service
```

### Adding a New Tool

1. Create `tools_mcp/tools/my_tool.py` with a `register(mcp: FastMCP)` function
2. Add a parameterized query module under `tools_mcp/db/queries/`
3. Register the module in `tools_mcp/server.py`
4. If the tool introduces a new intent, add it to `TOOL_INTENTS` in `app/agent/state.py`
5. Add few-shot examples to `app/agent/prompts/classifier.py`

### Adding a New Intent

1. Add the string literal to `IntentType` in `app/agent/state.py`
2. Classify it into `TOOL_INTENTS`, `DIRECT_RESPONSE_INTENTS`, or `ESCALATION_INTENTS`
3. Decide which delegator domain it belongs to (`need_information`, `need_assistance`, `need_advice`) and update `app/agent/prompts/customer_delegator.py` if the mapping isn't covered
4. Add few-shot examples to `app/agent/prompts/classifier.py`
5. Update the tool planner system prompt if the intent maps to a tool

---