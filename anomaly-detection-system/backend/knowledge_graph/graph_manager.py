"""
Knowledge Graph Manager using NetworkX.
Manages temporal relationships between anomalies and enables pattern discovery.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
from backend.utils.config import get_detection_config
from backend.utils.helpers import generate_anomaly_fingerprint

logger = logging.getLogger(__name__)


class KnowledgeGraphManager:
    """
    Manages a temporal knowledge graph of anomalies.
    Nodes represent anomaly events, edges represent relationships.
    """

    def __init__(self):
        """Initialize the knowledge graph manager."""
        self.config = get_detection_config()
        kg_config = self.config.get('knowledge_graph', {})

        self.max_nodes = kg_config.get('max_nodes', 1000)
        self.edge_expiry_hours = kg_config.get('edge_expiry_hours', 168)  # 1 week
        self.similarity_threshold = kg_config.get('similarity_threshold', 0.8)

        # Create directed graph for temporal relationships
        self.graph = nx.DiGraph()

        # Store anomaly signatures for pattern matching
        self.signatures: Dict[str, Dict[str, Any]] = {}

        # Track node creation times for cleanup
        self.node_timestamps: Dict[str, datetime] = {}

    def add_anomaly(
        self,
        anomaly_id: str,
        anomaly_data: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Add an anomaly as a node in the knowledge graph.

        Args:
            anomaly_id: Unique identifier for the anomaly
            anomaly_data: Anomaly metadata and details
            timestamp: Timestamp of anomaly occurrence
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Create node attributes
        node_attrs = {
            'id': anomaly_id,
            'timestamp': timestamp,
            'source': anomaly_data.get('source', 'unknown'),
            'metric': anomaly_data.get('metric', 'unknown'),
            'value': anomaly_data.get('value'),
            'confidence': anomaly_data.get('confidence', 0.5),
            'severity': anomaly_data.get('severity', 'medium'),
            'methods': anomaly_data.get('methods', []),
            'metadata': anomaly_data.get('metadata', {})
        }

        # Add node to graph
        self.graph.add_node(anomaly_id, **node_attrs)
        self.node_timestamps[anomaly_id] = timestamp

        # Generate and store signature
        signature = self._generate_signature(anomaly_data)
        self.signatures[anomaly_id] = signature

        # Maintain graph size
        self._cleanup_old_nodes()

        logger.debug(f"Added anomaly node: {anomaly_id}")

    def add_relationship(
        self,
        from_anomaly: str,
        to_anomaly: str,
        relationship_type: str,
        confidence: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a relationship edge between two anomalies.

        Args:
            from_anomaly: Source anomaly ID
            to_anomaly: Target anomaly ID
            relationship_type: Type of relationship (causal, correlation, temporal, etc.)
            confidence: Confidence in this relationship (0-1)
            metadata: Additional relationship metadata
        """
        if from_anomaly not in self.graph or to_anomaly not in self.graph:
            logger.warning(f"Cannot add edge: nodes not in graph")
            return

        edge_attrs = {
            'type': relationship_type,
            'confidence': confidence,
            'created_at': datetime.now(),
            'metadata': metadata or {}
        }

        self.graph.add_edge(from_anomaly, to_anomaly, **edge_attrs)
        logger.debug(f"Added {relationship_type} edge: {from_anomaly} -> {to_anomaly}")

    def find_related_anomalies(
        self,
        anomaly_id: str,
        max_distance: int = 2,
        min_confidence: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find anomalies related to a given anomaly.

        Args:
            anomaly_id: Anomaly to find relations for
            max_distance: Maximum graph distance to search
            min_confidence: Minimum edge confidence to follow

        Returns:
            List of related anomalies with relationship info
        """
        if anomaly_id not in self.graph:
            return []

        related = []

        # BFS to find related nodes
        visited = {anomaly_id}
        queue = [(anomaly_id, 0, [])]  # (node, distance, path)

        while queue:
            current, distance, path = queue.pop(0)

            if distance >= max_distance:
                continue

            # Check outgoing edges
            for neighbor in self.graph.neighbors(current):
                if neighbor in visited:
                    continue

                edge_data = self.graph.edges[current, neighbor]
                edge_confidence = edge_data.get('confidence', 0.5)

                if edge_confidence >= min_confidence:
                    visited.add(neighbor)
                    new_path = path + [(current, neighbor, edge_data['type'])]

                    node_data = self.graph.nodes[neighbor]
                    related.append({
                        'anomaly_id': neighbor,
                        'distance': distance + 1,
                        'path': new_path,
                        'relationship_type': edge_data['type'],
                        'confidence': edge_confidence,
                        'node_data': node_data
                    })

                    queue.append((neighbor, distance + 1, new_path))

        return related

    def find_causal_chain(
        self,
        start_anomaly: str,
        end_anomaly: Optional[str] = None,
        max_length: int = 5
    ) -> List[List[Dict[str, Any]]]:
        """
        Find causal chains starting from an anomaly.

        Args:
            start_anomaly: Starting anomaly ID
            end_anomaly: Optional target anomaly ID
            max_length: Maximum chain length

        Returns:
            List of causal chains (each chain is a list of nodes)
        """
        if start_anomaly not in self.graph:
            return []

        chains = []

        def dfs(current: str, path: List[Dict[str, Any]], visited: Set[str]):
            """DFS to find causal paths."""
            if len(path) >= max_length:
                return

            # If we reached the target, save the chain
            if end_anomaly and current == end_anomaly:
                chains.append(path.copy())
                return

            # Explore causal edges
            for neighbor in self.graph.neighbors(current):
                if neighbor in visited:
                    continue

                edge_data = self.graph.edges[current, neighbor]
                if edge_data.get('type') == 'causal':
                    visited.add(neighbor)
                    node_data = self.graph.nodes[neighbor]

                    path.append({
                        'anomaly_id': neighbor,
                        'node_data': node_data,
                        'edge_data': edge_data
                    })

                    dfs(neighbor, path, visited)
                    path.pop()
                    visited.remove(neighbor)

            # If no specific target, save the chain if it's non-empty
            if not end_anomaly and len(path) > 1:
                chains.append(path.copy())

        # Start DFS
        start_node = self.graph.nodes[start_anomaly]
        dfs(start_anomaly, [{'anomaly_id': start_anomaly, 'node_data': start_node}], {start_anomaly})

        return chains

    def find_similar_patterns(
        self,
        anomaly_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find historical anomalies with similar patterns.

        Args:
            anomaly_id: Anomaly to find similar patterns for
            top_k: Number of similar patterns to return

        Returns:
            List of similar anomalies with similarity scores
        """
        if anomaly_id not in self.signatures:
            return []

        target_signature = self.signatures[anomaly_id]
        similarities = []

        for other_id, other_signature in self.signatures.items():
            if other_id == anomaly_id:
                continue

            similarity = self._calculate_signature_similarity(target_signature, other_signature)

            if similarity >= self.similarity_threshold:
                similarities.append({
                    'anomaly_id': other_id,
                    'similarity': similarity,
                    'signature': other_signature,
                    'node_data': self.graph.nodes.get(other_id, {})
                })

        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]

    def get_anomaly_context(self, anomaly_id: str) -> Dict[str, Any]:
        """
        Get full context for an anomaly including relationships and similar patterns.

        Args:
            anomaly_id: Anomaly ID

        Returns:
            Dictionary with comprehensive anomaly context
        """
        if anomaly_id not in self.graph:
            return {}

        node_data = dict(self.graph.nodes[anomaly_id])

        return {
            'anomaly_id': anomaly_id,
            'node_data': node_data,
            'signature': self.signatures.get(anomaly_id, {}),
            'related_anomalies': self.find_related_anomalies(anomaly_id),
            'causal_chains': self.find_causal_chain(anomaly_id),
            'similar_patterns': self.find_similar_patterns(anomaly_id),
            'temporal_neighbors': self._find_temporal_neighbors(anomaly_id)
        }

    def _find_temporal_neighbors(
        self,
        anomaly_id: str,
        time_window_hours: int = 1
    ) -> List[Dict[str, Any]]:
        """Find anomalies that occurred around the same time."""
        if anomaly_id not in self.node_timestamps:
            return []

        target_time = self.node_timestamps[anomaly_id]
        window_start = target_time - timedelta(hours=time_window_hours)
        window_end = target_time + timedelta(hours=time_window_hours)

        neighbors = []
        for node_id, timestamp in self.node_timestamps.items():
            if node_id != anomaly_id and window_start <= timestamp <= window_end:
                neighbors.append({
                    'anomaly_id': node_id,
                    'timestamp': timestamp,
                    'time_diff_seconds': abs((timestamp - target_time).total_seconds()),
                    'node_data': self.graph.nodes[node_id]
                })

        # Sort by time proximity
        neighbors.sort(key=lambda x: x['time_diff_seconds'])
        return neighbors

    def _generate_signature(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fingerprint signature for an anomaly."""
        return {
            'source': anomaly_data.get('source', ''),
            'metric': anomaly_data.get('metric', ''),
            'magnitude': abs(anomaly_data.get('deviation', 0)),
            'confidence': anomaly_data.get('confidence', 0.5),
            'methods': anomaly_data.get('methods', []),
            'pattern_type': anomaly_data.get('type', 'unknown')
        }

    def _calculate_signature_similarity(
        self,
        sig1: Dict[str, Any],
        sig2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between two anomaly signatures."""
        score = 0.0
        weights = {
            'source': 0.2,
            'metric': 0.2,
            'magnitude': 0.3,
            'pattern_type': 0.3
        }

        # Exact matches
        if sig1.get('source') == sig2.get('source'):
            score += weights['source']

        if sig1.get('metric') == sig2.get('metric'):
            score += weights['metric']

        if sig1.get('pattern_type') == sig2.get('pattern_type'):
            score += weights['pattern_type']

        # Magnitude similarity
        mag1 = sig1.get('magnitude', 0)
        mag2 = sig2.get('magnitude', 0)
        if mag1 > 0 and mag2 > 0:
            mag_ratio = min(mag1, mag2) / max(mag1, mag2)
            score += weights['magnitude'] * mag_ratio

        return score

    def _cleanup_old_nodes(self) -> None:
        """Remove old nodes to maintain max_nodes limit."""
        if len(self.graph.nodes) <= self.max_nodes:
            return

        # Sort nodes by timestamp
        sorted_nodes = sorted(
            self.node_timestamps.items(),
            key=lambda x: x[1]
        )

        # Remove oldest nodes
        num_to_remove = len(self.graph.nodes) - self.max_nodes
        for node_id, _ in sorted_nodes[:num_to_remove]:
            self.graph.remove_node(node_id)
            del self.node_timestamps[node_id]
            if node_id in self.signatures:
                del self.signatures[node_id]

        logger.info(f"Cleaned up {num_to_remove} old nodes from knowledge graph")

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        return {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'num_signatures': len(self.signatures),
            'oldest_node': min(self.node_timestamps.values()) if self.node_timestamps else None,
            'newest_node': max(self.node_timestamps.values()) if self.node_timestamps else None,
            'avg_degree': sum(dict(self.graph.degree()).values()) / max(self.graph.number_of_nodes(), 1)
        }

    def export_graph(self) -> Dict[str, Any]:
        """Export graph for visualization."""
        nodes = []
        edges = []

        for node_id, node_data in self.graph.nodes(data=True):
            nodes.append({
                'id': node_id,
                **node_data
            })

        for src, dst, edge_data in self.graph.edges(data=True):
            edges.append({
                'source': src,
                'target': dst,
                **edge_data
            })

        return {
            'nodes': nodes,
            'edges': edges,
            'stats': self.get_graph_stats()
        }
