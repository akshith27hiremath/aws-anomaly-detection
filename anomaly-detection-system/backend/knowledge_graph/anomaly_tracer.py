"""
Anomaly Tracer for analyzing relationships and cascading effects.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .graph_manager import KnowledgeGraphManager

logger = logging.getLogger(__name__)


class AnomalyTracer:
    """
    Traces anomaly relationships and cascading effects through the knowledge graph.
    """

    def __init__(self, graph_manager: KnowledgeGraphManager):
        """
        Initialize anomaly tracer.

        Args:
            graph_manager: Knowledge graph manager instance
        """
        self.graph = graph_manager

    def trace_root_cause(self, anomaly_id: str) -> Dict[str, Any]:
        """
        Attempt to find the root cause of an anomaly by tracing backward.

        Args:
            anomaly_id: Anomaly to trace

        Returns:
            Dictionary with root cause analysis
        """
        # Find all incoming causal edges
        causal_predecessors = []

        if anomaly_id in self.graph.graph:
            for predecessor in self.graph.graph.predecessors(anomaly_id):
                edge_data = self.graph.graph.edges[predecessor, anomaly_id]
                if edge_data.get('type') == 'causal':
                    causal_predecessors.append({
                        'anomaly_id': predecessor,
                        'node_data': self.graph.graph.nodes[predecessor],
                        'edge_data': edge_data
                    })

        # If no predecessors, this might be a root cause
        if not causal_predecessors:
            return {
                'is_root_cause': True,
                'anomaly_id': anomaly_id,
                'confidence': 0.8,
                'explanation': 'No causal predecessors found - likely a root cause'
            }

        # Find the earliest predecessor
        earliest = min(
            causal_predecessors,
            key=lambda x: x['node_data'].get('timestamp', datetime.now())
        )

        # Recursively trace back
        further_trace = self.trace_root_cause(earliest['anomaly_id'])

        return {
            'is_root_cause': False,
            'anomaly_id': anomaly_id,
            'immediate_cause': earliest,
            'root_cause': further_trace,
            'causal_chain_length': 1 + further_trace.get('causal_chain_length', 0)
        }

    def trace_downstream_effects(
        self,
        anomaly_id: str,
        max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find all downstream anomalies caused by this anomaly.

        Args:
            anomaly_id: Source anomaly
            max_depth: Maximum depth to trace

        Returns:
            List of affected anomalies
        """
        affected = []

        def dfs(current_id: str, depth: int, path: List[str]):
            if depth >= max_depth:
                return

            if current_id not in self.graph.graph:
                return

            for successor in self.graph.graph.successors(current_id):
                edge_data = self.graph.graph.edges[current_id, successor]

                # Only follow causal edges
                if edge_data.get('type') == 'causal':
                    if successor not in path:  # Avoid cycles
                        affected.append({
                            'anomaly_id': successor,
                            'depth': depth + 1,
                            'path': path + [successor],
                            'node_data': self.graph.graph.nodes[successor],
                            'edge_data': edge_data
                        })

                        dfs(successor, depth + 1, path + [successor])

        dfs(anomaly_id, 0, [anomaly_id])
        return affected

    def find_cascading_failures(
        self,
        time_window_minutes: int = 30,
        min_anomalies: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Identify cascading failure patterns - multiple related anomalies in short time.

        Args:
            time_window_minutes: Time window to search
            min_anomalies: Minimum anomalies to constitute a cascade

        Returns:
            List of cascading failure events
        """
        cascades = []

        # Group anomalies by time windows
        time_groups = {}
        for node_id, timestamp in self.graph.node_timestamps.items():
            window_key = timestamp.replace(second=0, microsecond=0)
            window_key = window_key.replace(
                minute=(window_key.minute // time_window_minutes) * time_window_minutes
            )

            if window_key not in time_groups:
                time_groups[window_key] = []

            time_groups[window_key].append({
                'anomaly_id': node_id,
                'timestamp': timestamp,
                'node_data': self.graph.graph.nodes[node_id]
            })

        # Find windows with multiple anomalies
        for window_time, anomalies in time_groups.items():
            if len(anomalies) >= min_anomalies:
                # Check if they're related
                related_count = 0
                for i, a1 in enumerate(anomalies):
                    for a2 in anomalies[i+1:]:
                        if self.graph.graph.has_edge(a1['anomaly_id'], a2['anomaly_id']):
                            related_count += 1

                if related_count > 0:
                    cascades.append({
                        'window_start': window_time,
                        'window_end': window_time + timedelta(minutes=time_window_minutes),
                        'anomaly_count': len(anomalies),
                        'related_pairs': related_count,
                        'anomalies': anomalies,
                        'severity': self._calculate_cascade_severity(anomalies)
                    })

        return cascades

    def _calculate_cascade_severity(self, anomalies: List[Dict[str, Any]]) -> float:
        """Calculate overall severity of a cascade."""
        if not anomalies:
            return 0.0

        severities = []
        severity_map = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}

        for anomaly in anomalies:
            sev = anomaly['node_data'].get('severity', 'medium')
            severities.append(severity_map.get(sev, 0.5))

        # Use max severity with average as modifier
        return max(severities) * 0.7 + (sum(severities) / len(severities)) * 0.3

    def find_correlation_clusters(self, min_cluster_size: int = 2) -> List[Dict[str, Any]]:
        """
        Find clusters of correlated anomalies.

        Args:
            min_cluster_size: Minimum anomalies in a cluster

        Returns:
            List of correlation clusters
        """
        import networkx as nx

        # Create subgraph of correlation edges only
        correlation_graph = nx.Graph()

        for src, dst, edge_data in self.graph.graph.edges(data=True):
            if edge_data.get('type') == 'correlation':
                correlation_graph.add_edge(src, dst, **edge_data)

        # Find connected components (clusters)
        clusters = []
        for component in nx.connected_components(correlation_graph):
            if len(component) >= min_cluster_size:
                cluster_anomalies = [
                    {
                        'anomaly_id': node_id,
                        'node_data': self.graph.graph.nodes[node_id]
                    }
                    for node_id in component
                ]

                # Analyze cluster
                sources = set(a['node_data'].get('source') for a in cluster_anomalies)
                metrics = set(a['node_data'].get('metric') for a in cluster_anomalies)

                clusters.append({
                    'size': len(component),
                    'anomalies': cluster_anomalies,
                    'affected_sources': list(sources),
                    'affected_metrics': list(metrics),
                    'is_cross_source': len(sources) > 1
                })

        return clusters

    def generate_anomaly_narrative(self, anomaly_id: str) -> str:
        """
        Generate a narrative description of an anomaly and its context.

        Args:
            anomaly_id: Anomaly ID

        Returns:
            Human-readable narrative string
        """
        if anomaly_id not in self.graph.graph:
            return f"Anomaly {anomaly_id} not found in knowledge graph."

        node_data = self.graph.graph.nodes[anomaly_id]
        context = self.graph.get_anomaly_context(anomaly_id)

        narrative = []

        # Basic description
        narrative.append(
            f"Anomaly detected in {node_data.get('source', 'unknown source')} "
            f"for metric '{node_data.get('metric', 'unknown')}' "
            f"with {node_data.get('severity', 'medium')} severity "
            f"(confidence: {node_data.get('confidence', 0.5):.2f})."
        )

        # Temporal context
        if context.get('temporal_neighbors'):
            narrative.append(
                f"This anomaly occurred alongside {len(context['temporal_neighbors'])} "
                f"other anomalies in the same time window."
            )

        # Causal relationships
        root_cause = self.trace_root_cause(anomaly_id)
        if not root_cause['is_root_cause']:
            narrative.append(
                f"This appears to be a downstream effect, with a causal chain of "
                f"{root_cause.get('causal_chain_length', 0)} steps."
            )
        else:
            narrative.append("This appears to be a root cause anomaly.")

        # Downstream effects
        downstream = self.trace_downstream_effects(anomaly_id)
        if downstream:
            narrative.append(
                f"This anomaly triggered {len(downstream)} downstream anomalies."
            )

        # Similar patterns
        if context.get('similar_patterns'):
            narrative.append(
                f"Similar patterns were observed in {len(context['similar_patterns'])} "
                f"historical anomalies."
            )

        return " ".join(narrative)
