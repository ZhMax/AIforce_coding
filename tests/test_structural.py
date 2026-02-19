"""
Tier 1: Structural Validation Tests

These tests validate bot configuration correctness without deploying.
Fast, run in milliseconds, work for any bot configuration.
"""

import re

import pytest


class TestNodeStructure:
    """Tests for node configuration"""

    @pytest.mark.structural
    def test_node_ids_are_unique(self, bot_config):
        """Verify node IDs are unique within scenario"""
        for s_idx, scenario in enumerate(bot_config["scenarios"]):
            node_ids = set()
            for n_idx, node in enumerate(scenario["nodes"]):
                node_id = node.get("id")
                assert node_id not in node_ids, (
                    f"Scenario {s_idx}: Duplicate node ID {node_id}"
                )
                node_ids.add(node_id)

    @pytest.mark.structural
    def test_block_ids_unique_in_node(self, bot_config):
        """Verify block IDs are unique within each node"""
        for s_idx, scenario in enumerate(bot_config["scenarios"]):
            for n_idx, node in enumerate(scenario["nodes"]):
                block_ids = set()
                for block in node.get("blocks", []):
                    block_id = block.get("id")
                    if block_id:
                        assert block_id not in block_ids, (
                            f"Scenario {s_idx}, Node {n_idx}: "
                            f"Duplicate block ID {block_id}"
                        )
                        block_ids.add(block_id)


class TestEntryEdgeValidation:
    """Tests for entry edge configuration"""

    @pytest.mark.structural
    def test_all_entry_edges_target_valid_nodes(self, bot_config, element_extractor):
        """Verify all entry edges point to valid nodes"""
        all_node_ids = element_extractor.get_all_node_ids()

        for s_idx, scenario in enumerate(bot_config["scenarios"]):
            for e_idx, edge in enumerate(scenario.get("entry_edges", [])):
                target = edge.get("target_node_id")
                assert target in all_node_ids, (
                    f"Scenario {s_idx}, Edge {e_idx}: "
                    f"Entry edge targets non-existent node: {target}"
                )

    @pytest.mark.structural
    def test_intent_edges_have_valid_threshold(self, bot_config):
        """Verify intent edges have threshold in valid range 0-1"""
        for s_idx, scenario in enumerate(bot_config["scenarios"]):
            for e_idx, edge in enumerate(scenario.get("entry_edges", [])):
                if edge.get("type") == "intent":
                    threshold = edge.get("threshold")
                    if threshold is not None:
                        assert 0 <= threshold <= 1, (
                            f"Scenario {s_idx}, Edge {e_idx}: "
                            f"Intent threshold must be 0-1, got {threshold}"
                        )

    @pytest.mark.structural
    def test_rule_edges_have_id(self, bot_config):
        """Verify rule edges have required 'id' field"""
        for s_idx, scenario in enumerate(bot_config["scenarios"]):
            for e_idx, edge in enumerate(scenario.get("entry_edges", [])):
                if edge.get("type") == "rule":
                    assert "id" in edge, (
                        f"Scenario {s_idx}, Edge {e_idx}: "
                        f"Rule edge must have 'id' field"
                    )


class TestNodeReferences:
    """Tests for node-to-node references"""

    @pytest.mark.structural
    def test_all_button_targets_exist(self, bot_config, element_extractor):
        """Verify all button block targets point to valid nodes"""
        all_node_ids = element_extractor.get_all_node_ids()

        for block in element_extractor.extract_blocks():
            if block.type == "buttons":
                for button in block.data.get("buttons", []):
                    target = button.get("target_node_id")
                    assert target in all_node_ids, (
                        f"Button block at {block.path}: "
                        f"Button targets non-existent node: {target}"
                    )

    @pytest.mark.structural
    def test_all_single_if_targets_exist(self, bot_config, element_extractor):
        """Verify single_if blocks target valid nodes"""
        all_node_ids = element_extractor.get_all_node_ids()

        for block in element_extractor.extract_blocks():
            if block.type == "single_if":
                target = block.data.get("target_node_id")
                if target:
                    assert target in all_node_ids, (
                        f"SingleIf block at {block.path}: "
                        f"Targets non-existent node: {target}"
                    )

    @pytest.mark.structural
    def test_all_extend_targets_exist(self, bot_config, element_extractor):
        """Verify extend blocks target valid scenarios"""
        all_scenario_ids = element_extractor.get_all_scenario_ids()

        for block in element_extractor.extract_blocks():
            if block.type == "extend":
                target_id = block.data.get("scenario_id")
                if target_id:
                    assert target_id in all_scenario_ids, (
                        f"Extend block at {block.path}: "
                        f"Targets non-existent scenario: {target_id}"
                    )


class TestRegexPatterns:
    """Tests for regex pattern validation"""

    @pytest.mark.structural
    def test_all_match_edges_have_valid_regex(self, bot_config):
        """Verify all match edges have valid regex patterns"""
        for s_idx, scenario in enumerate(bot_config["scenarios"]):
            for e_idx, edge in enumerate(scenario.get("entry_edges", [])):
                if edge.get("type") == "match":
                    pattern = edge.get("value", "")
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        pytest.fail(
                            f"Scenario {s_idx}, Edge {e_idx}: "
                            f"Invalid regex pattern '{pattern}' - {e}"
                        )


class TestBlockSemanticValidation:
    """Tests for semantic validation of block configurations"""

    @pytest.mark.structural
    def test_llm_blocks_have_system_and_user_message(self, element_extractor):
        """Verify LLM blocks have both system_message and user_message"""
        llm_blocks = element_extractor.extract_blocks_by_type("llm")

        for block in llm_blocks:
            assert "system_message" in block.data, (
                f"LLM block at {block.path} missing 'system_message'"
            )
            assert block.data.get("system_message"), (
                f"LLM block at {block.path} has empty 'system_message'"
            )
            assert "user_message" in block.data, (
                f"LLM block at {block.path} missing 'user_message'"
            )

    @pytest.mark.structural
    def test_agent_blocks_have_system_and_user_message(self, element_extractor):
        """Verify Agent blocks have both system_message and user_message"""
        agent_blocks = element_extractor.extract_blocks_by_type("agent")

        for block in agent_blocks:
            assert "system_message" in block.data, (
                f"Agent block at {block.path} missing 'system_message'"
            )
            assert block.data.get("system_message"), (
                f"Agent block at {block.path} has empty 'system_message'"
            )
            assert "user_message" in block.data, (
                f"Agent block at {block.path} missing 'user_message'"
            )

    @pytest.mark.structural
    def test_http_request_blocks_have_valid_method(self, element_extractor):
        """Verify HTTP request blocks have valid HTTP method"""
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH"}
        http_blocks = element_extractor.extract_blocks_by_type("http_request")

        for block in http_blocks:
            method = block.data.get("method", "").upper()
            assert method in valid_methods, (
                f"HTTP request block at {block.path}: "
                f"Invalid method '{method}'. Must be one of {valid_methods}"
            )

    @pytest.mark.structural
    def test_variables_blocks_have_valid_type(self, element_extractor):
        """Verify variables blocks have valid variable_type"""
        valid_types = {"constant", "python", "regexp", "regexp_map"}
        var_blocks = element_extractor.extract_blocks_by_type("variables")

        for block in var_blocks:
            var_type = block.data.get("variable_type")
            assert var_type in valid_types, (
                f"Variables block at {block.path}: "
                f"Invalid variable_type '{var_type}'. Must be one of {valid_types}"
            )

    @pytest.mark.structural
    def test_buttons_have_non_empty_titles(self, element_extractor):
        """Verify all buttons have non-empty titles"""
        buttons_blocks = element_extractor.extract_blocks_by_type("buttons")

        for block in buttons_blocks:
            buttons = block.data.get("buttons", [])
            for btn_idx, button in enumerate(buttons):
                title = button.get("title", "").strip()
                assert title, (
                    f"Buttons block at {block.path}, button {btn_idx}: "
                    f"Button title cannot be empty"
                )

    @pytest.mark.structural
    def test_dynamic_buttons_have_required_fields(self, element_extractor):
        """Verify dynamic buttons blocks have required fields"""
        dyn_blocks = element_extractor.extract_blocks_by_type("dynamic_buttons")

        for block in dyn_blocks:
            assert "source_variable_name" in block.data, (
                f"DynamicButtons block at {block.path} missing 'source_variable_name'"
            )
            assert "result_variable_name" in block.data, (
                f"DynamicButtons block at {block.path} missing 'result_variable_name'"
            )

    @pytest.mark.structural
    def test_single_if_blocks_have_expression(self, element_extractor):
        """Verify single_if blocks have non-empty expression"""
        if_blocks = element_extractor.extract_blocks_by_type("single_if")

        for block in if_blocks:
            expression = block.data.get("expression", "").strip()
            assert expression, f"SingleIf block at {block.path} has empty 'expression'"

class TestBotConfigValidation:
    """Tests for bot configuration semantic validation"""

    @pytest.mark.structural
    def test_bot_name_length_valid(self, bot_config):
        """Verify bot_name is 4-64 characters"""
        bot_name = bot_config.get("bot_name", "")
        assert 4 <= len(bot_name) <= 64, (
            f"bot_name must be 4-64 characters, got {len(bot_name)}"
        )

    @pytest.mark.structural
    def test_no_match_stub_answer_length(self, bot_config):
        """Verify no_match_stub_answer is at least 4 characters"""
        stub = bot_config.get("no_match_stub_answer", "")
        assert len(stub) >= 4, (
            f"no_match_stub_answer must be at least 4 characters, got {len(stub)}"
        )


class TestScenarioConsistency:
    """Tests for cross-scenario consistency"""

    @pytest.mark.structural
    def test_scenario_ids_are_unique(self, bot_config):
        """Verify scenario IDs are unique"""
        scenario_ids = set()

        for scenario in bot_config.get("scenarios", []):
            if "id" in scenario:
                scenario_id = scenario["id"]
                assert scenario_id not in scenario_ids, (
                    f"Duplicate scenario ID: {scenario_id}"
                )
                scenario_ids.add(scenario_id)

    @pytest.mark.structural
    def test_scenario_slugs_are_unique(self, element_extractor):
        """Verify scenario slugs are unique"""
        scenarios = element_extractor.extract_scenarios()
        slugs = set()

        for scenario in scenarios:
            assert scenario.slug not in slugs, (
                f"Duplicate scenario slug: {scenario.slug}"
            )
            slugs.add(scenario.slug)
