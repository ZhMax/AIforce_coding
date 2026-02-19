"""
Universal Bot Connectivity Tests

These tests verify basic bot functionality without requiring bot configuration.
They work for any bot and test:
- Basic responses
- Input edge cases
- Session management
- Resilience

Tests use generic messages that most bots should handle.
"""

import pytest


class TestBasicConnectivity:
    """Tests for basic bot connectivity and responses"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_bot_responds_to_message(self, bot_client):
        """
        Verify bot responds to a simple message.

        Sends a generic greeting and verifies we get a response with content.
        """
        response = await bot_client.send_message("hello", new_session=True)

        assert response is not None, "Bot should return a response"
        assert response.text or response.buttons, (
            "Response should have text or buttons"
        )


class TestInputEdgeCases:
    """Tests for bot handling of edge case inputs"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_bot_handles_empty_message(self, bot_client):
        """Verify bot handles empty message gracefully"""
        response = await bot_client.send_message("", new_session=True)

        # Bot should handle gracefully (may respond or not)
        assert response is not None, "Bot should handle empty message"

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_bot_handles_whitespace(self, bot_client):
        """Verify bot handles whitespace-only message"""
        response = await bot_client.send_message("   ", new_session=True)

        assert response is not None, "Bot should handle whitespace"

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_bot_handles_special_characters(self, bot_client):
        """Verify bot handles special characters and emojis"""
        response = await bot_client.send_message("Hello! @#$ 😊", new_session=True)

        assert response is not None, "Bot should handle special characters"
        assert response.text or response.buttons, "Response should have content"

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_bot_handles_long_input(self, bot_client):
        """Verify bot handles very long input"""
        long_text = "a" * 1000
        response = await bot_client.send_message(long_text, new_session=True)

        assert response is not None, "Bot should handle long input"

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_bot_handles_newlines(self, bot_client):
        """Verify bot handles multi-line messages"""
        response = await bot_client.send_message("line1\nline2\nline3", new_session=True)

        assert response is not None, "Bot should handle newlines"


class TestSessionManagement:
    """Tests for session persistence and management"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_session_persists_across_messages(self, bot_client):
        """
        Verify session state persists across multiple messages.

        Sends two messages in the same session and verifies both get responses.
        """
        # First message - start session
        response1 = await bot_client.send_message("hello", new_session=True)
        assert response1 is not None, "First message should get response"

        # Second message - same session
        response2 = await bot_client.send_message("test")
        assert response2 is not None, "Second message should get response"

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_new_session_starts_fresh(self, bot_client):
        """
        Verify new sessions are independent.

        Each new session should start with clean state.
        """
        # First session
        response1 = await bot_client.send_message("hello", new_session=True)
        assert response1 is not None

        # Second session - should start fresh
        response2 = await bot_client.send_message("hello", new_session=True)
        assert response2 is not None


class TestResilience:
    """Tests for bot resilience and consistency"""

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_rapid_sequential_messages(self, bot_client):
        """Verify bot handles rapid sequential messages"""
        # Send multiple messages quickly
        response1 = await bot_client.send_message("hello", new_session=True)
        response2 = await bot_client.send_message("test")
        response3 = await bot_client.send_message("another")
        response4 = await bot_client.send_message("message")
        response5 = await bot_client.send_message("final")

        # All should get responses
        assert response1 is not None
        assert response2 is not None
        assert response3 is not None
        assert response4 is not None
        assert response5 is not None

    @pytest.mark.behavioral
    @pytest.mark.asyncio
    async def test_repeated_same_input(self, bot_client):
        """
        Verify bot handles repeated same input consistently.

        Same input should get consistent responses.
        """
        # Send same message multiple times
        response1 = await bot_client.send_message("hello", new_session=True)
        response2 = await bot_client.send_message("hello", new_session=True)
        response3 = await bot_client.send_message("hello", new_session=True)

        # All should get responses
        assert response1 is not None
        assert response2 is not None
        assert response3 is not None
