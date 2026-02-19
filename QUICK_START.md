# Quick Start - Bot Testing Framework

## Installation (1 minute)

```bash
cd AIforce_coding
pip install -r requirements.txt
```

## Run Tests for Your Bot

### Recommended: Full Test Pipeline

**File**: `tests/pipeline.py`

This runs the complete testing workflow (structural + behavioral):

```bash
cd AIforce_coding/tests
# Edit pipeline.py main() with your config path:
#   config_path = "/path/to/your/bot-config.json"
python3 pipeline.py
```

**What it runs**:
1. ✓ Config analysis and validation
2. ✓ Structural tests (24 tests)
3. ✓ Bot import on platform via API
4. ✓ Behavioral tests (33 tests)
5. ✓ Cleanup (removes bot from platform)

### Alternative: Manual Test Control

**Structural Tests Only** (no deployment required):
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

**Individual Test Files**:
```bash
# Universal connectivity tests
pytest tests/test_connectivity.py -v --bot-id=8553 --current-version-id=8581

# Config-driven entry edge tests
pytest tests/test_entry_edges.py -v --bot-id=8553 --current-version-id=8581 --bot-config=/path/to/config.json

# Block-type-specific tests
pytest tests/test_blocks.py -v --bot-id=8553 --current-version-id=8581 --bot-config=/path/to/config.json
```

## What You'll See

✅ **Configuration loaded**
✅ **24 structural tests run**
✅ **Results**: PASSED or FAILED with details

## Test Different Bot

Edit `tests/pipeline.py` and change the config path:
```python
config_path = "/path/to/bot-97-v671.json"
```

Or use direct pytest:
```bash
pytest tests/test_structural.py --bot-config=/path/to/bot-97-v671.json -v
```

## What Gets Tested

**Structural Tests** (Phase 1 - no API needed):
- ✓ Bot structure and required fields
- ✓ All 6 scenarios (bot-8553) properly defined
- ✓ Node and block definitions
- ✓ Button navigation targets
- ✓ Extend block scenario references
- ✓ LLM block configuration
- ✓ Regex pattern validation
- ✓ Variable usage in templates
- ✓ Data consistency

**Behavioral Tests** (Phase 2 - requires deployed bot):
- ✓ Bot connectivity and response handling
- ✓ Session persistence across messages
- ✓ Entry edge activation (match edges, init/no_match events)
- ✓ Button navigation and multi-step flows
- ✓ Block-type-specific behavior (auto-skip tests for missing blocks)

## Next Steps

- **Detailed guide**: See `README.md`
- **Examples**: See `examples/README.md`
- **Full reference**: See `examples/USAGE.md`

## File Structure

```
AIforce_coding/
├── QUICK_START.md              # This file
├── README.md                    # Full documentation
├── requirements.txt             # Dependencies
├── pytest.ini                   # Pytest config
│
├── bot_testing/                 # Framework package
│   ├── config/                  # Config loading
│   ├── execution/               # API client (Phase 2)
│   └── coverage/                # Coverage tracking (Phase 4)
│
├── tests/                       # Test suite
│   ├── conftest.py             # Fixtures
│   └── test_structural.py      # Structural tests
│
└── examples/                    # Example scripts
    ├── run_bot_8553_tests.sh    # Bash runner
    ├── run_bot_8553_tests.py    # Python runner with analysis
    ├── run_tests_api.py         # Programmatic API
    ├── README.md                # Examples guide
    └── USAGE.md                 # Detailed reference
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `pytest: command not found` | Run `pip install -r requirements.txt` |
| `Config file not found` | Check `BOT_CONFIG_PATH` is correct |
| `ModuleNotFoundError` | Make sure you're in `AIforce_coding` directory |
| Permission denied `.sh` | Run `chmod +x examples/run_bot_8553_tests.sh` |

## Architecture Overview

```
User → Script/Pytest → Fixtures → Element Extractor → Test Assertions
                                        ↓
                                   Bot Config JSON
                                   (bot-8553.json)
```

The same test code works for any bot - configuration is injected at runtime!

## Quick Reference Commands

```bash
# Full pipeline (recommended)
cd AIforce_coding/tests
python3 pipeline.py

# Structural tests only
cd AIforce_coding
pytest tests/test_structural.py --bot-config=/path/to/config.json -v

# Behavioral tests only (requires deployed bot)
pytest tests/ -m behavioral \
  --bot-id=8553 \
  --current-version-id=8581 \
  --bot-config=/path/to/config.json -v

# Test specific class
pytest tests/test_structural.py::TestBotConfiguration --bot-config=/path/to/config.json -v

# Test with coverage
pytest tests/test_structural.py --bot-config=/path/to/config.json --cov=bot_testing

# Test all bots (structural only)
for bot in ../mws_api/test_api/bot-*.json; do
    pytest tests/test_structural.py --bot-config=$bot -v
done
```

## Expected Output

```
tests/test_structural.py::TestBotConfiguration::test_config_has_scenarios PASSED
tests/test_structural.py::TestBotConfiguration::test_bot_has_required_fields PASSED
tests/test_structural.py::TestScenarioStructure::test_all_scenarios_have_required_fields PASSED
...
========================== 24 passed in 0.42s ==========================
```

## Key Concepts

- **Structural Tests**: Validate bot JSON configuration (no API calls)
- **Generic Tests**: Same test code works for any bot
- **Parametrization**: Bot config injected via pytest fixtures
- **Element Extractor**: Parses bot structure into testable elements
- **No Deployment**: Tests run without deploying bot to API

## Coming Soon (Phase 2-4)

- Behavioral tests (send messages to bot)
- LLM and HTTP block execution tests
- Coverage tracking and reporting
- CLI tool for easy test running

## Support

- Check `examples/USAGE.md` for detailed troubleshooting
- See `README.md` for full documentation
- Review test code in `tests/test_structural.py` for examples

---

**Ready to test? Run:**
```bash
cd AIforce_coding/tests
# Edit pipeline.py with your config path, then:
python3 pipeline.py
```

Or jump to `README.md` for detailed documentation!
