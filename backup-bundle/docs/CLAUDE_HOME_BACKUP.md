# Project: Quantitative Analysis & Trading Tools

## Project Overview
- Building tools for quantitative analysis and crypto trading
- Focus on decentralized exchanges (Hyperliquid, dYdX)
- AI signal generation and real-time processing
- Custom trading bots and data analysis tooling
- Smart money tracking and order book analysis

---

## Development Workflow: Superpowers Methodology

**Quick Reference**: `~/.claude/WORKFLOW_QUICKREF.md`

### The 5 Iron Laws

| Principle | Command | Rule |
|-----------|---------|------|
| TDD | `/tdd` | NO production code without failing test first |
| Verification | `/verify` | Evidence before claims, always |
| Debugging | `/debug` | NO fixes without root cause investigation (4-phase) |
| Planning | `/plan` | Plans must be executable with ZERO codebase context |
| Isolation | `/worktree` | Isolated workspace for each feature |

### Development Workflow
```
1. /plan "feature description"     # Design first
2. /worktree feature-name          # Isolate work
3. /tdd "first requirement"        # Test first
4. (implement minimal code)
5. /verify                         # Prove it works
6. /review                         # Quality check
7. (repeat 3-6 for each task)
8. git merge && cleanup worktree
```

### Thinking Budget Keywords
| Keyword | Tokens | Use For |
|---------|--------|---------|
| `think` | ~4k | Simple tasks, quick fixes |
| `think hard` | ~10k | Debugging, optimization |
| `think harder` | ~20k | Complex multi-file changes |
| `ultrathink` | ~32k | Architecture, complex refactors |

### Efficiency Mode (v1.1.0 - 2025-12-06)
For extended sessions, activate with "use efficiency mode":
- Skip TodoWrite for linear tasks
- Batch file reads in parallel
- Defer tests to end of logical unit
- Trust recent context (< 5 messages)
- Code review at phase end only

See `~/.claude/WORKFLOW_QUICKREF.md` for full details.

### Red Flags (STOP immediately)
- Writing code before tests
- Tests passing immediately when written
- Making multiple simultaneous changes
- "Just this once" rationalization
- Using words: "should," "probably," "seems to"
- Third fix attempt failed → architecture review

### Session Bootstrap (Copy-Paste for Fresh Sessions)
```
Read ~/.claude/WORKFLOW_QUICKREF.md and ~/CLAUDE.md to understand my development workflow.

I follow the Superpowers methodology:
1. TDD Iron Law: NO code without failing test first
2. Verification: Evidence before claims
3. Systematic Debugging: 4-phase root cause analysis
4. Zero-Context Plans: Plans executable by anyone
5. Git Worktrees: Isolated feature development

Acknowledge you understand these principles before we proceed.
```

---

## GitHub-First Development (MANDATORY)

**All development work MUST be tracked in GitHub.**

### SDLC Workflow
```
GitHub Issue → /plan → /scratchpad → /tdd (@QA) → implement (@Dev) → /review → gh pr create
```

### Automatic Behaviors (NO permission needed)
1. **Every task** starts with a GitHub Issue (create if none exists)
2. **Every branch** is named `<type>/issue-<number>-<description>`
3. **Every commit** references the issue number
4. **Every completion** creates a PR with `Closes #<issue>`

### GitHub CLI Commands
```bash
gh issue view 123          # Read issue requirements
gh issue create            # Create new issue
gh pr create               # Create pull request
gh pr merge --squash       # Merge after approval
```

### NEVER Do
- Push directly to main/master
- Create branches without issues
- Merge without PR review
- Use raw `git push` to remote (use `gh` instead)

### Agent Profiles
| Agent | Role | When to Use |
|-------|------|-------------|
| `@QA` | Write tests only | Phase 3: TDD |
| `@Dev` | Implementation only | Phase 4: Implementation |
| `@GitHub` | Repo master | All git operations |

---

## CV Boilerplate Framework (Primary Active Project)
- **Location**: `/home/nomad/Desktop/CV-BOILER-PLATE-FORK/`
- **Current Phase**: Phase 3 - Rugs.fun Integration & Custom CV Training System
- **Status**: Checkpoints 1-2 COMPLETED, Checkpoint 3 (Gymnasium Environment) PENDING
- **Key Achievement**: OCR extraction working with 67% accuracy (2/3 critical regions)
- **Vision**: Live training system that learns by watching human gameplay

### Rugs.fun Integration Progress
- ✅ **Checkpoint 1**: Configuration system with corrected region coordinates (13/13 tests)
- ✅ **Checkpoint 2**: RugsExtractor OCR wrapper (13/13 tests passing)
  - current_price (multiplier): 79.7% confidence ✅
  - current_balance (SOL): 100% confidence ✅
  - bet_amount: Known limitation (0.000 too small)
- 🎯 **Phase 3.5**: Training System - ACTIVE (see below)
- ⏳ **Checkpoint 3**: Gymnasium environment with browser automation (AFTER Phase 3.5)
- 📋 **Phase 4**: Advanced CV training (custom CNN) - PLANNED

### Phase 3.5: YOLO Object Detection (ACTIVE - Pivoted 2025-10-26)
**Strategic Pivot**: OCR-based approach abandoned in favor of YOLOv8 object detection after A/B testing revealed OCR was 0% accurate due to dynamic UI positioning, while YOLO achieved 62% overall with 94% on critical fields.

**Current Status**: Training YOLOv8n model overnight on 361 annotated images

**Key Milestones**:
- ✅ **3.5A-D**: OCR training infrastructure complete (session recording, game state detection, correction tools)
- ✅ **Bulk Data Collection**: 3 gameplay sessions captured, 361 frames annotated in Roboflow
- ✅ **A/B Testing**: Human-validated comparison of OCR vs YOLO
  - OCR: 0/79 fields = 0% (hardcoded regions fail on dynamic UI)
  - YOLO v3: 49/79 fields = 62% overall
    - Price: 94% ✅ (production ready)
    - Balance: 90% ✅ (production ready)
    - PNL: 53% (needs improvement)
    - Bet Amount: 26% (needs improvement)
- ✅ **Dataset**: 361 images (289 train / 49 valid / 23 test) with 9 classes
- ✅ **GitHub Repo**: https://github.com/Dutchthenomad/YOLO-Notebook
  - Colab-compatible training notebook
  - Auto-detects local/Colab environment
  - "Open in Colab" badge for one-click training
- 🏃 **Training v5**: Overnight training started (2025-10-26 evening)
  - Model: YOLOv8n (nano)
  - Epochs: 150 (early stopping patience=20)
  - Image size: 640x640 (GPU memory optimized)
  - Batch: 4 (CPU training)
  - Expected completion: 3-5 hours
  - Output: `runs/detect/train/weights/best.pt`

**Expected v5 Improvements** (361 images vs 111 in v3):
- Price: 94% → 96%+
- Balance: 90% → 93%+
- PNL: 53% → 75-80% (major improvement)
- Bet Amount: 26% → 70%+ (critical improvement)
- Countdown: 0% → 60-70% (new detections)
- Rugged: 0% → 65-75% (new detections)

**Architecture Decision**: YOLO chosen over OCR because:
1. Dynamic UI elements move/resize - OCR hardcoded regions fail
2. YOLO learns spatial relationships and adapts to UI changes
3. Faster inference (real-time gameplay detection)
4. Better accuracy on small/distorted text (bet amounts)

**Next Steps** (Tomorrow):
1. Evaluate v5 model accuracy
2. If <85%: Collect more training data (target 500+ images)
3. If ≥85%: Deploy to production pipeline
4. Integrate with game automation bot

**See**: `AB_TEST_RESULTS.md`, `docs/BULK_ANNOTATION_GUIDE.md`

### Custom CV Training Vision (Phase 4 - Future)
**Objective**: Advanced custom CNN training for 98%+ accuracy (after Phase 3.5 complete)
- **Approach**: Custom lightweight CNN architecture optimized for Rugs.fun
- **Data Requirements**: 5,000-10,000 labeled frames from Phase 3.5 sessions
- **Timeline**: 6 additional weeks after Phase 3.5
- **See**: `docs/projects/rugs_fun/CUSTOM_CV_TRAINING.md` and `PHASE_4_ROADMAP.md`

## Rugs.fun RL Trading Bot (Active Development - NEW)
- **Location**: `/home/nomad/Desktop/rugs-rl-bot/`
- **Current Phase**: Phase 0 Revision - Fix Reward Hacking + REPLAYER Integration
- **Status**: Phase 0 trained but has critical bugs, REPLAYER validation needed
- **Vision**: Dual-model system with sidebet predictor + RL trading bot working synergistically

### Project Phases

**✅ Phase 1: Environment & Data Collection** (COMPLETE)
- Gymnasium environment with 79 observation features
- 929 game recordings collected (`/home/nomad/rugs_recordings/`)
- REPLAYER system for game analysis

**✅ Phase 2: Sidebet Model Training** (COMPLETE - Nov 7, 2025)
- **Model**: Gradient Boosting Classifier (v3)
- **Performance**: 38.1% win rate (vs 16.7% random), 754% ROI
- **Martingale**: 100% success (never bankrupted in 200-game backtest)
- **Features**: 14-dimensional feature vector (z-score, volatility, sweet spot timing)
- **Output**: 5 real-time predictions per tick (probability, confidence, timing, flags)
- **Location**: `/home/nomad/Desktop/rugs-rl-bot/models/sidebet_v3_gb_*.pkl`
- **Documentation**: `/home/nomad/Desktop/rugs-rl-bot/REWARDS DESIGN AGENT DOCUMENTATION/sidebet_training/`

**✅ Phase 3: Empirical Analysis & Rewards Design** (COMPLETE - Nov 8, 2025)
- **Analysis**: 899 games analyzed, sweet spot (25-50x), temporal risk model (69-tick safe window)
- **Rewards Design**: Agent-designed Phase 0 config with 4 components (rug avoidance, zone entry, temporal, survival)
- **Training**: 250k timesteps, 552 episodes, reward improved from -1,500 to +4,890
- **Status**: Training completed successfully

**❌ Phase 0: Initial Training - FAILED** (Nov 8, 2025)
- **Model**: `models/phase0_20251108_200516/phase0_final.zip`
- **Training Metrics**: Episode reward 4,890, length 806 steps (looked successful)
- **Actual Performance**: 0% ROI, 0 positions opened, 100% SELL spam
- **Root Cause**: Reward hacking - rug avoidance bug rewards SELL without checking positions
- **Action Distribution**: 81.4% SELL_MAIN_25, 18.6% SELL_MAIN_100, 0% BUY
- **Status**: FAILED - Model exploits bug instead of trading
- **Documentation**: `docs/PHASE0_EVALUATION_RESULTS.md`

**❌ Phase 0 Revision: 100k Training - FAILED** (Nov 9, 2025)
- **Model**: `models/phase0_revised_20251109_103831/phase0_revised_final.zip`
- **Training**: 100k timesteps, appeared successful (reward +1,470, length 265)
- **Actual Performance**: 0% ROI, 0 positions opened (90.5% BUY_BOTH spam, all rejected)
- **Root Cause**: Sophisticated reward hacking - agent farms passive rewards without trading
  - Rug avoidance: +reward for avoiding rugs (without having positions!)
  - Zone entry: +reward for being in optimal zones (without entering!)
  - Survival bonuses: +reward for lasting long
- **Status**: FAILED - Model learned to farm passive rewards, not trade
- **Documentation**: `CRITICAL_BUGS_LOG.md`

**🔄 Phase 0 Clean Slate: Minimal Baseline** (ACTIVE - Nov 9, 2025 evening)
- **Philosophy**: Start from ZERO. Prove basics work before adding complexity.
- **Config**: `configs/reward_config_minimal.yaml` (only 2 components: financial + bankruptcy)
- **Verification**: `test_minimal_baseline.py` - ✅ PASSING (positions open correctly)
- **Critical Fixes**:
  1. Added guard checks in `reward_calculator.py` for optional parameters
  2. Fixed missing attribute crashes (zone_optimal_min, temporal_safe_window, etc.)
- **Status**: Environment verified working with minimal config
- **Next Steps**:
  1. Train minimal model (10k timesteps) to verify agent CAN learn
  2. Add debug logging to diagnose why trained models reject BUY attempts
  3. Only add complexity after proving base case works
- **Lesson Learned**: **Complexity is the enemy.** 17-component reward function enabled exploitation. 2 components make bugs obvious.

### Empirical Analysis Results (Nov 8, 2025)

**Analysis Completed**:
- ✅ **Phase 1**: Entry opportunity analysis (140K+ samples)
- ✅ **Phase 2**: Volatility & drawdown patterns
- ✅ **Phase 3**: Survival curves (conditional)
- ✅ **Phase 4**: Profit distributions by entry point
- ✅ **Phase 5**: Position duration & temporal risk (NEW)

**Critical Findings**:
1. **100% Rug Rate**: All entries eventually rug → exit timing is EVERYTHING
2. **25-50x Sweet Spot**: Best risk/reward (75% success, 186-427% median returns)
3. **Median Game Lifespan**: 138 ticks (50% of games rug by this point)
4. **Temporal Risk Model**: 38.3% rug in first 100 ticks, 79.3% by tick 300
5. **Stop Losses**: Should be 30-50%, not 10% (avg drawdowns 8-25%, recovery rate 85-91%)
6. **Optimal Hold Times**: 48-60 ticks for sweet spot entries (25-50x)
7. **Dynamic Profit Targets**: 1-10x→25%, 25-50x→100-200%, 100x+→10-25%
8. **Survivor Bias**: Cannot plan "hold 300 ticks" - 79% of games already dead

**Bayesian Model Parameters Generated**:
```python
TEMPORAL_RUG_PROB = {
    50: 0.234,   # 23.4% cumulative rug probability
    100: 0.386,  # 38.6%
    138: 0.500,  # 50% (median)
    200: 0.644,  # 64.4%
    300: 0.793   # 79.3%
}

EXIT_URGENCY = {
    'safe': 69,      # < 69 ticks
    'caution': 104,  # 69-104 ticks
    'danger': 138,   # 104-138 ticks (median rug)
    'critical': 268  # > 268 ticks (P75, 75% already rugged)
}

OPTIMAL_HOLD_TIMES = {
    1: 65,   # 61% success
    25: 60,  # 75% success (SWEET SPOT)
    50: 48,  # 75% success (SWEET SPOT)
    100: 71  # 36% success
}
```

**Analysis Scripts**:
- Entry/volatility/survival/profit: `/home/nomad/Desktop/REPLAYER/analyze_trading_patterns.py` (870 lines)
- Position duration/temporal: `/home/nomad/Desktop/REPLAYER/analyze_position_duration.py` (600 lines)
- Results: `trading_pattern_analysis.json` (12KB), `position_duration_analysis.json` (24KB)

### Rewards Design Documentation (For Agent Session)

**✅ Documentation Complete** (6 of 7 files, ~2,900 lines):

1. **FILE_SHARING_CHECKLIST.md** (450 lines) - Session workflow
2. **KEY_INSIGHTS.md** (267 lines) - Executive summary
3. **EMPIRICAL_DATA.md** (1,252 lines) ⭐ - Complete empirical findings
4. **LLM_INSTRUCTIONS.md** (270 lines) - Role + 8 required deliverables
5. **REWARD_DESIGN_PROMPT.md** (645 lines) - Master context
6. ⏳ QUESTIONS.md (~700 lines) - Pending
7. ⏳ BUNDLE.md (~700 lines) - Pending

**Location**: `/home/nomad/Desktop/rugs-rl-bot/REWARDS DESIGN AGENT DOCUMENTATION/trading_bot/`

### SidebetPredictor Integration

**Status**: Wrapper class created, tests passing (38/38)

**Components**:
- `SidebetPredictor` class (365 lines) - Real-time rug probability predictions
- 29 unit tests (100% passing)
- 9 integration tests (100% passing)
- **Location**: `/home/nomad/Desktop/rugs-rl-bot/rugs_bot/sidebet/predictor.py`

**Output Features** (5 per tick):
```python
{
    'probability': 0.0-1.0,        # Rug probability
    'confidence': 0.0-1.0,         # Prediction reliability
    'ticks_to_rug_norm': 0.0-1.0,  # Normalized timing estimate
    'is_critical': 0/1,            # Emergency flag (prob ≥ 0.50)
    'should_exit': 0/1             # Exit recommendation (prob ≥ 0.40)
}
```

**Integration Status**:
- ✅ Standalone predictor ready
- ⏳ Integration into RugsMultiGameEnv (pending rewards design)
- ⏳ Integration into REPLAYER for visual validation
- ⏳ Multi-game loop support
- ⏳ Validation dashboard UI updates

### Key Lesson: Visual Validation is Critical

**Problem**: Training metrics looked successful (reward 4,890, length 806 steps) but bot was completely broken
- Agent learned to exploit reward bug instead of trading
- Profitability metrics revealed 0% ROI, 0 positions opened
- **Root Cause**: No way to observe actual behavior during training

**Solution**: REPLAYER Integration
- Watch bot play in real-time to validate behavior
- Visual confirmation of trading logic (entries, exits, timing)
- Catch reward hacking before wasting compute on training
- Same system will be used for deployment - validate in production environment

### Development Roadmap (Updated Nov 8, 2025)

**Phase 0 Revision** (ACTIVE - 1-2 weeks):
1. ⏳ Fix rug avoidance reward bug (check `had_positions`)
2. ⏳ Rebalance reward weights (Financial P&L: 0.3→3.0)
3. ⏳ Add engagement penalties (inactivity, trade completion)
4. ⏳ Re-train Phase 0 model (100k-250k timesteps)
5. ⏳ Validate with profitability metrics (>5% ROI, >50% engagement)

**Phase 0.5: REPLAYER Integration** (PRIORITY - 1 week):
1. ⏳ Integrate trained RL model into REPLAYER
2. ⏳ Add real-time action visualization (BUY/SELL/WAIT indicators)
3. ⏳ Add reward component breakdown display
4. ⏳ Visual validation of 10-20 games
5. ⏳ Confirm bot behavior matches expectations before further training

**Phase 1: Refinement** (After visual validation):
1. ⏳ Tune hyperparameters based on observed behavior
2. ⏳ Extended training (500k-1M timesteps)
3. ⏳ Multi-game validation in REPLAYER
4. ⏳ Performance targets: 60%+ win rate, 90%+ rug avoidance, <5% bankruptcy

**Phase 2: Deployment** (Production ready):
1. ⏳ Integrate SidebetPredictor + RL bot coordination
2. ⏳ Live trading validation (paper trading)
3. ⏳ Risk management layer
4. ⏳ Production deployment

**Phase 3: Meta Bot Coordination** (Future):
- Dual-strategy system (sidebet + trading bot)
- Hedging and win multiplication
- Portfolio optimization

### Commands (Rugs RL Bot)

**Testing**:
- All tests: `cd ~/Desktop/rugs-rl-bot && .venv/bin/python -m pytest tests/ -v`
- Sidebet predictor: `.venv/bin/python -m pytest tests/test_sidebet/test_predictor.py -v`
- Integration tests: `.venv/bin/python -m pytest tests/test_environment/test_sidebet_integration.py -v`
- Config validation: `.venv/bin/python scripts/validate_phase0_config.py`

**Training**:
- Train Phase 0: `cd ~/Desktop/rugs-rl-bot && .venv/bin/python scripts/train_phase0_model.py --timesteps 250000`
- Test training: `.venv/bin/python scripts/train_phase0_model.py --timesteps 5000` (5k test run)

**Evaluation** (detect reward hacking):
- Full evaluation: `.venv/bin/python scripts/evaluate_phase0_model.py --model models/phase0_*/phase0_final.zip --episodes 50`
- Quick eval (10 games): `.venv/bin/python /tmp/eval_10games.py`
- Profitability analysis: `.venv/bin/python /tmp/profit_eval.py` (30 games, P&L tracking)
- Action distribution: `.venv/bin/python /tmp/diagnose_actions.py` (detect SELL spam)
- Reward breakdown: `.venv/bin/python /tmp/reward_breakdown.py` (component analysis)

**Empirical Analysis**:
- Trading patterns: `cd ~/Desktop/REPLAYER && python3 analyze_trading_patterns.py`
- Position duration: `python3 analyze_position_duration.py`
- Results: `cat trading_pattern_analysis.json | jq .`

### Project Structure (Rugs RL Bot)

**`/home/nomad/Desktop/rugs-rl-bot/`**:
- `/rugs_bot/` - Core RL bot modules
  - `/env/` - Gymnasium environment
  - `/sidebet/` - Sidebet model wrapper
    - `predictor.py` - SidebetPredictor class (365 lines)
    - `feature_extractor.py` - Feature engineering
  - `/rewards/` - Reward function components
- `/models/` - Trained models
  - `sidebet_v3_gb_*.pkl` - Sidebet classifier
  - `rl_trading_bot_*.zip` - RL policy (pending)
- `/tests/` - Test suite (38/38 passing)
- `/REWARDS DESIGN AGENT DOCUMENTATION/` - Agent session docs
  - `/sidebet_training/` - Phase 2 docs (reference)
  - `/trading_bot/` - Phase 3 docs (active)

**`/home/nomad/Desktop/REPLAYER/`**:
- Game replay and validation system
- Analysis scripts (trading patterns, duration, volatility)
- Results JSON files

**`/home/nomad/rugs_recordings/`**:
- 929 recorded game sessions (JSONL format)
- Dataset for empirical analysis

## REPLAYER - Dual-Mode Replay/Live Game Viewer (Production Ready)
- **Location**: `/home/nomad/Desktop/REPLAYER/`
- **Current Phase**: Phase 7B (Menu Bar UI) + Phase 8 Planning
- **Status**: ✅ **Production Ready** - Phase 6 complete, Phase 7A complete, 237/237 tests passing
- **Vision**: Dual-mode viewer (replay recorded games OR live WebSocket feed) + RL training environment

### Recent Completions (2025-11-15)

**✅ Phase 7A: RecorderSink Test Fixes** (Nov 15, 2025)
- Fixed `test_recorded_tick_format` - Save filepath before `stop_recording()`
- All 21 RecorderSink tests passing
- Documentation: `docs/PHASE_7A_COMPLETION.md`

**✅ Phase 6: WebSocket Live Feed Integration** (Nov 14, 2025)
- Live WebSocket feed working flawlessly (4.01 signals/sec, 241ms latency)
- Continuous multi-game support
- Thread-safe UI updates via TkDispatcher
- Documentation: `docs/PHASE_6_COMPLETION.md`

**✅ Production Audit Fixes** (Nov 15, 2025)
- **8 fixes applied**: Memory leaks, race conditions, file handle leaks, performance bottlenecks
- **Thread safety**: All menu callbacks use `root.after()`
- **Error boundaries**: All Socket.IO handlers wrapped in try/except
- **Decimal precision**: Price calculations use Decimal (not float)
- **Backpressure**: RecorderSink emergency flush on buffer overflow
- Documentation: `AUDIT_FIXES_SUMMARY.md`

### Key Features

**Dual-Mode Operation**:
- **Replay Mode**: Play back 929+ recorded games from JSONL files
- **Live Mode**: Real-time WebSocket feed from Rugs.fun backend
- **Perfect Fidelity**: Both modes use identical code paths (only tick SOURCE differs)

**Bot Automation**:
- 3 trading strategies: Conservative, Aggressive, Sidebet
- ML integration: SidebetPredictor (38.1% win rate, 754% ROI)
- Async execution with thread-safe UI updates
- Real-time decision visualization

**Production Infrastructure**:
- Event-driven architecture (EventBus pub/sub)
- Centralized state management (GameState with RLock)
- Auto-recording to JSONL (RecorderSink)
- Live ring buffer (5000-tick memory-bounded)
- Thread-safe UI marshaling (TkDispatcher)

### Next Phase: Phase 8 - UI-First Bot System (13-20 days)

**Vision**: Enable bot to execute trades through UI layer (not just backend) for live trading preparation

**Key Objectives**:
1. **Partial Sell Functionality** - 4 buttons (10%, 25%, 50%, 100%)
2. **BotUIController** - UI-layer execution bridge
3. **Playwright Integration** - Use existing CV-BOILER-PLATE automation
4. **Dual-Mode Execution** - Backend (fast, training) + UI (realistic, live prep)
5. **Timing Learning** - Bot learns realistic UI interaction delays
6. **State Synchronization** - Keep REPLAYER state in sync with browser DOM

**Phase Breakdown**:
- **Phase 8.1**: Partial Sell Infrastructure (2-3 days)
  - Extend Position model with `reduce_amount()` method
  - Add `execute_partial_sell()` to TradeManager
  - Add `partial_close_position()` to GameState
  - Write tests for partial sell functionality

- **Phase 8.2**: UI Partial Sell Buttons (1-2 days)
  - Replace single SELL button with 4 buttons (10%, 25%, 50%, 100%)
  - Add button handlers calling `execute_partial_sell(percentage)`
  - Update position display to show remaining position

- **Phase 8.3**: BotUIController (2-3 days)
  - Create BotUIController class for UI interaction
  - Implement methods: `set_bet_amount()`, `click_buy()`, `click_sell()`, etc.
  - Add ExecutionMode enum (BACKEND, UI_LAYER)
  - Update BotController for dual-mode execution

- **Phase 8.4**: Minimal Bot Configuration UI (1-2 days)
  - Create BotConfigPanel class
  - Add settings: execution mode, strategy, bet amount
  - Add "Bot → Configuration..." menu item
  - Persist config to `bot_config.json`

- **Phase 8.5**: Playwright Integration Bridge (3-4 days)
  - Create BrowserExecutor class
  - Import RugsBrowserManager from CV-BOILER-PLATE-FORK
  - Implement async browser control methods
  - Add `--live` command-line flag
  - Add execution validation and retry logic

- **Phase 8.6**: State Synchronization & Timing Learning (2-3 days)
  - Add browser state polling (read balance/position from DOM)
  - Add state reconciliation logic
  - Track execution timing metrics (click → effect delay)
  - Add timing dashboard UI

- **Phase 8.7**: Production Readiness (2-3 days)
  - Add safety mechanisms (loss limits, emergency stop)
  - Add comprehensive logging
  - Update documentation
  - Full end-to-end testing (backend + UI modes)

**Success Criteria**:
- ✅ Bot can execute trades via backend (existing)
- ✅ Bot can execute trades via UI layer (new)
- ✅ Timing metrics tracked and displayed
- ✅ State synchronized between REPLAYER and browser
- ✅ Configuration persisted across sessions
- ✅ All tests passing (240+ tests)

**Timeline**: 13-20 days total

### Commands (REPLAYER)

**Running**:
- Run application: `cd ~/Desktop/REPLAYER && ./run.sh`
- Run tests: `cd ~/Desktop/REPLAYER/src && python3 -m pytest tests/ -v` (237/237 passing)

**Analysis Scripts**:
- Trading patterns: `cd ~/Desktop/REPLAYER && python3 analyze_trading_patterns.py`
- Position duration: `python3 analyze_position_duration.py`
- Game durations: `python3 analyze_game_durations.py`
- Results: `cat trading_pattern_analysis.json | jq .`

**Integration**:
- Uses `/home/nomad/rugs_recordings/` for replay data (929 games)
- Symlinks to `/home/nomad/Desktop/rugs-rl-bot/rugs_bot/sidebet/` for ML predictor
- Will integrate with `/home/nomad/Desktop/CV-BOILER-PLATE-FORK/` for Playwright automation (Phase 8.5)

### Architecture Highlights

**Thread-Safe Design**:
- `TkDispatcher` - Marshals UI updates from background threads to main thread
- `GameState` - RLock for re-entrant locking, releases lock before callbacks
- `EventBus` - Queue-based async processing (5000 event capacity)

**Event-Driven**:
- 20+ event types (game, trading, bot, UI)
- Pub/sub pattern via EventBus
- Weak references prevent memory leaks

**Dual-Mode Ready**:
- `ReplaySource` abstraction (file vs live feed)
- Identical code paths for replay and live modes
- Only difference: tick SOURCE

**Production Quality**:
- Comprehensive error handling
- Resource cleanup (atexit handlers)
- Audit-approved (8 critical/high fixes applied)
- 237/237 tests passing

### Documentation

**Project Docs** (`/home/nomad/Desktop/REPLAYER/`):
- `CLAUDE.md` - Comprehensive project context (this session's updates)
- `AGENTS.md` - Concise repository guidelines
- `SESSION_PLANNING.md` - Detailed planning document
- `AUDIT_FIXES_SUMMARY.md` - Complete audit fix details
- `docs/PHASE_6_COMPLETION.md` - Live feed integration
- `docs/PHASE_7A_COMPLETION.md` - RecorderSink test fixes

**Key Files to Know**:
- `src/core/game_state.py` - Centralized state management (640 lines)
- `src/ui/main_window.py` - Main UI window (926 lines)
- `src/ui/tk_dispatcher.py` - Thread-safe UI updates (47 lines)
- `src/services/event_bus.py` - Event pub/sub system
- `src/bot/controller.py` - Bot control (152 lines)

## 2048 Bot Educational Platform (Reference Project)
- **Location**: `/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo/`
- **Current Phase**: Phase 2C COMPLETED - GUI Integration & Production Readiness
- **Latest Performance**: 2.36 points/move efficiency (improved from 2.24)
- **Target Baseline**: 11.54 points/move (human baseline)
- **Key Achievement**: Full GUI integration with real-time screenshot display and organized data management

### Recent Accomplishments
- ✅ Enhanced strategy from simple priorities to sophisticated heuristic evaluation
- ✅ Fixed critical bugs: empty tile counting, move recommendation interface
- ✅ Implemented weight tuning framework with multiple configurations
- ✅ Achieved consistent 32-tile performance with optimized weights
- ✅ All testing conducted in non-headless mode (visible browser) for validation
- ✅ **CRITICAL**: Fixed GUI screenshot display - Live Game Display now functional
- ✅ **NEW**: Comprehensive screenshot management system with session organization
- ✅ **NEW**: Direct memory-to-GUI transfer eliminating file I/O bottleneck
- ✅ **NEW**: Production-ready codebase with clean file structure

### Future Algorithm Framework (Planned)
```
algorithms/
├── basic/                     # Current priority-based system
├── heuristic/                 # Enhanced weighted heuristics (current)
├── reinforcement_learning/    # RL training modules
├── deep_rl/                   # Deep reinforcement learning
├── minimax/                   # Game tree search algorithms
└── student_submissions/       # Student-developed algorithms
```

### Educational Platform Vision
- **Algorithm Selection**: Choose strategy algorithm for any game session
- **ML Integration**: RL/Deep RL wrappers for student bot training
- **Competition System**: Leaderboard with verified scores and model sharing
- **Learning Framework**: Structured curriculum for AI/ML education

### CV Boilerplate Commands (Rugs.fun Integration)
**Location**: `cd ~/Desktop/CV-BOILER-PLATE-FORK`

**Testing & Verification:**
- Run all tests: `.venv/bin/python3 -m pytest tests/ -v`
- Config validation: `.venv/bin/python3 -m pytest tests/test_rugs_config.py -v`
- OCR extraction tests: `.venv/bin/python3 -m pytest tests/test_rugs_extractor.py -v -s`
- Checkpoint 1 verification: `.venv/bin/python3 scripts/verify_checkpoint_rugs_1.py`
- Checkpoint 2 verification: `.venv/bin/python3 scripts/verify_checkpoint_rugs_2.py`
- Checkpoint 3.5A verification: `.venv/bin/python3 scripts/verify_checkpoint_rugs_3a.py` ✅
- Checkpoint 3.5B verification: `.venv/bin/python3 scripts/verify_checkpoint_rugs_3b.py` ✅
- SessionRecorder tests: `.venv/bin/python3 -m pytest tests/test_session_recorder.py -v`
- GameStateDetector tests: `.venv/bin/python3 -m pytest tests/test_game_state_detector.py -v`
- Browser viewport debug: `.venv/bin/python3 scripts/debug_browser_viewport.py`

**OCR Validation Tools:**
- Interactive validation: `.venv/bin/python3 tools/ocr_validation_tool.py rugs_screenshot.png rugs_hud_regions.json`
- Quick demo: `.venv/bin/python3 tools/ocr_validation_demo.py`

**Phase 3.5 Commands (YOLO Training - ACTIVE):**
- **Train YOLO model overnight**: `.venv/bin/python3 train_overnight.py`
- **Open training notebook in VS Code**: `./open_notebook.sh`
- **Validate training setup**: `.venv/bin/python3 scripts/validate_training_setup.py`
- **Bulk gameplay collection**: `.venv/bin/python3 scripts/rugs_fun/bulk_collect_gameplay.py --games 20`
- **Sample frames for annotation**: `.venv/bin/python3 scripts/sample_frames_for_annotation.py <session_dir> --count 30`
- **Human validation of A/B test**: `.venv/bin/python3 scripts/validate_ab_test_human.py`
- **Run A/B test session**: `.venv/bin/python3 scripts/run_ab_test_session.py`

**Phase 3.5 Legacy (OCR Infrastructure - Reference):**
- Setup Phantom profile: `.venv/bin/python3 scripts/setup_phantom_profile.py`
- Session recording: `.venv/bin/python3 scripts/verify_checkpoint_rugs_3b.py`
- SessionRecorder tests: `.venv/bin/python3 -m pytest tests/test_session_recorder.py -v`
- GameStateDetector tests: `.venv/bin/python3 -m pytest tests/test_game_state_detector.py -v`

**GitHub Repositories:**
- **Main CV Boilerplate**: https://github.com/Dutchthenomad/CV-BOILER-PLATE-FORK (if pushed)
- **YOLO Training Notebook**: https://github.com/Dutchthenomad/YOLO-Notebook ✅
  - Colab link: https://colab.research.google.com/github/Dutchthenomad/YOLO-Notebook/blob/main/train_rugs_yolo.ipynb

### 2048 Bot Commands (Reference)
- Performance test: `cd ~/Desktop/SOLANA\ EDU/2048-playwright-fork/2048-demo && python run_visible_bot.py`
- Strategy validation: `cd ~/Desktop/SOLANA\ EDU/2048-playwright-fork/2048-demo && python test_enhanced_strategy.py`
- Weight tuning: `cd ~/Desktop/SOLANA\ EDU/2048-playwright-fork/2048-demo && python weight_tuning_framework.py`
- Quick comparison: `cd ~/Desktop/SOLANA\ EDU/2048-playwright-fork/2048-demo && python quick_weight_test.py`
- **GUI Mode**: `cd ~/Desktop/SOLANA\ EDU/2048-playwright-fork/2048-demo && python gui_enhanced_2048_bot.py --gui`
- **Algorithm Demo**: `cd ~/Desktop/SOLANA\ EDU/2048-playwright-fork/2048-demo && python algorithm_comparison_demo.py`
- **Student Workflow**: `cd ~/Desktop/SOLANA\ EDU/2048-playwright-fork/2048-demo && python demo_student_workflow.py`

## Useful Commands

### Hyperliquid Data System
- Setup: `cd ~/Desktop/hyperliquid-data-system && ./setup.sh`
- Run interactive: `cd ~/Desktop/hyperliquid-data-system && ./run.sh`
- Run headless: `cd ~/Desktop/hyperliquid-data-system && ./start-headless.sh`
- Monitor: `cd ~/Desktop/hyperliquid-data-system && ./monitor.sh`
- Install as service: `cd ~/Desktop/hyperliquid-data-system && sudo ./install-service.sh`

### MCP Server
- Start server: `cd /home/nomad/mcp-server && npm start`
- Start in dev mode: `cd /home/nomad/mcp-server && npm run dev`
- Run client example: `cd /home/nomad/mcp-server && node client-example.js`

### Environment Setup
- Install dependencies: `npm install`
- Start InfluxDB: `docker-compose up -d influxdb`

## Project Structure

### `/Desktop/CV-BOILER-PLATE-FORK` (Primary Active Codebase)
- Computer vision boilerplate framework for game automation
  - `/core` - Core library modules
    - `/browser` - Browser automation modules
      - `controller.py` - Playwright browser control
      - `persistent_profile.py` - Persistent Chromium profile system (150 lines)
    - `/vision` - Vision processing modules
      - `ocr_extractor.py` - Generic OCR wrapper (EasyOCR/Tesseract)
    - `/rugs` - Rugs.fun game-specific modules
      - `extractor.py` - RugsExtractor class (game-specific OCR wrapper)
      - `session_recorder.py` - SessionRecorder with profile support (360 lines)
      - `game_state_detector.py` - 5-state game detection (90 lines)
      - `automation.py` - Wallet connection automation (180 lines)
      - `environment.py` - RugsEnv Gymnasium interface (PENDING - Checkpoint 3)
  - `/tests` - Test-driven development test suite
    - `test_rugs_config.py` - Configuration validation tests (13/13 passing)
    - `test_rugs_extractor.py` - OCR extraction tests (13/13 passing)
    - `test_session_recorder.py` - Session recorder tests (21/21 passing)
    - `test_game_state_detector.py` - Game state detection tests (7/7 passing)
    - `test_persistent_profile.py` - Persistent profile tests (9/9 passing)
    - `test_rugs_env.py` - Gymnasium environment tests (PENDING)
  - `/scripts` - Utility and verification scripts
    - `verify_checkpoint_rugs_1.py` - Checkpoint 1 verification (config)
    - `verify_checkpoint_rugs_2.py` - Checkpoint 2 verification (OCR)
    - `verify_checkpoint_rugs_3a.py` - Checkpoint 3.5A verification (recorder)
    - `verify_checkpoint_rugs_3b.py` - Checkpoint 3.5B verification (wallet, 334 lines)
    - `setup_phantom_profile.py` - Interactive wallet setup (280 lines)
    - `debug_browser_viewport.py` - Viewport diagnostic tool (180 lines)
  - `/tools` - OCR validation and calibration tools
    - `ocr_validation_tool.py` - Interactive OCR validation
    - `ocr_validation_demo.py` - Non-interactive demo
  - `/docs/projects/rugs_fun/` - Rugs.fun project documentation
    - `tui_extensions.md` - TUI design notes
    - `TRAINING_SYSTEM.md` - Training system architecture
    - `CUSTOM_CV_TRAINING.md` - Custom CV training architecture (Phase 4)
    - `PHASE_4_ROADMAP.md` - Implementation roadmap
  - `rugs_hud_regions.json` - HUD region configuration (15 annotated regions)
  - `rugs_screenshot.png` - Test screenshot for validation

### `/Desktop/hyperliquid-data-system`
- Primary data collection and analysis system for Hyperliquid
  - `/src` - Source code files
    - `index.js` - Main system entry point and process manager
    - `collector.js` - Data collection and smart money analysis logic
    - `api.js` - REST API implementation
    - `/utils` - Utility modules
      - `db.js` - Database connection and queries
      - `logger.js` - Logging system
  - Various shell scripts for system operations
  - Documentation files (README, SMART-MONEY, FAQ)

### `/mcp-server`
- Main MCP server implementation
  - `/src` - Source code files
    - `server.js` - WebSocket server implementation
    - `market-data.js` - Market data connectors and handling
    - `signal-generator.js` - Trading signal generation
    - `index.js` - Main entry point
    - `/exchanges` - Exchange-specific connectors
      - `hyperliquid.js` - Hyperliquid exchange API client
      - `dydx.js` - dYdX exchange API client
  - `architecture.md` - Detailed architecture documentation
  - `client-example.js` - Example WebSocket client

## Code Style Preferences
- Modern JavaScript (ES6+)
- Async/await for asynchronous operations
- Modular architecture with clear separation of concerns
- EventEmitter pattern for exchange connectors
- Comprehensive error handling for 24/7 operation

## Smart Money Analysis Features
- Whale wallet tracking
- Order book imbalance detection
- Liquidity grab identification
- Funding rate arbitrage scanning
- Liquidation event monitoring

## Notes & References
- Implementing data collection and analysis systems as foundation for signal generation
- Primary focus: high-quality data analysis and trading automation
- Smart money footprint detection as key strategy development area
- Hyperliquid API docs: https://hyperliquid.xyz/docs/api
- dYdX API docs: https://docs.dydx.exchange/
- InfluxDB docs: https://docs.influxdata.com/