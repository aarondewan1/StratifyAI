# README.md

# Highlights

- **Specialised React-Style Agents** — A Quant, a Qualitative Analyst, a CIO, and a Risk Agent, each with clear domain logic.
- **Shared State** — Robust context passing via a single shared state object.
- **Parallel + Sequential Flows** — Quant & Analyst run in parallel (fan-in), feeding the CIO, who then hands off to Risk.
- **Agent-to-Agent Cross-Checks** — The CIO Agent can dynamically query the Quant and Analyst, ensuring alignment before committing.
- **Deterministic + Dynamic Tools** — Some tools run automatically before LLM calls (e.g., macro tickers); others are called on-demand by agents.
- **Real-Time External APIs** — Yahoo Finance + Google Search exposed as tools for live data pulls and fact-checks.
- **HiTL Conditional Edges** — Risk Agent conditionally routes to Execution or Human-in-the-Loop Node based on final risk status.
- **Fully Auditable** — Every run logs agent steps, tool calls, final reports, HiTL overrides, and key state changes.
- **Typed Validation** — Pydantic report types enforce consistent, structured agent outputs.

---

# Installation

1. Download & unzip the repo.
2. Set up your Python env:
    
    ```bash
    cd agents-fund
    python3 -m venv env
    pip3 install -r requirements.txt
    source env/bin/activate
    ```
    
3. Run:
    
    ```bash
    python3 -m app.main
    ```
    

Runs a simulation with the provided `market_data.json`. Logs land in `logs/`.

> ⚠️ Note: .env is included for your convenience, only because these keys will expire soon anyway. API keys have a $5 cap!

> Note: While installing, you can also choose to look in the logs/ directory, for an older run (with example logs).

# Config

- `.env` → `DEBUG=True | False` toggles verbose LangGraph logs to the console.

# Design Decisions & Strategies

- **LLM:** GPT-4o — fast, great with context, solid for multi-agent loops.
- **Framework:** LangGraph/LangChain for workflow orchestration.
- **Tools:** Deterministic vs. dynamic usage depending on agent role.

# Agents Overview

> `We have 4 agents, and a human-in-the loop node. The agents each have specific roles, mimicking those in a real organisation.`
> 

## Analyst Agent

- Qualitative sentiment analysis of market headlines.
- **Dynamic**: Chooses tickers to verify via **Google Search** + **Yahoo Finance**.
- Produces a structured Analyst Report with a clear equity/bond split.

## Quant Agent

- Macro signals via CPI, unemployment, and inflation.
- **Deterministic**: Always fetches SPY and ^IRX via **Yahoo Finance**.
- Misery Index computed automatically.
- Outputs a structured Quant Report with numeric justification.

## CIO Agent

- Cross-checks Analyst & Quant Reports.
- Can **question** either agent if needed — fully reactive.
- Consolidates into a final CIO Report.

## Risk Agent

- Reviews CIO decision for hallucinations or flawed logic.
- Issues a Risk Report: `ALLOW`, `WARN`, or `BLOCK`, with justification.
- Dynamically calls the Google Search tool, to independently verify any justifications in previous Reports.
- **Conditional routing**: sends to Execution or Human-in-the-Loop Node.

## Human Approval Node

- Triggered on `WARN` or `BLOCK` risk outcomes.
- Skipped if Risk Report is `ALLOW`.

## Execution Node

- “Executes” the new portfolio split (stub node)

# Tools

### Yahoo Finance

- Historical ticker data by month.
- Used deterministically (Quant) and dynamically (Analyst).
- Provides clean LLM-friendly stats.

### Google Search

- Live fact-check or news verification.
- Used dynamically by Analyst Agent, and Risk Agent.

# List of Todos

> `A list of the todo’s I planned and then implemented, in order, for transparency of my approach and priorities in this task.`
> 

- [ ]  create 4 ReACT agents: Analyst (qualitative), Quant, CIO (i.e. executive decision maker), Risk
- [ ]  connect graph structure (linear, with connected nodes)
- [ ]  create a structured report for each agent
    - [ ]  each agent’s decision {equities, bonds, justification} is stored in structured Report
- [ ]  prompt engineer the agents
- [ ]  add centralised state
- [ ]  add google search tool to Analyst (searches for any additional info)
- [ ]  add Yahoo Finance tool to Analyst dynamically (the analyst selects which
- [ ]  give CIO tools to question/chat with Analyst and Quant agent
- [ ]  add a human approval node (for HITL)
- [ ]  create simulation running loop for the month
- [ ]  parallelism of quant and analyst agent
- [ ]  add logging
    - [ ]  agent invocations
    - [ ]  tool calls
    - [ ]  state updates at the start and the end of each run
- [ ]  create a rules based interest rate extractor node
- [ ]  add conditional logic between the Risk Agent, the Human Approval Node and the Execution Node
- [ ]  add starting capital to simulation (as requested)

### Left Undone

> Tasks I did not complete.
> 

- [ ]  integrate the interest rate extractor node into the workflow
- [ ]  add a failsafe wrapper for the tools, as a decorator function that blanket catches exceptions