"""
Bot configuration element extractor
Extracts blocks, edges, nodes, and scenarios from bot configuration
"""

from typing import Any, Dict, List, Optional

from .element_types import BlockInfo, EntryEdgeInfo, NodeInfo, ScenarioInfo


class ElementExtractor:
    """Extracts testable elements from bot configuration"""

    def __init__(self):
        self.config_attrs: Optional[Dict[str, Any]] = None

    @staticmethod
    def extract_bot_attributes(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract bot attributes from nested data structure if present

        Handles both formats:
        - Raw: {"scenarios": [...], "bot_name": "...", ...}
        - Exported: {"data": {"attributes": {...}}}
        """
        if "data" in config and "attributes" in config.get("data", {}):
            return config["data"]["attributes"]
        return config

    def set_config_attr(self, config: Dict[str, Any]):
        self.config_attrs = ElementExtractor.extract_bot_attributes(config)

    def extract_blocks(self) -> List[BlockInfo]:
        """
        Extract all blocks from all scenarios

        Returns:
            List of BlockInfo objects for all blocks in the bot
        """

        blocks = []

        for s_idx, scenario in enumerate(self.config_attrs.get("scenarios", [])):
            scenario_slug = scenario.get("slug", scenario.get("name", ""))
            scenario_name = scenario.get("name", "")

            for node in scenario.get("nodes", []):
                node_id = node.get("id", "")
                node_name = node.get("name", "")

                for b_idx, block in enumerate(node.get("blocks", [])):
                    block_info = BlockInfo(
                        path=f"scenarios[{s_idx}].nodes[{node_id}].blocks[{b_idx}]",
                        type=block.get("type", "unknown"),
                        data=block,
                        scenario_slug=scenario_slug,
                        scenario_name=scenario_name,
                        node_id=node_id,
                        node_name=node_name,
                        block_id=block.get("id", f"block_{b_idx}"),
                    )
                    blocks.append(block_info)

        return blocks

    def extract_blocks_by_type(self, block_type: str) -> List[BlockInfo]:
        """
        Extract all blocks of a specific type

        Args:
            block_type: Type of block to extract (e.g., "llm", "answer", "buttons")

        Returns:
            List of BlockInfo objects matching the type
        """
        return [b for b in self.extract_blocks() if b.type == block_type]

    def extract_entry_edges(self) -> List[EntryEdgeInfo]:
        """
        Extract all entry edges from all scenarios

        Returns:
            List of EntryEdgeInfo objects for all entry edges
        """

        edges = []

        for s_idx, scenario in enumerate(self.config_attrs.get("scenarios", [])):
            scenario_slug = scenario.get("slug", scenario.get("name", ""))
            scenario_name = scenario.get("name", "")

            for e_idx, edge in enumerate(scenario.get("entry_edges", [])):
                edge_info = EntryEdgeInfo(
                    path=f"scenarios[{s_idx}].entry_edges[{e_idx}]",
                    type=edge.get("type", "unknown"),
                    pattern=edge.get("value", ""),
                    target_node_id=edge.get("target_node_id", ""),
                    scenario_slug=scenario_slug,
                    scenario_name=scenario_name,
                    edge_id=edge.get("id"),
                    name=edge.get("name"),
                )
                edges.append(edge_info)

        return edges

    def extract_entry_edges_by_type(self, edge_type: str) -> List[EntryEdgeInfo]:
        """
        Extract all entry edges of a specific type

        Args:
            edge_type: Type of edge (e.g., "match", "event", "manual")

        Returns:
            List of EntryEdgeInfo objects matching the type
        """
        return [e for e in self.extract_entry_edges() if e.type == edge_type]

    def extract_nodes(self) -> List[NodeInfo]:
        """
        Extract all nodes from all scenarios

        Returns:
            List of NodeInfo objects for all nodes
        """

        nodes = []

        for s_idx, scenario in enumerate(self.config_attrs.get("scenarios", [])):
            scenario_slug = scenario.get("slug", scenario.get("name", ""))
            scenario_name = scenario.get("name", "")

            for n_idx, node in enumerate(scenario.get("nodes", [])):
                # Extract blocks for this node
                blocks = self.extract_blocks()
                node_blocks = [b for b in blocks if b.node_id == node.get("id")]

                node_info = NodeInfo(
                    path=f"scenarios[{s_idx}].nodes[{n_idx}]",
                    node_id=node.get("id", ""),
                    name=node.get("name", ""),
                    scenario_slug=scenario_slug,
                    scenario_name=scenario_name,
                    blocks=node_blocks,
                    next_node_id=node.get("next_node_id"),
                )
                nodes.append(node_info)

        return nodes

    def extract_scenarios(self) -> List[ScenarioInfo]:
        """
        Extract all scenarios

        Returns:
            List of ScenarioInfo objects
        """

        scenarios = []

        for s_idx, scenario in enumerate(self.config_attrs.get("scenarios", [])):
            slug = scenario.get("slug", scenario.get("name", ""))
            name = scenario.get("name", "")

            # Extract entry edges for this scenario
            all_edges = self.extract_entry_edges()
            scenario_edges = [e for e in all_edges if e.scenario_slug == slug]

            # Extract nodes for this scenario
            all_nodes = self.extract_nodes()
            scenario_nodes = [n for n in all_nodes if n.scenario_slug == slug]

            scenario_info = ScenarioInfo(
                path=f"scenarios[{s_idx}]",
                scenario_id=scenario.get("id"),
                name=name,
                slug=slug,
                parent_scenario_id=scenario.get("parent_scenario_id"),
                entry_edges=scenario_edges,
                nodes=scenario_nodes,
            )
            scenarios.append(scenario_info)

        return scenarios

    def get_all_node_ids(self) -> set:
        """
        Get all node IDs in the configuration

        Returns:
            Set of all node IDs
        """

        node_ids = set()
        for scenario in self.config_attrs.get("scenarios", []):
            for node in scenario.get("nodes", []):
                node_ids.add(node.get("id", ""))
        return node_ids

    def get_all_scenario_ids(self) -> set:
        """
        Get all scenario IDs in the configuration

        Returns:
            Set of all scenario IDs
        """

        return {
            s.get("id") for s in self.config_attrs.get("scenarios", []) if "id" in s
        }

    def find_block_by_id(self, block_id: str) -> Optional[BlockInfo]:
        """
        Find a block by its ID

        Args:
            block_id: Block ID to search for

        Returns:
            BlockInfo if found, None otherwise
        """
        for block in self.extract_blocks():
            if block.block_id == block_id:
                return block
        return None

    def find_node_by_id(self, node_id: str) -> Optional[NodeInfo]:
        """
        Find a node by its ID

        Args:
            node_id: Node ID to search for

        Returns:
            NodeInfo if found, None otherwise
        """
        for node in self.extract_nodes():
            if node.node_id == node_id:
                return node
        return None

    def find_scenario_by_slug(self, slug: str) -> Optional[ScenarioInfo]:
        """
        Find a scenario by its slug

        Args:
            slug: Scenario slug to search for

        Returns:
            ScenarioInfo if found, None otherwise
        """
        for scenario in self.extract_scenarios():
            if scenario.slug == slug:
                return scenario
        return None
