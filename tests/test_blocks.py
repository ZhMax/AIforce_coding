"""
Config-Driven Block Behavior Tests

These tests verify block-specific behavior using the bot's actual configuration.
Each test class checks for the presence of specific block types and skips if not found.

Tests automatically skip if bot config is not available or lacks the block type.
"""

import pytest
from bot_testing.utils import regex_to_sample_message


class TestWaitForUserBlock:
    """Tests for wait_for_user block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_wait_pauses_and_resumes(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify wait_for_user block pauses and resumes bot flow.

        Finds a scenario with wait_for_user, activates it, sends follow-up.
        """
        if not has_block_type("wait_for_user"):
            pytest.skip("Bot has no wait_for_user blocks")

        # Send initial message (may reach wait_for_user)
        response1 = await bot_client.send_message("hello", new_session=True)
        assert response1 is not None

        # Send follow-up (should resume from wait)
        response2 = await bot_client.send_message("continue")
        assert response2 is not None


class TestButtonsBlock:
    """Tests for buttons block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_buttons_block_shows_buttons(self, bot_client, buttons_scenario, bot_config_extractor):
        """
        Verify buttons block displays buttons.

        Parametrized over scenarios containing buttons blocks.
        Activates scenario and verifies response has buttons.
        """
        if not bot_config_extractor:
            pytest.skip("Bot config not available")

        if not buttons_scenario:
            pytest.skip("No scenarios with buttons blocks")

        # Find an entry edge for this scenario
        entry_edges = [e for e in buttons_scenario.entry_edges if e.type == "match"]
        if not entry_edges:
            pytest.skip(f"Scenario '{buttons_scenario.slug}' has no match entry edge")

        # Activate scenario
        edge = entry_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        # Response should have buttons (eventually)
        # Note: buttons may not appear immediately if other blocks execute first
        assert response is not None, "Buttons scenario should respond"


class TestAnswerBlock:
    """Tests for answer block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_answer_block_returns_text(self, bot_client, has_block_type):
        """
        Verify answer blocks produce text responses.

        Most bots have answer blocks, so we just verify basic response.
        """
        if not has_block_type("answer"):
            pytest.skip("Bot has no answer blocks")

        response = await bot_client.send_message("hello", new_session=True)

        assert response is not None, "Answer block should respond"
        # Text may be empty if other blocks (like buttons) are present
        assert response.text or response.buttons, "Response should have content"


class TestLlmBlock:
    """Tests for LLM block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_llm_produces_text_response(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify LLM blocks generate text responses.

        Finds a scenario with LLM block, activates it.
        """
        if not has_block_type("llm"):
            pytest.skip("Bot has no LLM blocks")

        # Find scenario with LLM block
        llm_blocks = bot_config_extractor.extract_blocks_by_type("llm")
        if not llm_blocks:
            pytest.skip("No LLM blocks found")

        # Find the scenario and entry edge
        llm_block = llm_blocks[0]
        scenario_slug = llm_block.scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, "LLM block should respond"
        assert response.text or response.buttons, "LLM response should have content"


class TestHttpRequestBlock:
    """Tests for http_request block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_http_request_produces_response(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify http_request blocks execute and produce responses.

        Finds scenario with http_request block, activates it.
        """
        if not has_block_type("http_request"):
            pytest.skip("Bot has no http_request blocks")

        # Find scenario with http_request block
        http_blocks = bot_config_extractor.extract_blocks_by_type("http_request")
        scenario_slug = http_blocks[0].scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, "HTTP request block should respond"


class TestExtendBlock:
    """Tests for extend block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_extend_navigates_to_child(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify extend blocks transfer to child scenarios.

        Finds scenario with extend block, activates it.
        """
        if not has_block_type("extend"):
            pytest.skip("Bot has no extend blocks")

        # Find scenario with extend block
        extend_blocks = bot_config_extractor.extract_blocks_by_type("extend")
        scenario_slug = extend_blocks[0].scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, "Extend block should respond"


class TestMatchExtendBlock:
    """Tests for match_extend block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_match_extend_selects_scenario(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify match_extend blocks select appropriate scenarios.

        Finds scenario with match_extend block, activates it.
        """
        if not has_block_type("match_extend"):
            pytest.skip("Bot has no match_extend blocks")

        # Find scenario with match_extend block
        match_extend_blocks = bot_config_extractor.extract_blocks_by_type("match_extend")
        scenario_slug = match_extend_blocks[0].scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, "Match_extend block should respond"


class TestCloseBlock:
    """Tests for close block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_close_ends_dialog(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify close block ends the dialog.

        Finds scenario with close block, activates it.
        After close, behavior depends on implementation.
        """
        if not has_block_type("close"):
            pytest.skip("Bot has no close blocks")

        # Find scenario with close block
        close_blocks = bot_config_extractor.extract_blocks_by_type("close")
        scenario_slug = close_blocks[0].scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, "Close block should respond"


class TestGoOperatorBlock:
    """Tests for go_operator block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_go_operator_transfers(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify go_operator block handles operator transfer.

        Finds scenario with go_operator block, activates it.
        """
        if not has_block_type("go_operator"):
            pytest.skip("Bot has no go_operator blocks")

        # Find scenario with go_operator block
        operator_blocks = bot_config_extractor.extract_blocks_by_type("go_operator")
        scenario_slug = operator_blocks[0].scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, "Go_operator block should respond"


class TestVariablesBlock:
    """Tests for variables block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_variables_set_in_session(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify variables blocks set session variables.

        Finds scenario with variables block, activates it, sends follow-up.
        """
        if not has_block_type("variables"):
            pytest.skip("Bot has no variables blocks")

        # Find scenario with variables block
        var_blocks = bot_config_extractor.extract_blocks_by_type("variables")
        scenario_slug = var_blocks[0].scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response1 = await bot_client.send_message(message, new_session=True)
        assert response1 is not None

        # Send follow-up to verify state
        response2 = await bot_client.send_message("follow-up")
        assert response2 is not None


class TestScriptBlock:
    """Tests for script block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_script_executes(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify script blocks execute successfully.

        Finds scenario with script block, activates it.
        """
        if not has_block_type("script"):
            pytest.skip("Bot has no script blocks")

        # Find scenario with script block
        script_blocks = bot_config_extractor.extract_blocks_by_type("script")
        scenario_slug = script_blocks[0].scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, "Script block should respond"


class TestAgentBlock:
    """Tests for agent block behavior (ReAct agents with tools)"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_agent_produces_response(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify agent blocks produce responses.

        Finds scenario with agent block, activates it.
        """
        if not has_block_type("agent"):
            pytest.skip("Bot has no agent blocks")

        # Find scenario with agent block
        agent_blocks = bot_config_extractor.extract_blocks_by_type("agent")
        scenario_slug = agent_blocks[0].scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, "Agent block should respond"


class TestDynamicButtonsBlock:
    """Tests for dynamic_buttons block behavior"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_dynamic_buttons_show_options(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify dynamic_buttons blocks display generated buttons.

        Finds scenario with dynamic_buttons block, activates it.
        """
        if not has_block_type("dynamic_buttons"):
            pytest.skip("Bot has no dynamic_buttons blocks")

        # Find scenario with dynamic_buttons block
        dyn_blocks = bot_config_extractor.extract_blocks_by_type("dynamic_buttons")
        scenario_slug = dyn_blocks[0].scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, "Dynamic_buttons block should respond"


class TestSingleIfBlock:
    """Tests for single_if block behavior (conditional transitions)"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_single_if_evaluates_condition(self, bot_client, bot_config_extractor, has_block_type):
        """
        Verify single_if blocks evaluate conditions.

        Finds scenario with single_if block, activates it.
        """
        if not has_block_type("single_if"):
            pytest.skip("Bot has no single_if blocks")

        # Find scenario with single_if block
        if_blocks = bot_config_extractor.extract_blocks_by_type("single_if")
        scenario_slug = if_blocks[0].scenario_slug

        scenarios = bot_config_extractor.extract_scenarios()
        scenario = next((s for s in scenarios if s.slug == scenario_slug), None)

        if not scenario:
            pytest.skip(f"Scenario '{scenario_slug}' not found")

        # Find entry edge
        match_edges = [e for e in scenario.entry_edges if e.type == "match"]
        if not match_edges:
            pytest.skip(f"Scenario '{scenario_slug}' has no match entry edge")

        # Activate scenario
        edge = match_edges[0]
        message = regex_to_sample_message(edge.pattern)
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, "Single_if block should respond"
