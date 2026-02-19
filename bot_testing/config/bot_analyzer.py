from typing import Any, Dict, List, Optional

from .element_types import BotInfo
from .extractor import ElementExtractor
from .loader import ConfigLoader
from .validator import ConfigValidator


class BotAnalyzer:
    """Analyze bot configuration and extract comprehensive statistics"""

    def __init__(self, config_path: str, schema_path: str):
        """
        Initialize analyzer with paths to configuration and schema files

        Args:
            config_path: Path to bot configuration file
            schema_path: Path to validation schema file
        """
        self.config_path = config_path
        self.loader = ConfigLoader()
        self.validator = ConfigValidator(schema_path)
        self.extractor = ElementExtractor()

        self.config: Optional[Dict[str, Any]] = None
        self.bot_info: Optional[BotInfo] = None
        self._is_loaded = False

    def load_and_validate(self) -> None:
        """Load configuration, validate it, and generate summary if valid"""
        self.config = self.loader.load(self.config_path)
        is_valid, errors = self.validator.validate(self.config)

        if is_valid:
            print("\n✓ Validation passed!")
            self.extractor.set_config_attr(self.config)
            self.bot_info = self.get_summary()
            self._is_loaded = True
            SummaryFormatter.print_summary(self.bot_info)

        else:
            print("\n✗ Validation failed!")
            for error in errors:
                print(f"  • {error}")

    def get_summary(self) -> BotInfo:
        """
        Get comprehensive bot configuration summary

        Returns:
            BotInfo object with complete configuration analysis
        """
        scenarios = self.extractor.extract_scenarios()
        blocks = self.extractor.extract_blocks()
        edges = self.extractor.extract_entry_edges()

        # Count blocks by type
        blocks_by_type = {}
        for block in blocks:
            blocks_by_type.setdefault(block.type, 0)
            blocks_by_type[block.type] += 1

        # Count edges by type
        edges_by_type = {}
        for edge in edges:
            edges_by_type.setdefault(edge.type, 0)
            edges_by_type[edge.type] += 1

        # Extract LLM blocks information
        llm_blocks = [
            {
                "scenario": b.scenario_slug,
                "model": b.data.get("model", {}).get("model_name", "unknown"),
                "result_variable": b.data.get("result_variable_name"),
            }
            for b in self.extractor.extract_blocks_by_type("llm")
        ]

        # Create and populate BotInfo
        config_attrs = self.extractor.config_attrs
        bot_info = BotInfo(
            bot_name=config_attrs.get("bot_name"),
            bot_id=config_attrs.get("bot_id"),
            version_id=config_attrs.get("version_id"),
            no_match_stub_answer=config_attrs.get("no_match_stub_answer"),
            request_ttl_in_seconds=config_attrs.get("request_ttl_in_seconds"),
            scenarios=scenarios,
            blocks_by_type=blocks_by_type,
            edges_by_type=edges_by_type,
            llm_blocks=llm_blocks,
            extend_blocks_count=len(self.extractor.extract_blocks_by_type("extend")),
            button_blocks_count=len(self.extractor.extract_blocks_by_type("buttons")),
        )

        return bot_info


class SummaryFormatter:
    """Format and print bot summary information"""

    SEPARATOR_WIDTH = 60

    @staticmethod
    def print_summary(bot_info: BotInfo) -> None:
        """
        Print formatted summary to console

        Args:
            bot_info: BotInfo object containing analyzed configuration data
        """
        if not bot_info:
            print("No summary available.")
            return

        SummaryFormatter._print_header(bot_info.bot_name)
        SummaryFormatter._print_overview(bot_info)
        SummaryFormatter._print_blocks_by_type(bot_info.blocks_by_type)
        SummaryFormatter._print_edges_by_type(bot_info.edges_by_type)
        SummaryFormatter._print_llm_blocks(bot_info.llm_blocks)
        SummaryFormatter._print_special_blocks(
            bot_info.extend_blocks_count, bot_info.button_blocks_count
        )
        SummaryFormatter._print_scenarios(bot_info.scenarios)

    @staticmethod
    def _print_header(bot_name: str) -> None:
        """Print summary header with bot name"""
        separator = "=" * SummaryFormatter.SEPARATOR_WIDTH
        print(f"\n{separator}")
        print(f"  Bot: {bot_name}")
        print(f"{separator}\n")

    @staticmethod
    def _print_overview(bot_info: BotInfo) -> None:
        """Print high-level configuration overview"""
        print("Configuration Summary:")
        print(f"  Scenarios: {bot_info.scenarios_count}")
        print(f"  Nodes: {bot_info.nodes_count}")
        print(f"  Blocks: {bot_info.blocks_count}")
        print(f"  Entry Edges: {bot_info.edges_count}\n")

    @staticmethod
    def _print_blocks_by_type(blocks_by_type: Dict[str, int]) -> None:
        """Print blocks grouped by type"""
        print("Blocks by Type:")
        for block_type in sorted(blocks_by_type.keys()):
            count = blocks_by_type[block_type]
            print(f"  • {block_type}: {count}")
        print()

    @staticmethod
    def _print_edges_by_type(edges_by_type: Dict[str, int]) -> None:
        """Print entry edges grouped by type"""
        print("Entry Edges by Type:")
        for edge_type in sorted(edges_by_type.keys()):
            count = edges_by_type[edge_type]
            print(f"  • {edge_type}: {count}")
        print()

    @staticmethod
    def _print_llm_blocks(llm_blocks: List[Dict[str, Any]]) -> None:
        """Print LLM blocks information"""
        if llm_blocks:
            print(f"LLM Blocks ({len(llm_blocks)} found):")
            for llm in llm_blocks:
                print(f"  • Model: {llm['model']}, Result: {llm['result_variable']}")
            print()

    @staticmethod
    def _print_special_blocks(extend_count: int, button_count: int) -> None:
        """Print special blocks counts"""
        print("Special Blocks:")
        print(f"  • Extend blocks: {extend_count}")
        print(f"  • Button blocks: {button_count}\n")

    @staticmethod
    def _print_scenarios(scenarios: List) -> None:
        """Print detailed scenario information"""
        print("Scenarios:")
        for scenario in scenarios:
            print(
                f"  • {scenario.slug}: "
                f"{len(scenario.nodes)} nodes, "
                f"{len(scenario.entry_edges)} entry edges"
            )
        print()
