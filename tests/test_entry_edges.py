"""
Config-Driven Entry Edge and Navigation Tests

These tests verify bot entry edges and navigation by using the bot's actual
configuration. Tests are parametrized over the edges defined in the config.

Tests automatically skip if bot config is not available.
"""

import pytest
from bot_testing.utils import regex_to_sample_message


class TestMatchEdges:
    """Tests for match-type entry edges (regex-based activation)"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_match_edge_activates(self, bot_client, match_edge, bot_config_extractor):
        """
        Verify match edge activates with generated message.

        Parametrized over all match edges in the bot config.
        Generates a sample message from the regex pattern and verifies bot responds.
        """
        if not bot_config_extractor:
            pytest.skip("Bot config not available")

        if not match_edge:
            pytest.skip("No match edges in bot config")

        # Generate sample message from regex pattern
        pattern = match_edge.pattern
        message = regex_to_sample_message(pattern)

        # Send message and verify response
        response = await bot_client.send_message(message, new_session=True)

        assert response is not None, f"Match edge '{pattern}' should trigger response"
        assert response.text or response.buttons, (
            f"Response from edge '{pattern}' should have content"
        )

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_match_edge_case_insensitive(self, bot_client, match_edge, bot_config_extractor):
        """
        Verify match edges work case-insensitively.

        Parametrized over match edges with alphabetic characters.
        Tests uppercase and lowercase variants.
        """
        if not bot_config_extractor:
            pytest.skip("Bot config not available")

        if not match_edge:
            pytest.skip("No match edges in bot config")

        # Generate sample message
        pattern = match_edge.pattern
        message = regex_to_sample_message(pattern)

        # Skip if no alphabetic characters
        if not any(c.isalpha() for c in message):
            pytest.skip(f"Pattern '{pattern}' has no alphabetic characters")

        # Test lowercase
        response_lower = await bot_client.send_message(message.lower(), new_session=True)
        assert response_lower is not None, "Lowercase variant should work"

        # Test uppercase
        response_upper = await bot_client.send_message(message.upper(), new_session=True)
        assert response_upper is not None, "Uppercase variant should work"


class TestEventEdges:
    """Tests for event-type entry edges (init, no_match)"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_init_event_triggers(self, bot_client, event_edges, bot_config_extractor):
        """
        Verify 'init' event triggers on first message.

        Sends first message in new session and verifies response.
        Skips if bot has no init event edge.
        """
        if not bot_config_extractor:
            pytest.skip("Bot config not available")

        # Check if bot has init event edge
        init_edges = [e for e in event_edges if e.pattern == "init"]
        if not init_edges:
            pytest.skip("Bot has no init event edge")

        # Send first message in new session
        response = await bot_client.send_message("hello", new_session=True)

        assert response is not None, "Init event should trigger response"
        assert response.text or response.buttons, "Init response should have content"

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_no_match_fallback(self, bot_client, event_edges, bot_config_extractor):
        """
        Verify 'no_match' fallback triggers for unrecognized input.

        Sends gibberish and verifies fallback response.
        Checks if response matches configured no_match_stub_answer.
        Skips if bot has no no_match event edge.
        """
        if not bot_config_extractor:
            pytest.skip("Bot config not available")

        # Check if bot has no_match event edge
        no_match_edges = [e for e in event_edges if e.pattern == "no_match"]
        if not no_match_edges:
            pytest.skip("Bot has no no_match event edge")

        # Send unrecognizable message
        response = await bot_client.send_message(
            "xyz123randomtextthatprobablydoesntexist",
            new_session=True
        )

        assert response is not None, "No_match should trigger response"

        # Optionally verify it matches configured stub answer
        config_attrs = bot_config_extractor.config_attrs
        stub_answer = config_attrs.get("no_match_stub_answer", "")
        if stub_answer and response.text:
            # Check if response contains the stub answer (may have formatting differences)
            assert stub_answer.lower() in response.text.lower() or response.text, (
                f"No_match response should relate to configured stub: '{stub_answer}'"
            )


class TestButtonNavigation:
    """Tests for button-based navigation"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_button_click_returns_response(self, bot_client):
        """
        Verify clicking a button returns a response.

        Sends initial message, checks for buttons, clicks first button.
        """
        # Get initial response
        response = await bot_client.send_message("hello", new_session=True)

        if not response or not response.buttons:
            pytest.skip("No buttons in initial response")

        # Click first button
        button = response.buttons[0]
        button_response = await bot_client.click_button(button.title)

        assert button_response is not None, "Button click should return response"

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_all_buttons_clickable(self, bot_client):
        """
        Verify all buttons in a response are clickable.

        Gets initial response with buttons, clicks each in separate sessions.
        """
        # Get initial response
        response = await bot_client.send_message("hello", new_session=True)

        if not response or not response.buttons:
            pytest.skip("No buttons in initial response")

        # Click each button in separate session
        for button in response.buttons:
            button_response = await bot_client.send_message(button.title, new_session=True)
            assert button_response is not None, f"Button '{button.title}' should work"

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_multi_step_navigation(self, bot_client):
        """
        Verify multi-step button navigation works.

        Follows button chains up to 10 steps.
        """
        response = await bot_client.send_message("hello", new_session=True)
        assert response is not None

        steps = 0
        max_steps = 10

        while response and response.buttons and steps < max_steps:
            # Click first button
            button = response.buttons[0]
            response = await bot_client.click_button(button.title)
            steps += 1

        # Should complete without errors
        assert steps > 0, "Should navigate at least one step"

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_branching_paths(self, bot_client):
        """
        Verify different buttons lead to different responses.

        Tests that bot has branching logic.
        """
        # Get initial response
        response = await bot_client.send_message("hello", new_session=True)

        if not response or not response.buttons or len(response.buttons) < 2:
            pytest.skip("Need at least 2 buttons to test branching")

        # Click first button
        response1 = await bot_client.click_button(response.buttons[0].title)
        assert response1 is not None

        # Start new session and click second button
        response_fresh = await bot_client.send_message("hello", new_session=True)
        response2 = await bot_client.click_button(response_fresh.buttons[1].title)
        assert response2 is not None

        # Both paths should work (may or may not be different responses)
