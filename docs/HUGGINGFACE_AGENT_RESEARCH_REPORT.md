# Hugging Face Agent Models & Implementation Research Report

**Created:** 2026-01-03
**Purpose:** Deep research for VECTRA-PLAYER RL/ML bot enhancement
**Target Infrastructure:** VPS with 2 vCPU, 7.8GB RAM, no GPU

---

## Executive Summary

### Top 3 Model Recommendations

| Rank | Model | Parameters | Why |
|------|-------|------------|-----|
| 1 | **Qwen 2.5 72B** (via API) | 72B | Best reasoning + math performance, strong tool use |
| 2 | **DeepSeek-R1-Distill-Qwen-32B** (via API) | 32B | SOTA reasoning, outperforms o1-mini, cost-efficient |
| 3 | **Phi-3-mini** (local CPU) | 3.8B | Can run on CPU, 69% MMLU, good for fast queries |

### Framework Choice: **smolagents + LangChain hybrid**

- **Primary:** smolagents for code-based agents (simpler, ~1000 lines codebase)
- **Secondary:** LangChain for orchestration when needed (langchain-huggingface integration)
- **Rationale:** smolagents is HF's official solution, actively maintained, minimal abstraction

### Key Implementation Patterns

1. **CodeAgent pattern** - Generate Python code for tool calls (more expressive than JSON)
2. **ReAct loop** - Thought → Action → Observation cycle
3. **Hybrid RL+Agent** - Agent for strategic guidance, RL for execution
4. **API-first** - Use HF Inference Providers for heavy lifting, local for simple queries

### Revised Timeline

| Phase | Original | Research-Based | Risk Level |
|-------|----------|----------------|------------|
| Phase 1: Foundation | 2 weeks | 2-3 weeks | Low |
| Phase 2: Capabilities | 3 weeks | 4-5 weeks | Medium |
| Phase 3: Training Integration | 3 weeks | 4-6 weeks | High |
| Phase 4: Hybrid Mode | 4 weeks | 6-8 weeks | High |
| **Total** | 12 weeks | 16-22 weeks | - |

---

## Task 1: Model Selection Research

### 1.1 Model Categories Evaluated

#### Reasoning Models (2025-2026 SOTA)

| Model | Size | MMLU | MATH-500 | AIME 2024 | Tool Use | API Available |
|-------|------|------|----------|-----------|----------|---------------|
| DeepSeek-R1 | 671B MoE | 90.8% | 97.3% | 79.8% | ✅ (v0528) | ✅ HF Providers |
| DeepSeek-R1-Distill-Qwen-32B | 32B | 85%+ | 94.3% | 72.6% | ✅ | ✅ HF Providers |
| Qwen 2.5 72B | 72B | 86%+ | 83.1% | - | ✅ | ✅ HF Providers |
| Qwen 3 235B | 235B | 88%+ | - | - | ✅ | ✅ HF Providers |
| Llama 3.3 70B | 70B | 82%+ | - | - | ✅ | ✅ HF Providers |
| Mistral Large | 123B | 81%+ | - | - | ✅ | ✅ HF Providers |

#### Small Efficient Models (CPU-Capable)

| Model | Size | MMLU | Latency (CPU) | Memory | Best For |
|-------|------|------|---------------|--------|----------|
| Phi-3-mini | 3.8B | 69% | 12+ tok/s (mobile) | 4-8GB | Fast queries, CPU inference |
| Qwen 2.5 7B | 7B | 74%+ | Slow without GPU | 8-16GB | Balance of quality/speed |
| Gemma 2 9B | 9B | 71%+ | Slow without GPU | 12-18GB | Multilingual |
| DeepSeek-R1-Distill-Qwen-7B | 7B | - | Slow without GPU | 8-16GB | Reasoning on budget |

#### Code Models

| Model | Size | HumanEval | Best For |
|-------|------|-----------|----------|
| Qwen 2.5-Coder 32B | 32B | 92%+ | Tool generation, code analysis |
| DeepSeek-Coder-V2 | 236B MoE | 90%+ | Complex code tasks |
| StarCoder2 15B | 15B | 46%+ | Code completion |

### 1.2 Strategic Reasoning Benchmarks

From GameBench, GTBench, and GAMEBoT research (2025):

- **GPT-5** emerged as best reasoning model in GAMEBoT evaluation
- **GPT-4** with CoT scaffolding achieves best LLM performance but still below human baseline
- **Code-pretrained models** benefit strategic reasoning significantly
- **Open-source gap:** Commercial models still lead in complex game scenarios

**Key Finding:** LLMs struggle with complete/deterministic games but are competitive in probabilistic scenarios - relevant for rugs.fun which has probabilistic elements.

### 1.3 Top 3 Recommendations (Detailed)

#### 1. Qwen 2.5 72B (via HF Inference API)
- **Why:** Top performer on Open LLM Leaderboard, exceptional multilingual + math
- **Reasoning:** 83.1% on MATH benchmarks
- **Tool Use:** Native support, works well with smolagents
- **Cost:** ~$0.0004/1K input tokens via HF Providers
- **Latency:** ~500ms-2s per request
- **Context:** 128K tokens - excellent for game history

#### 2. DeepSeek-R1-Distill-Qwen-32B (via API)
- **Why:** Outperforms o1-mini, 94.3% MATH-500, trained with RL
- **Reasoning:** Purpose-built for multi-step reasoning
- **Tool Use:** v0528 added function calling support
- **Cost:** Very competitive pricing
- **Latency:** ~1-3s per request
- **Context:** 128K tokens

#### 3. Phi-3-mini 3.8B (Local CPU)
- **Why:** Runs on CPU (12+ tok/s on mobile), 69% MMLU rivals larger models
- **Reasoning:** Good for simple strategic queries
- **Tool Use:** Limited but functional
- **Cost:** Free (local)
- **Latency:** ~50-100ms locally
- **Best For:** Fast, simple queries; fallback when API unavailable

---

## Task 2: Agent Framework Evaluation

### 2.1 Framework Comparison

| Criteria | smolagents | LangChain | Custom |
|----------|------------|-----------|--------|
| **Complexity** | ~1000 lines | Large framework | Variable |
| **Learning Curve** | Low | Medium-High | High |
| **HF Integration** | Native | Via langchain-huggingface | Manual |
| **Code Agents** | ✅ First-class | ✅ Supported | Manual |
| **Tool Creation** | @tool decorator | Tool class | Manual |
| **Multi-Agent** | ✅ Built-in | ✅ LangGraph | Manual |
| **Production Ready** | Growing | Mature | Depends |
| **Documentation** | Good (+ course) | Excellent | N/A |
| **Sandboxing** | Docker, E2B, Modal | Limited | Manual |

### 2.2 Recommended Framework: smolagents

**Rationale:**
1. Official HF library - tight model integration
2. CodeAgent generates Python (more expressive than JSON tool calls)
3. Minimal abstraction - easy to understand and debug
4. Built-in security via sandboxed execution
5. Free Agents Course for learning

**Implementation Pattern:**

```python
from smolagents import CodeAgent, HfApiModel, tool

# Define custom tools
@tool
def analyze_game_state(state_json: str) -> str:
    """Analyzes rugs.fun game state and returns strategic insights.

    Args:
        state_json: JSON string of current game state
    """
    # Parse and analyze
    state = json.loads(state_json)
    # ... analysis logic
    return strategic_advice

# Create agent
model = HfApiModel(model_id="Qwen/Qwen2.5-72B-Instruct")
agent = CodeAgent(
    tools=[analyze_game_state, query_qdrant, get_historical_patterns],
    model=model,
    additional_authorized_imports=['numpy', 'pandas']
)

# Run
result = agent.run("Analyze this game state and recommend action: {state}")
```

### 2.3 LangChain Integration (When Needed)

Use `langchain-huggingface` package for:
- Complex orchestration workflows
- Integration with existing LangChain tools
- LangGraph for stateful multi-agent systems

```python
from langchain_huggingface import HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-72B-Instruct",
    task="text-generation",
)
```

---

## Task 3: Tool Design Patterns

### 3.1 Standard Tool Interface (smolagents)

```python
from smolagents import tool
from typing import Optional

@tool
def query_game_history(
    game_id: str,
    event_type: Optional[str] = None,
    limit: int = 100
) -> str:
    """Queries historical game events from TimescaleDB.

    Args:
        game_id: The unique game identifier
        event_type: Filter by event type (e.g., 'bet', 'cashout')
        limit: Maximum events to return

    Returns:
        JSON string of matching events
    """
    import psycopg2
    import json

    conn = psycopg2.connect(
        host="timescaledb",
        port=5433,
        database="rugs_analytics",
        user=os.environ["TSDB_USER"],
        password=os.environ["TSDB_PASS"]
    )

    query = "SELECT * FROM game_events WHERE game_id = %s"
    params = [game_id]

    if event_type:
        query += " AND event_type = %s"
        params.append(event_type)

    query += " ORDER BY timestamp DESC LIMIT %s"
    params.append(limit)

    with conn.cursor() as cur:
        cur.execute(query, params)
        results = cur.fetchall()

    return json.dumps(results)
```

### 3.2 Best Practices

#### DO:
- **Type hints on all parameters** - Required for tool API generation
- **Detailed docstrings** - LLM reads these to understand tool usage
- **Return strings** - Easier for LLM to process
- **Handle errors gracefully** - Return error messages, don't raise
- **Keep tools atomic** - One tool, one purpose
- **Import inside function** - Required for Hub sharing

#### DON'T:
- **Complex return types** - Avoid nested objects
- **Side effects without confirmation** - Dangerous actions need safeguards
- **Unbounded queries** - Always have limits
- **Sensitive data in errors** - Sanitize error messages

### 3.3 Tool Categories for VECTRA-PLAYER

```python
# 1. RAG/Knowledge Tools
@tool
def search_protocol_docs(query: str) -> str:
    """Search rugs.fun protocol documentation in Qdrant."""

@tool
def get_strategy_patterns(pattern_type: str) -> str:
    """Retrieve known strategy patterns from knowledge base."""

# 2. Analytics Tools
@tool
def get_player_statistics(player_id: str) -> str:
    """Get historical statistics for a player."""

@tool
def analyze_market_conditions(timeframe: str) -> str:
    """Analyze recent market/game conditions."""

# 3. RL Integration Tools
@tool
def get_rl_policy_confidence(state: str) -> str:
    """Query RL model's confidence for current state."""

@tool
def suggest_curriculum_task(difficulty: str) -> str:
    """Suggest next training task for curriculum learning."""
```

### 3.4 Performance Optimizations

| Optimization | Implementation | Expected Benefit |
|--------------|----------------|------------------|
| **Caching** | `@lru_cache` for repeated queries | 50-80% latency reduction |
| **Batching** | Combine similar Qdrant queries | 30-50% fewer API calls |
| **Timeouts** | 10s default, 30s for complex | Prevent hanging |
| **Async** | `asyncio` for I/O-bound tools | 2-3x throughput |

---

## Task 4: Prompt Engineering for Game Analysis

### 4.1 Recommended Prompt Patterns

#### Pattern 1: Game State Analysis (ReAct-style)

```
You are a strategic analyst for rugs.fun, a crypto game with probabilistic outcomes.

GAME STATE:
{game_state_json}

AVAILABLE TOOLS:
- search_protocol_docs(query): Search game mechanics documentation
- get_player_statistics(player_id): Get historical player data
- analyze_market_conditions(timeframe): Analyze recent patterns

TASK: Analyze this game state and recommend whether to BET, HOLD, or CASHOUT.

Think step-by-step:
1. First, understand the current game phase and player positions
2. Query relevant historical patterns
3. Assess risk/reward based on game mechanics
4. Provide recommendation with confidence level

Begin your analysis:
```

#### Pattern 2: Feature Discovery for RL

```
You are helping train a reinforcement learning agent for rugs.fun.

CURRENT OBSERVATION SPACE:
{observation_features}

RECENT GAME TRAJECTORIES:
{trajectory_samples}

TASK: Identify potential new features that could improve RL performance.

Consider:
1. What patterns do successful players exploit?
2. What information is available but not currently captured?
3. What temporal patterns might be predictive?

Output as JSON:
{
  "proposed_features": [
    {"name": "...", "description": "...", "extraction_method": "..."}
  ],
  "rationale": "..."
}
```

#### Pattern 3: Curriculum Task Generation

```
You are designing a curriculum for training an RL agent on rugs.fun.

CURRENT AGENT CAPABILITIES:
- Win rate: {win_rate}%
- Average holding time: {avg_hold}s
- Risk tolerance: {risk_profile}

AVAILABLE TRAINING SCENARIOS:
{scenario_list}

TASK: Select the next training scenario that:
1. Is slightly harder than current capability
2. Focuses on the agent's weakest area
3. Has clear success criteria

Output:
{
  "scenario_id": "...",
  "difficulty": 1-10,
  "target_metric": "...",
  "success_threshold": ...
}
```

### 4.2 Prompt Optimization Tips

| Tip | Rationale | Impact |
|-----|-----------|--------|
| **Minimize context** | Tokens cost money/time | 20-40% cost reduction |
| **Structured output** | JSON schemas prevent parsing errors | 90%+ parse success |
| **Few-shot examples** | 2-3 examples improve consistency | 15-25% accuracy boost |
| **Role assignment** | "You are a strategic analyst" | Better adherence |
| **Step-by-step** | Explicit reasoning steps | Better on complex tasks |

### 4.3 When NOT to Use CoT

Based on 2025 research (Wharton study):
- **Reasoning models** (DeepSeek-R1, o1) already include CoT internally
- CoT adds 20-80% latency with minimal accuracy gain on these models
- Use CoT primarily with **non-reasoning models** (base Qwen, Llama)

---

## Task 5: Hybrid RL + Agent Architecture

### 5.1 Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                     HYBRID DECISION SYSTEM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │   RL Agent   │◄───────►│  LLM Agent   │                      │
│  │   (Fast)     │         │  (Strategic) │                      │
│  │   ~10ms      │         │   ~500ms     │                      │
│  └──────┬───────┘         └──────┬───────┘                      │
│         │                        │                               │
│         ▼                        ▼                               │
│  ┌──────────────────────────────────────────┐                   │
│  │           Decision Arbiter                │                   │
│  │  - Confidence comparison                  │                   │
│  │  - Latency budget management              │                   │
│  │  - Override logic                         │                   │
│  └──────────────────────────────────────────┘                   │
│                        │                                         │
│                        ▼                                         │
│               ┌──────────────┐                                  │
│               │    ACTION    │                                  │
│               └──────────────┘                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Decision Logic

```python
async def decide_action(state: GameState) -> Action:
    # 1. Always get RL prediction (fast)
    rl_action, rl_confidence = rl_agent.predict(state)

    # 2. Determine if LLM consultation needed
    should_consult_llm = (
        rl_confidence < CONFIDENCE_THRESHOLD or  # Low confidence
        state.is_critical_moment() or             # High stakes
        state.is_novel_situation()                # Unseen pattern
    )

    if should_consult_llm:
        try:
            # Async call with timeout
            llm_result = await asyncio.wait_for(
                llm_agent.analyze(state),
                timeout=LATENCY_BUDGET
            )

            if llm_result.confidence > rl_confidence:
                # Log for RL learning
                log_llm_override(state, rl_action, llm_result.action)
                return llm_result.action

        except asyncio.TimeoutError:
            # Fall back to RL
            pass

    return rl_action
```

### 5.3 When to Query Agent

| Trigger | Frequency | Latency Budget |
|---------|-----------|----------------|
| Low RL confidence (<0.6) | ~20% of decisions | 500ms |
| Critical game moments | ~5% of decisions | 1000ms |
| Novel state patterns | ~10% of decisions | 500ms |
| Periodic strategic review | Every 30s | 2000ms |
| Post-game analysis | After each game | 5000ms |

### 5.4 Learning from Agent

```python
class AgentGuidedReplayBuffer:
    """Store agent advice for RL training."""

    def add_agent_insight(self, state, agent_action, agent_reasoning):
        # Add to prioritized replay buffer
        self.buffer.add(
            state=state,
            expert_action=agent_action,
            priority=HIGH  # Agent advice gets priority
        )

    def sample_with_agent_guidance(self, batch_size):
        # 20% of batch from agent guidance
        agent_samples = self.buffer.sample_priority(batch_size // 5)
        regular_samples = self.buffer.sample_random(batch_size * 4 // 5)
        return agent_samples + regular_samples
```

---

## Task 6: Resource Optimization for VPS

### 6.1 VPS Constraints

| Resource | Available | Current Usage | For Agent |
|----------|-----------|---------------|-----------|
| CPU | 2 vCPU | ~30% | ~40-50% |
| RAM | 7.8 GB | ~2.9 GB | ~2-3 GB |
| Disk | 32 GB free | - | ~5 GB |
| Network | Unlimited | - | API calls |

### 6.2 Recommended Configuration: Hybrid API + Local

```
┌─────────────────────────────────────────┐
│           INFERENCE STRATEGY            │
├─────────────────────────────────────────┤
│                                         │
│  SIMPLE QUERIES (<50 tokens output)     │
│  ───────────────────────────────────    │
│  └──► Phi-3-mini (local, GGUF Q4)       │
│       • Latency: 50-100ms               │
│       • Cost: $0                         │
│       • RAM: ~3GB                        │
│                                         │
│  COMPLEX REASONING                      │
│  ───────────────────────────────────    │
│  └──► Qwen 2.5 72B (HF Inference API)   │
│       • Latency: 500-2000ms             │
│       • Cost: ~$0.0004/1K tokens        │
│       • RAM: 0 (remote)                 │
│                                         │
│  FALLBACK                               │
│  ───────────────────────────────────    │
│  └──► DeepSeek API / OpenRouter         │
│                                         │
└─────────────────────────────────────────┘
```

### 6.3 Local Model Setup (Phi-3-mini)

```bash
# Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make

# Download quantized model
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf

# Run server
./server -m Phi-3-mini-4k-instruct-q4.gguf -c 4096 --port 8080
```

**Expected Performance:**
- ~15-20 tok/s on 2 vCPU
- ~3GB RAM usage
- Suitable for: quick classification, simple queries

### 6.4 Cost Projections

| Usage Scenario | Queries/Day | Tokens/Query | Daily Cost | Monthly Cost |
|----------------|-------------|--------------|------------|--------------|
| Light (testing) | 100 | 500 | $0.02 | $0.60 |
| Medium (active) | 1,000 | 500 | $0.20 | $6.00 |
| Heavy (prod) | 10,000 | 500 | $2.00 | $60.00 |

**With Local Fallback:**
- Route 70% simple queries to local Phi-3
- Route 30% complex to API
- **Savings: 50-70%**

### 6.5 Optimization Strategies

| Strategy | Implementation | Savings |
|----------|----------------|---------|
| **Prompt caching** | Hash prompts, cache responses | 30-50% fewer calls |
| **Batch similar queries** | Queue + batch every 100ms | 20-30% throughput gain |
| **Response streaming** | Stream tokens as generated | Better UX, same cost |
| **Tiered routing** | Local for simple, API for complex | 50-70% cost reduction |

---

## Task 7: CI/CD Integration Patterns

### 7.1 Testing Strategy

```yaml
# .github/workflows/agent-tests.yml
name: Agent Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deterministic Tests
        run: |
          # Test tool implementations
          pytest tests/tools/ -v

          # Test prompt templates
          pytest tests/prompts/ -v

          # Test state parsing
          pytest tests/parsing/ -v

  agent-evals:
    runs-on: ubuntu-latest
    steps:
      - name: Install DeepEval
        run: pip install deepeval

      - name: Run Evaluations
        run: |
          # Non-deterministic agent tests
          deepeval test run tests/agent_evals/
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}

      - name: Check Thresholds
        run: |
          # Fail if accuracy < 80%
          python scripts/check_eval_thresholds.py
```

### 7.2 Evaluation Metrics

```python
# tests/agent_evals/test_game_analysis.py
from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    HallucinationMetric,
    TaskCompletionMetric
)

def test_game_state_analysis():
    test_cases = load_test_cases("game_analysis")

    metrics = [
        AnswerRelevancyMetric(threshold=0.7),
        HallucinationMetric(threshold=0.2),  # Max 20% hallucination
        TaskCompletionMetric(threshold=0.8)
    ]

    results = evaluate(
        test_cases=test_cases,
        metrics=metrics,
        run_async=True
    )

    assert results.overall_score >= 0.75, "Agent quality below threshold"
```

### 7.3 Monitoring Dashboard

**Key Metrics to Track:**

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Latency (p50) | <500ms | >1000ms |
| Latency (p95) | <2000ms | >5000ms |
| Success Rate | >95% | <90% |
| Hallucination Rate | <10% | >20% |
| Cost per Query | <$0.001 | >$0.005 |
| Tool Call Success | >98% | <95% |

### 7.4 Deployment Pipeline

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Push   │────►│  Test   │────►│  Eval   │────►│ Deploy  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                    │               │               │
                    ▼               ▼               ▼
              Unit Tests      Agent Evals     Canary (10%)
              Tool Tests      Quality Gate    Full Rollout
              Lint/Type       Cost Check      Rollback Ready
```

---

## Task 8: Security & Safety Considerations

### 8.1 Threat Model

| Threat | Risk Level | Attack Vector |
|--------|------------|---------------|
| Prompt Injection | HIGH | Malicious game data |
| SQL Injection | MEDIUM | TimescaleDB tool |
| Resource Exhaustion | MEDIUM | Infinite loops |
| API Key Exposure | HIGH | Logs, errors |
| Data Exfiltration | LOW | Tool misuse |

### 8.2 Security Checklist

#### Input Validation
- [ ] Sanitize all game state JSON before prompting
- [ ] Validate player IDs against allowlist format
- [ ] Limit input size (max 10KB per request)
- [ ] Strip potential injection patterns

#### Tool Safety
- [ ] Parameterized queries only (no string interpolation)
- [ ] Read-only database connections for analytics
- [ ] Tool execution timeouts (max 30s)
- [ ] Resource limits (max 100 rows per query)

#### Output Validation
- [ ] Parse agent outputs as structured JSON
- [ ] Reject malformed responses
- [ ] Confidence threshold for actions (min 0.6)
- [ ] Human-in-loop for high-stakes decisions

#### Secrets Management
- [ ] Use environment variables, never hardcode
- [ ] Rotate API keys monthly
- [ ] Separate keys for dev/staging/prod
- [ ] Audit key usage logs

### 8.3 Prompt Injection Prevention

```python
def sanitize_game_state(state: dict) -> dict:
    """Remove potential injection patterns from game state."""

    DANGEROUS_PATTERNS = [
        r'ignore previous',
        r'system:',
        r'<\|.*\|>',
        r'```',
    ]

    def clean_string(s: str) -> str:
        for pattern in DANGEROUS_PATTERNS:
            s = re.sub(pattern, '[FILTERED]', s, flags=re.IGNORECASE)
        return s

    def clean_recursive(obj):
        if isinstance(obj, str):
            return clean_string(obj)
        elif isinstance(obj, dict):
            return {k: clean_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_recursive(v) for v in obj]
        return obj

    return clean_recursive(state)
```

### 8.4 Sandboxed Execution

```python
from smolagents import CodeAgent, HfApiModel

agent = CodeAgent(
    tools=[...],
    model=model,
    # Execute code in Docker sandbox
    executor="docker",
    docker_image="python:3.11-slim",
    # Limit resources
    max_memory="512m",
    max_cpu="0.5",
    network_disabled=True,  # No network access from sandbox
)
```

---

## Task 9: Reference Implementations

### 9.1 Top GitHub Projects

| Project | URL | Stars | Key Learnings |
|---------|-----|-------|---------------|
| **GamingAgent** | [lmgame-org/GamingAgent](https://github.com/lmgame-org/GamingAgent) | Active | VLM game agents, benchmarking framework |
| **smolagents** | [huggingface/smolagents](https://github.com/huggingface/smolagents) | 15k+ | Official HF agent implementation |
| **AgentVerse** | [OpenBMB/AgentVerse](https://github.com/OpenBMB/AgentVerse) | 4k+ | Multi-agent simulation framework |
| **awesome-LLM-game-agent-papers** | [git-disl/...](https://github.com/git-disl/awesome-LLM-game-agent-papers) | 500+ | Paper collection, includes PokéLLMon |
| **LLMWars** | [andrewgph/llmwars](https://github.com/andrewgph/llmwars) | 200+ | Competitive LLM games in Docker |

### 9.2 Code Patterns to Adapt

#### From GamingAgent - Game State Handling

```python
class GameStateProcessor:
    """Process visual/text game state for LLM consumption."""

    def __init__(self, game_config: dict):
        self.config = game_config
        self.history = []

    def process_state(self, raw_state: dict) -> str:
        """Convert game state to LLM-friendly format."""

        # Extract key features
        features = {
            "phase": raw_state.get("gamePhase"),
            "players": self._summarize_players(raw_state.get("players", [])),
            "pot": raw_state.get("currentPot"),
            "my_position": raw_state.get("myPosition"),
        }

        # Add relevant history
        features["recent_actions"] = self.history[-5:]

        return json.dumps(features, indent=2)
```

#### From smolagents - Tool Registration

```python
from smolagents import Tool

class QdrantSearchTool(Tool):
    name = "search_knowledge_base"
    description = "Search the rugs.fun knowledge base for relevant information"
    inputs = {
        "query": {"type": "string", "description": "Search query"},
        "collection": {
            "type": "string",
            "description": "Collection to search",
            "enum": ["rugs_protocol", "rl_design", "external_docs"]
        },
        "limit": {"type": "integer", "description": "Max results", "default": 5}
    }
    output_type = "string"

    def forward(self, query: str, collection: str = "rugs_protocol", limit: int = 5) -> str:
        from qdrant_client import QdrantClient

        client = QdrantClient(host="localhost", port=6333)
        results = client.search(
            collection_name=collection,
            query_vector=self._embed(query),
            limit=limit
        )

        return json.dumps([
            {"text": r.payload["text"], "score": r.score}
            for r in results
        ])
```

### 9.3 Academic Implementations

| Paper | Code | Key Technique |
|-------|------|---------------|
| PokéLLMon (ICLR 2024) | [GitHub](https://github.com/git-disl/PokeLLMon) | In-context RL, battle agent |
| LLMHRL (2025) | N/A | Hierarchical RL with LLM teacher |
| GameBench | [GitHub](https://github.com/Jiarui-Lu/GameBench) | Multi-game evaluation |

---

## Task 10: Implementation Timeline & Effort Estimation

### 10.1 Revised Phase Breakdown

#### Phase 1: Foundation (2-3 weeks)

| Task | Days | Dependencies | Risk |
|------|------|--------------|------|
| Set up smolagents environment | 1 | None | Low |
| Configure HF Inference API | 1 | API key | Low |
| Create base tool interfaces | 3 | Qdrant running | Low |
| Implement Qdrant search tool | 2 | - | Low |
| Implement TimescaleDB tool | 2 | - | Medium |
| Basic agent with 3 tools | 3 | Above complete | Low |
| Testing framework setup | 2 | - | Low |

**Phase 1 Deliverable:** Working agent that can query knowledge base and answer questions about rugs.fun

#### Phase 2: Capabilities (4-5 weeks)

| Task | Days | Dependencies | Risk |
|------|------|--------------|------|
| Game state analysis tool | 4 | Protocol understanding | Medium |
| Player statistics tool | 3 | TimescaleDB schema | Low |
| Pattern recognition tool | 5 | Historical data | Medium |
| Strategy synthesis prompts | 4 | Game knowledge | Medium |
| Feature discovery capability | 5 | RL codebase access | High |
| Curriculum generation | 4 | RL training setup | High |
| Evaluation suite | 5 | Test data | Medium |

**Phase 2 Deliverable:** Agent can analyze games, discover features, suggest training curricula

#### Phase 3: Training Integration (4-6 weeks)

| Task | Days | Dependencies | Risk |
|------|------|--------------|------|
| RL codebase integration | 5 | RL repo access | High |
| Agent-guided replay buffer | 4 | RL training loop | High |
| Reward shaping from agent | 5 | Reward function | High |
| Curriculum learning system | 5 | Training infrastructure | High |
| A/B testing framework | 4 | Metrics collection | Medium |
| Performance benchmarking | 3 | Baseline metrics | Low |

**Phase 3 Deliverable:** RL training can be guided by agent insights

#### Phase 4: Hybrid Mode (6-8 weeks)

| Task | Days | Dependencies | Risk |
|------|------|--------------|------|
| Real-time decision arbiter | 5 | Phase 1-3 complete | High |
| Async agent queries | 4 | - | Medium |
| Confidence calibration | 5 | Test games | High |
| Fallback mechanisms | 3 | - | Low |
| Latency optimization | 5 | Performance data | Medium |
| Production hardening | 5 | All above | High |
| Documentation | 3 | - | Low |
| Load testing | 4 | Production env | Medium |

**Phase 4 Deliverable:** Production-ready hybrid RL+Agent system

### 10.2 Risk Factors

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| API rate limits | Medium | High | Local fallback model |
| Latency too high | Medium | High | Aggressive caching, tiered routing |
| Agent hallucinations | High | Medium | Confidence thresholds, validation |
| RL integration complexity | High | High | Incremental integration, feature flags |
| Cost overruns | Medium | Medium | Usage monitoring, caps |

### 10.3 Critical Path

```
Week 1-2:   Foundation (tools, basic agent)
    │
    ▼
Week 3-6:   Capabilities (analysis, discovery)
    │
    ▼
Week 7-12:  Training Integration (RL connection)
    │
    ▼
Week 13-20: Hybrid Mode (real-time decisions)
    │
    ▼
Week 21-22: Production Hardening
```

### 10.4 Go/No-Go Checkpoints

| Checkpoint | Week | Criteria |
|------------|------|----------|
| Phase 1 Complete | 3 | Agent answers protocol questions accurately |
| Phase 2 Complete | 8 | Agent suggests useful features (validated by human) |
| Phase 3 Complete | 14 | RL performance improves with agent guidance |
| Phase 4 Complete | 22 | Hybrid system operates in real-time (<500ms) |

---

## Appendix A: Model Comparison Table (Full)

| Model | Size | MMLU | MATH | Code | Context | API Cost | Local Viable | Recommendation |
|-------|------|------|------|------|---------|----------|--------------|----------------|
| GPT-4o | ? | 88% | 76% | 90% | 128K | $$$ | No | Good but expensive |
| Claude 3.5 Sonnet | ? | 89% | 78% | 92% | 200K | $$$ | No | Excellent reasoning |
| DeepSeek-R1 | 671B | 91% | 97% | 96% | 128K | $$ | No | **Best open reasoning** |
| DeepSeek-R1-Distill-32B | 32B | 85% | 94% | 88% | 128K | $ | Barely | **Best value** |
| Qwen 2.5 72B | 72B | 86% | 83% | 85% | 128K | $ | No | **Recommended API** |
| Qwen 2.5 7B | 7B | 74% | 65% | 72% | 128K | ¢ | Slow | Budget option |
| Llama 3.3 70B | 70B | 82% | 68% | 80% | 128K | $ | No | Good general |
| Phi-3-mini | 3.8B | 69% | 52% | 58% | 4K/128K | Free | **Yes** | **Local fallback** |
| Gemma 2 9B | 9B | 71% | 55% | 60% | 8K | ¢ | Slow | Alternative local |

---

## Appendix B: Useful Links

### Documentation
- [smolagents Documentation](https://huggingface.co/docs/smolagents)
- [HF Agents Course](https://huggingface.co/learn/agents-course)
- [LangChain-HuggingFace Integration](https://huggingface.co/blog/langchain)
- [DeepEval Testing Framework](https://github.com/confident-ai/deepeval)

### Research Papers
- [GameBench: Strategic Reasoning](https://arxiv.org/abs/2406.06613)
- [DeepSeek-R1 Technical Report](https://arxiv.org/abs/2501.12948)
- [Design Patterns for Prompt Injection Security](https://arxiv.org/abs/2506.08837)
- [LLMHRL: Hierarchical RL with LLM](https://www.sciencedirect.com/science/article/abs/pii/S0020025525008217)

### Tools & Frameworks
- [llama.cpp for CPU Inference](https://github.com/ggerganov/llama.cpp)
- [Qdrant Vector Database](https://qdrant.tech/documentation/)
- [Langfuse Observability](https://langfuse.com/)

---

## Appendix C: Quick Start Commands

```bash
# 1. Install smolagents
pip install smolagents

# 2. Set up HF token
export HF_TOKEN="hf_..."

# 3. Create basic agent
python -c "
from smolagents import CodeAgent, HfApiModel

model = HfApiModel('Qwen/Qwen2.5-72B-Instruct')
agent = CodeAgent(tools=[], model=model)
print(agent.run('What is 2+2?'))
"

# 4. Test local Phi-3 (optional)
# Install llama-cpp-python
pip install llama-cpp-python

# Download model
wget https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
```

---

*Report compiled: 2026-01-03*
*Research duration: ~4 hours*
*Sources: HuggingFace docs, arXiv papers, GitHub repositories, industry blogs*
