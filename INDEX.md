# Bot Testing Framework - Complete Index

## 📋 Start Here

New to this framework? **Read in this order:**

1. **[QUICK_START.md](QUICK_START.md)** ⚡ - 5 minutes
   - Installation
   - Run your first test
   - Basic troubleshooting

2. **[README.md](README.md)** 📖 - 15 minutes
   - Architecture overview
   - What gets tested
   - How it works

3. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** 🏗️ - 20 minutes
   - What was built
   - Code examples
   - File structure

4. **[examples/README.md](examples/README.md)** 🔧 - 10 minutes
   - 3 ways to run tests
   - Real output examples
   - Troubleshooting

5. **[examples/USAGE.md](examples/USAGE.md)** 📚 - Reference
   - Detailed commands
   - Test coverage breakdown
   - Advanced usage

---

## 🚀 Quick Commands

### Install
```bash
cd AIforce_coding
pip install -r requirements.txt
```

### Recommended: Full Test Pipeline
```bash
cd AIforce_coding/tests
# Edit pipeline.py main() with your config path, then:
python3 pipeline.py
```

**What it runs**:
1. Config analysis and validation
2. Structural tests (24 tests)
3. Bot import on platform
4. Behavioral tests (33 tests)
5. Cleanup (removes bot)

### Alternative: Manual Pytest Control

**Structural Tests Only**:
```bash
cd AIforce_coding
pytest tests/test_structural.py --bot-config=/path/to/config.json -v
```

**Behavioral Tests Only** (requires deployed bot):
```bash
pytest tests/ -m behavioral \
  --bot-id=8553 \
  --current-version-id=8581 \
  --bot-config=/path/to/config.json -v
```

**Test All Bots** (structural only):
```bash
for bot in ../mws_api/test_api/bot-*.json; do
    pytest tests/test_structural.py --bot-config=$bot -v
done
```

---

## 📁 File Structure

```
AIforce_coding/
│
├── 📄 Documentation (Start Here!)
│   ├── INDEX.md                     ← You are here
│   ├── QUICK_START.md               ← Read this first
│   ├── README.md                    ← Full overview
│   └── IMPLEMENTATION_SUMMARY.md    ← Architecture details
│
├── 📦 Framework Package (bot_testing/)
│   ├── utils.py                     ← Utility functions (regex_to_sample)
│   ├── config/
│   │   ├── loader.py                ← Load bot JSON
│   │   ├── extractor.py             ← Parse bot structure
│   │   └── element_types.py         ← Data classes
│   ├── execution/
│   │   ├── handler.py               ← Platform API handler
│   │   └── client.py                ← Bot API client
│   └── coverage/
│       └── tracker.py               ← Coverage tracking (Phase 4)
│
├── 🧪 Tests (tests/)
│   ├── conftest.py                  ← Pytest fixtures + dynamic parametrization
│   ├── test_structural.py           ← 24 structural tests
│   ├── test_connectivity.py         ← 10 universal connectivity tests
│   ├── test_entry_edges.py          ← 8 parametrized entry edge tests
│   └── test_blocks.py               ← 15 config-driven block tests
│
├── 🔧 Examples (examples/)
│   ├── README.md                    ← Examples guide
│   ├── USAGE.md                     ← Detailed reference
│   ├── run_bot_8553_tests.sh        ← Bash script
│   ├── run_bot_8553_tests.py        ← Python script
│   └── run_tests_api.py             ← Programmatic API
│
├── ⚙️ Configuration
│   ├── requirements.txt              ← Dependencies
│   ├── pytest.ini                   ← Pytest config
│   └── .env.example                 ← Environment template
│
└── 📝 Project Files
    └── .gitignore                   ← Git exclusions
```

---

## 🎯 What Each Component Does

### ConfigLoader (`bot_testing/config/loader.py`)
**Purpose**: Load bot configuration files
```python
loader = ConfigLoader("bot-8553.json")
config = loader.load()  # Returns dict
```

### ElementExtractor (`bot_testing/config/extractor.py`)
**Purpose**: Extract blocks, edges, nodes, scenarios
```python
extractor = ElementExtractor(config)
blocks = extractor.extract_blocks()
llm_blocks = extractor.extract_blocks_by_type("llm")
scenarios = extractor.extract_scenarios()
```

### Data Classes (`bot_testing/config/element_types.py`)
**Purpose**: Type-safe representation of bot elements
```python
BlockInfo, EntryEdgeInfo, NodeInfo, ScenarioInfo, BotInfo
```

### Test Fixtures (`tests/conftest.py`)
**Purpose**: Inject bot configuration into tests
```python
@pytest.fixture
def bot_config(bot_config_path):
    # Loads BOT_CONFIG_PATH environment variable
    return ConfigLoader(bot_config_path).load()
```

### Structural Tests (`tests/test_structural.py`)
**Purpose**: Validate bot configuration structure (24 tests)
```python
- TestBotConfiguration (3 tests)
- TestScenarioStructure (3 tests)
- TestNodeStructure (3 tests)
- TestBlockStructure (2 tests)
- TestEntryEdgeValidation (3 tests)
- TestNodeReferences (3 tests)
- TestRegexPatterns (1 test)
- TestVariableUsage (4 tests)
- TestScenarioConsistency (2 tests)
```

### BotTestClient (`bot_testing/execution/client.py`)
**Purpose**: API wrapper for behavioral tests (Phase 2)
```python
client = BotTestClient("http://api-url", "token")
await client.deploy_bot(config)
response = await client.send_message("hello")
```

### CoverageTracker (`bot_testing/coverage/tracker.py`)
**Purpose**: Track test coverage (Phase 4)
```python
tracker = CoverageTracker()
tracker.mark_block_tested("scenarios[0].nodes[0].blocks[0]")
summary = tracker.get_coverage_summary(total=50)
```

---

## 📊 Test Statistics

### Bot-8553 ("Рекомендатор ужина v3")
- **Scenarios**: 6
- **Nodes**: ~15
- **Blocks**: ~31
  - Answer: 8
  - Buttons: 8
  - Extend: 7
  - LLM: 3
  - Single-If: 2
  - Wait: 3
- **Entry Edges**: 6 (5 match, 1 event)
- **Tests**: 24 structural tests
- **Time**: < 1 second

### Bot-97 ("supabase_check")
- **Scenarios**: 1
- **Nodes**: 2
- **Blocks**: ~5
- **Entry Edges**: 1
- **Tests**: 24 structural tests
- **Time**: < 1 second

---

## 🏃 Quickest Test Run

1. **Install**:
   ```bash
   cd AIforce_coding
   pip install -r requirements.txt
   ```

2. **Configure** (edit `tests/pipeline.py`):
   ```python
   config_path = "/path/to/your/bot-config.json"
   ```

3. **Run**:
   ```bash
   cd tests
   python3 pipeline.py
   ```

4. **See Results**:
   ```
   ✓ Step 1: Config analyzed
   ✓ Step 2: Structural tests PASSED (24 tests)
   ✓ Step 3: Bot imported on platform
   ✓ Step 4: Behavioral tests PASSED (33 tests)
   ✓ Pipeline Completed Successfully!
   ```

---

## 🔍 Full Test Pipeline with Analysis

The `pipeline.py` module provides comprehensive testing:

```bash
cd AIforce_coding/tests
python3 pipeline.py
```

**Pipeline Steps**:
1. **Config Analysis**
   - Validates JSON schema
   - Extracts bot elements (scenarios, nodes, blocks, edges)
   - Reports configuration summary
2. **Structural Tests**
   - 24 tests validating bot structure
   - No deployment required
3. **Platform Import**
   - Deploys bot via API
   - Returns bot_id and version_id
4. **Behavioral Tests**
   - 33 tests validating bot behavior
   - Config-driven and parametrized
   - Auto-skips tests for missing features
5. **Cleanup**
   - Removes bot from platform

---

## 🛠️ For Developers

### Understanding the Framework

1. **Data Flow**:
   ```
   Bot JSON File
        ↓
   ConfigLoader.load()
        ↓
   {bot_config dict}
        ↓
   ElementExtractor(config)
        ↓
   BlockInfo, EntryEdgeInfo, NodeInfo...
        ↓
   Pytest Tests
   ```

2. **Test Injection**:
   ```
   BOT_CONFIG_PATH=bot-8553.json
        ↓
   conftest.py fixture
        ↓
   bot_config parameter
        ↓
   test_structural.py methods
   ```

3. **Generic Test Pattern**:
   ```python
   @pytest.mark.structural
   def test_validation(self, bot_config, element_extractor):
       # Same code, different bot!
       # Works for bot-97 AND bot-8553
       blocks = element_extractor.extract_blocks()
       assert len(blocks) > 0
   ```

### Adding New Tests

1. Open `tests/test_structural.py`
2. Find appropriate test class or create new one
3. Add test method with `@pytest.mark.structural`
4. Use fixtures: `bot_config`, `element_extractor`
5. Run: `BOT_CONFIG_PATH=../mws_api/test_api/bot-8553-v8581.json pytest tests/test_structural.py -v`

### Using in Your Code

```python
from bot_testing.config import ConfigLoader, ElementExtractor

# Load any bot
loader = ConfigLoader("my-bot.json")
config = loader.load()

# Extract elements
extractor = ElementExtractor(config)

# Work with elements
for block in extractor.extract_blocks():
    print(f"Block type: {block.type}")
    print(f"Scenario: {block.scenario_slug}")
    print(f"Configuration: {block.data}")
```

---

## 🐛 Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| `pytest not found` | Run `pip install -r requirements.txt` |
| `Config file not found` | Set `BOT_CONFIG_PATH` or check path |
| `Module not found` | Run from `AIforce_coding` directory |
| `Permission denied` | Run `chmod +x examples/*.sh` |
| Test failures | Check output for which field is missing |

See `examples/USAGE.md` for detailed troubleshooting.

---

## 📈 What's Being Tested

### Configuration Level
- ✓ Bot has required fields
- ✓ Scenarios properly defined
- ✓ Nodes properly defined
- ✓ Blocks properly defined

### Reference Level
- ✓ Button targets point to real nodes
- ✓ Single-if targets point to real nodes
- ✓ Extend blocks target real scenarios

### Type Level
- ✓ Block types are valid
- ✓ Edge types are valid

### Content Level
- ✓ Regex patterns are valid
- ✓ Variables are defined
- ✓ LLM blocks have models
- ✓ HTTP blocks have URLs
- ✓ Button blocks have buttons

### Consistency Level
- ✓ Node IDs are unique
- ✓ Scenario IDs are unique
- ✓ Scenario slugs are unique

---

## 🚦 Status

### Phase 1: Structural Validation ✅ COMPLETE
- ConfigLoader, ElementExtractor
- 24 structural tests
- Works with bot-97 and bot-8553
- 3 executable examples

### Phase 2: Behavioral Tests ✅ COMPLETE
- Config-driven entry edge tests (parametrized over match edges)
- Universal connectivity tests (work for any bot)
- Block-type-specific tests with auto-skip
- 33 total behavioral tests across 3 files
- Config loads from file OR platform API

### Phase 3: Advanced Behavioral Tests 🔜 UPCOMING
- Test LLM block execution with models
- Test HTTP request blocks
- Test Script block execution
- Coverage path tracking

### Phase 4: Coverage & Reporting 🔜 UPCOMING
- HTML coverage reports
- CLI tool for easy test running
- CI/CD integration
- Coverage dashboard

---

## 📞 Getting Help

1. **Quick answer?** → Read [QUICK_START.md](QUICK_START.md)
2. **How it works?** → Read [README.md](README.md)
3. **Code examples?** → Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
4. **Run examples?** → See [examples/README.md](examples/README.md)
5. **Detailed reference?** → See [examples/USAGE.md](examples/USAGE.md)
6. **Stuck?** → Check [examples/USAGE.md](examples/USAGE.md) troubleshooting section

---

## 💡 Key Insights

### 1. Generic Tests
Same test code works for **any bot** - no code generation needed!

### 2. Runtime Injection
Bot configuration is injected via environment variable - no test modifications needed!

### 3. Reusable Components
Framework components can be used independently in your code.

### 4. Extensible Design
Easy to add new tests or new block types without modifying existing code.

### 5. No Deployment Required
Structural tests run instantly without deploying to API.

---

## 🎓 Learn By Example

### Full Test Pipeline (Recommended)
```bash
cd AIforce_coding/tests
# Edit pipeline.py with your config path
python3 pipeline.py
```

### Programmatic Pipeline Access
```python
from tests.pipeline import run_full_pipeline

success = run_full_pipeline(
    config_path="/path/to/bot-config.json",
    skip_structural=False,   # Run structural tests
    skip_import=False,       # Import on platform
    skip_behavioral=False,   # Run behavioral tests
)
```

### Individual Pipeline Steps
```python
from tests.pipeline import (
    load_and_analyze_bot,
    run_pytest_structural,
    import_bot_on_platform,
    run_pytest_behavioral
)

# Step by step control
success, analyzer = load_and_analyze_bot(config_path)
run_pytest_structural(config_path)
bot_id, version_id = import_bot_on_platform(config_path)
run_pytest_behavioral(bot_id, version_id, config_path)
```

### Direct Pytest Control
```bash
cd AIforce_coding
pytest tests/test_structural.py --bot-config=/path/to/config.json -vv
pytest tests/ -m behavioral --bot-id=8553 --current-version-id=8581 --bot-config=/path/to/config.json -v
```

---

## ✨ Summary

You have a complete, working, extensible testing framework for bots!

**Current Status**: Phase 1 & 2 ✅
- Structural validation tests (24 tests)
- Behavioral testing via API (33 tests)
- Full test pipeline orchestration
- Config-driven parametrization
- Auto-skip for missing features
- Comprehensive documentation

**Ready for**: Phase 3-4
- Advanced behavioral tests (LLM, HTTP, Script blocks)
- Coverage reporting and dashboards
- CI/CD integration

**Start testing**:
```bash
cd AIforce_coding/tests
# Edit pipeline.py with your config path
python3 pipeline.py
```

Enjoy! 🚀
