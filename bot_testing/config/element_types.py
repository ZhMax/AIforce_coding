"""
Data classes for bot configuration elements
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class BlockInfo:
    """Information about a block in the bot configuration"""

    path: str  # e.g., "scenarios[0].nodes[1].blocks[0]"
    type: str  # e.g., "llm", "answer", "buttons", etc.
    data: Dict[str, Any]  # Full block configuration
    scenario_slug: str  # Scenario containing this block
    scenario_name: str  # Human-readable scenario name
    node_id: str  # Node ID containing this block
    node_name: str  # Human-readable node name
    block_id: str  # Block's own ID

    def __repr__(self) -> str:
        return f"BlockInfo(type={self.type}, path={self.path})"


@dataclass
class EntryEdgeInfo:
    """Information about an entry edge in a scenario"""

    path: str  # e.g., "scenarios[0].entry_edges[0]"
    type: str  # "match", "event", "manual"
    pattern: str  # The value field (regex pattern or event name)
    target_node_id: str  # Target node ID
    scenario_slug: str  # Scenario containing this edge
    scenario_name: str  # Human-readable scenario name
    edge_id: Optional[str] = None  # Edge ID if present
    name: Optional[str] = None  # Edge name if present

    def __repr__(self) -> str:
        return f"EntryEdgeInfo(type={self.type}, pattern={self.pattern})"


@dataclass
class NodeInfo:
    """Information about a node in the bot configuration"""

    path: str  # e.g., "scenarios[0].nodes[1]"
    node_id: str  # Node's ID
    name: str  # Human-readable node name
    scenario_slug: str  # Scenario containing this node
    scenario_name: str  # Human-readable scenario name
    blocks: List[BlockInfo]  # Blocks in this node
    next_node_id: Optional[str] = None  # Next node in chain

    def __repr__(self) -> str:
        return f"NodeInfo(id={self.node_id}, name={self.name})"


@dataclass
class ScenarioInfo:
    """Information about a scenario in the bot configuration"""

    path: str  # e.g., "scenarios[0]"
    scenario_id: Optional[str]  # Scenario ID if present
    name: str  # Human-readable name
    slug: str  # URL-safe slug
    parent_scenario_id: Optional[str] = None
    entry_edges: List[EntryEdgeInfo] = None
    nodes: List[NodeInfo] = None

    def __post_init__(self):
        if self.entry_edges is None:
            self.entry_edges = []
        if self.nodes is None:
            self.nodes = []

    def __repr__(self) -> str:
        return f"ScenarioInfo(slug={self.slug}, nodes={len(self.nodes)})"


@dataclass
class BotInfo:
    """High-level bot configuration information with summary statistics"""

    bot_name: str
    bot_id: Optional[int] = None
    version_id: Optional[int] = None
    no_match_stub_answer: str = ""
    request_ttl_in_seconds: int = 30
    scenarios: List[ScenarioInfo] = None

    # Summary statistics (populated by analyzer)
    blocks_by_type: Dict[str, int] = None
    edges_by_type: Dict[str, int] = None
    llm_blocks: List[Dict[str, Any]] = None
    extend_blocks_count: int = 0
    button_blocks_count: int = 0

    def __post_init__(self):
        if self.scenarios is None:
            self.scenarios = []
        if self.blocks_by_type is None:
            self.blocks_by_type = {}
        if self.edges_by_type is None:
            self.edges_by_type = {}
        if self.llm_blocks is None:
            self.llm_blocks = []

    @property
    def scenarios_count(self) -> int:
        """Total number of scenarios"""
        return len(self.scenarios)

    @property
    def nodes_count(self) -> int:
        """Total number of nodes across all scenarios"""
        return sum(len(s.nodes) for s in self.scenarios)

    @property
    def blocks_count(self) -> int:
        """Total number of blocks across all scenarios"""
        return sum(self.blocks_by_type.values())

    @property
    def edges_count(self) -> int:
        """Total number of entry edges across all scenarios"""
        return sum(self.edges_by_type.values())

    def __repr__(self) -> str:
        return f"BotInfo(name={self.bot_name}, scenarios={len(self.scenarios)})"
