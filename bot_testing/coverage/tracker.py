"""
Coverage tracker - tracks which bot elements are tested
"""

from collections import defaultdict
from typing import Any, Dict, List, Set


class CoverageTracker:
    """Tracks test coverage of bot configuration elements"""

    def __init__(self):
        """Initialize coverage tracker"""
        self.tested_elements: Set[str] = set()
        self.test_results: Dict[str, Any] = defaultdict(list)

    def mark_block_tested(self, block_path: str, passed: bool = True) -> None:
        """
        Mark a block as tested

        Args:
            block_path: Path to the block (e.g., "scenarios[0].nodes[1].blocks[0]")
            passed: Whether the test passed
        """
        key = f"block:{block_path}"
        self.tested_elements.add(key)
        self.test_results[key].append({"passed": passed})

    def mark_edge_tested(self, edge_path: str, passed: bool = True) -> None:
        """
        Mark an entry edge as tested

        Args:
            edge_path: Path to the edge
            passed: Whether the test passed
        """
        key = f"edge:{edge_path}"
        self.tested_elements.add(key)
        self.test_results[key].append({"passed": passed})

    def mark_node_tested(self, node_path: str, passed: bool = True) -> None:
        """
        Mark a node as tested

        Args:
            node_path: Path to the node
            passed: Whether the test passed
        """
        key = f"node:{node_path}"
        self.tested_elements.add(key)
        self.test_results[key].append({"passed": passed})

    def get_coverage_summary(self, total_elements: int) -> Dict[str, Any]:
        """
        Get coverage summary

        Args:
            total_elements: Total number of elements in configuration

        Returns:
            Dictionary with coverage statistics
        """
        tested = len(self.tested_elements)
        coverage = (tested / total_elements * 100) if total_elements > 0 else 0

        return {
            "total_elements": total_elements,
            "tested_elements": tested,
            "coverage_percent": round(coverage, 1),
            "untested_elements": total_elements - tested,
        }
