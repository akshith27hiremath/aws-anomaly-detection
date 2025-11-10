"""
Coordinator Agent - Synthesizes findings from all agents and produces final analysis.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from backend.explainability.counterfactual import CounterfactualGenerator
from backend.explainability.narrative_generator import NarrativeGenerator
from backend.knowledge_graph import AnomalyTracer, KnowledgeGraphManager
from backend.utils.config import get_detection_config
from backend.utils.helpers import weighted_average

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    Coordinator agent that synthesizes findings from all specialized agents.
    Produces final anomaly reports with explanations and counterfactuals.
    """

    def __init__(
        self,
        knowledge_graph: KnowledgeGraphManager,
        counterfactual_gen: CounterfactualGenerator,
        narrative_gen: NarrativeGenerator
    ):
        """
        Initialize the coordinator agent.

        Args:
            knowledge_graph: Knowledge graph manager
            counterfactual_gen: Counterfactual generator
            narrative_gen: Narrative generator
        """
        self.config = get_detection_config()
        agent_config = self.config.get_agent_config('coordinator')

        self.weight = agent_config.get('weight', 0.15)
        self.consensus_threshold = agent_config.get('consensus_threshold', 0.6)

        self.knowledge_graph = knowledge_graph
        self.anomaly_tracer = AnomalyTracer(knowledge_graph)
        self.counterfactual_gen = counterfactual_gen
        self.narrative_gen = narrative_gen

        self.name = "CoordinatorAgent"

    async def synthesize(
        self,
        agent_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesize results from all agents into final anomaly reports.

        Args:
            agent_results: List of results from all agents

        Returns:
            Synthesized anomaly reports
        """
        logger.info(f"{self.name}: Synthesizing results from {len(agent_results)} agents")

        # Extract all anomalies from agents
        all_anomalies = []
        for result in agent_results:
            agent_name = result.get('agent', 'unknown')
            agent_weight = result.get('weight', 0.2)

            for anomaly in result.get('anomalies', []):
                anomaly['agent_name'] = agent_name
                anomaly['agent_weight'] = agent_weight
                all_anomalies.append(anomaly)

        # Group anomalies by similarity
        grouped_anomalies = self._group_similar_anomalies(all_anomalies)

        # Create final reports
        final_reports = []

        for group in grouped_anomalies:
            report = await self._create_anomaly_report(group, agent_results)

            if report['consensus_score'] >= self.consensus_threshold:
                final_reports.append(report)

        # Sort by severity and confidence
        final_reports.sort(
            key=lambda x: (x['severity_score'], x['consensus_score']),
            reverse=True
        )

        # Add to knowledge graph
        for report in final_reports:
            self._add_to_knowledge_graph(report)

        # Detect relationships between anomalies
        self._detect_relationships(final_reports)

        logger.info(f"{self.name}: Generated {len(final_reports)} final anomaly reports")

        return {
            'agent': self.name,
            'total_anomalies': len(final_reports),
            'high_severity_count': sum(1 for r in final_reports if r['severity'] in ['high', 'critical']),
            'reports': final_reports,
            'metadata': {
                'agents_consulted': [r['agent'] for r in agent_results],
                'total_detections': len(all_anomalies),
                'consensus_threshold': self.consensus_threshold
            }
        }

    def _group_similar_anomalies(
        self,
        anomalies: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Group similar anomalies detected by different agents."""
        if not anomalies:
            return []

        # Group by source, metric, and approximate timestamp
        groups = {}

        for anomaly in anomalies:
            source = anomaly.get('source', 'unknown')
            metric = anomaly.get('metric', 'unknown')
            timestamp = anomaly.get('timestamp', datetime.now())

            # Round timestamp to minute for grouping
            ts_key = timestamp.replace(second=0, microsecond=0)

            key = (source, metric, ts_key)

            if key not in groups:
                groups[key] = []

            groups[key].append(anomaly)

        return list(groups.values())

    async def _create_anomaly_report(
        self,
        anomaly_group: List[Dict[str, Any]],
        agent_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create comprehensive report for an anomaly group."""
        # Calculate consensus score
        agent_weights = [a.get('agent_weight', 0.2) for a in anomaly_group]
        agent_confidences = [a.get('confidence', 0.5) for a in anomaly_group]

        consensus_score = weighted_average(agent_confidences, agent_weights)

        # Aggregate severity
        severity_scores = [a.get('severity_score', 0.5) for a in anomaly_group]
        avg_severity_score = np.mean(severity_scores)

        if avg_severity_score >= 0.9:
            severity = 'critical'
        elif avg_severity_score >= 0.75:
            severity = 'high'
        elif avg_severity_score >= 0.5:
            severity = 'medium'
        else:
            severity = 'low'

        # Get representative anomaly
        representative = max(anomaly_group, key=lambda x: x.get('confidence', 0))

        # Generate unique ID
        anomaly_id = self._generate_anomaly_id(representative)

        # Collect all detection methods
        all_methods = []
        for anomaly in anomaly_group:
            methods = anomaly.get('detection_methods', [])
            if isinstance(methods, list):
                all_methods.extend(methods)
            agent_name = anomaly.get('agent_name', '')
            if agent_name:
                all_methods.append(agent_name)

        # Generate explanations
        combined_explanation = self._combine_explanations(anomaly_group)

        # Generate narrative
        narrative = self.narrative_gen.generate(representative, anomaly_group)

        # Generate counterfactuals
        counterfactuals = self.counterfactual_gen.generate(representative)

        report = {
            'anomaly_id': anomaly_id,
            'source': representative.get('source'),
            'metric': representative.get('metric'),
            'timestamp': representative.get('timestamp', datetime.now()),
            'value': representative.get('value'),
            'consensus_score': consensus_score,
            'severity': severity,
            'severity_score': avg_severity_score,
            'detection_count': len(anomaly_group),
            'detecting_agents': list(set(a.get('agent_name') for a in anomaly_group)),
            'detection_methods': list(set(all_methods)),
            'explanation': combined_explanation,
            'narrative': narrative,
            'counterfactuals': counterfactuals,
            'individual_detections': anomaly_group,
            'created_at': datetime.now()
        }

        return report

    def _generate_anomaly_id(self, anomaly: Dict[str, Any]) -> str:
        """Generate unique ID for anomaly."""
        source = anomaly.get('source', 'unknown')
        metric = anomaly.get('metric', 'unknown')
        timestamp = anomaly.get('timestamp', datetime.now())

        return f"{source}_{metric}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

    def _combine_explanations(self, anomaly_group: List[Dict[str, Any]]) -> str:
        """Combine explanations from multiple agents."""
        explanations = []

        for anomaly in anomaly_group:
            explanation = anomaly.get('explanation', '')
            agent = anomaly.get('agent_name', 'Unknown')

            if explanation:
                explanations.append(f"[{agent}] {explanation}")

        return " | ".join(explanations)

    def _add_to_knowledge_graph(self, report: Dict[str, Any]) -> None:
        """Add anomaly report to knowledge graph."""
        try:
            anomaly_id = report['anomaly_id']

            # Prepare data for knowledge graph
            anomaly_data = {
                'source': report['source'],
                'metric': report['metric'],
                'value': report['value'],
                'confidence': report['consensus_score'],
                'severity': report['severity'],
                'methods': report['detection_methods'],
                'metadata': {
                    'detecting_agents': report['detecting_agents'],
                    'detection_count': report['detection_count']
                }
            }

            # Add to graph
            self.knowledge_graph.add_anomaly(
                anomaly_id=anomaly_id,
                anomaly_data=anomaly_data,
                timestamp=report['timestamp']
            )

        except Exception as e:
            logger.error(f"Error adding anomaly to knowledge graph: {e}")

    def _detect_relationships(self, reports: List[Dict[str, Any]]) -> None:
        """Detect and add relationships between anomalies."""
        for i, report1 in enumerate(reports):
            for report2 in reports[i+1:]:
                # Check for temporal proximity
                time_diff = abs(
                    (report1['timestamp'] - report2['timestamp']).total_seconds()
                )

                if time_diff <= 300:  # Within 5 minutes
                    # Temporal relationship
                    self.knowledge_graph.add_relationship(
                        report1['anomaly_id'],
                        report2['anomaly_id'],
                        'temporal',
                        confidence=0.7
                    )

                # Check for same source
                if report1['source'] == report2['source']:
                    # Same source correlation
                    self.knowledge_graph.add_relationship(
                        report1['anomaly_id'],
                        report2['anomaly_id'],
                        'correlation',
                        confidence=0.6
                    )

                # Check for potential causality (earlier -> later)
                if report1['timestamp'] < report2['timestamp'] and time_diff <= 600:
                    # Potential causal relationship
                    confidence = 0.5 + (0.3 if report1['severity'] == 'high' else 0)

                    self.knowledge_graph.add_relationship(
                        report1['anomaly_id'],
                        report2['anomaly_id'],
                        'causal',
                        confidence=confidence,
                        metadata={'time_diff_seconds': time_diff}
                    )


class AgentOrchestrator:
    """
    Orchestrates all agents to perform comprehensive anomaly detection.
    """

    def __init__(self):
        """Initialize the orchestrator with all agents."""
        from .context_agent import ContextAgent
        from .correlation_agent import CorrelationAgent
        from .statistical_agent import StatisticalAgent
        from .temporal_agent import TemporalAgent

        # Initialize components
        self.knowledge_graph = KnowledgeGraphManager()
        self.counterfactual_gen = CounterfactualGenerator()
        self.narrative_gen = NarrativeGenerator()

        # Initialize agents
        self.statistical_agent = StatisticalAgent()
        self.temporal_agent = TemporalAgent()
        self.correlation_agent = CorrelationAgent()
        self.context_agent = ContextAgent()
        self.coordinator = CoordinatorAgent(
            self.knowledge_graph,
            self.counterfactual_gen,
            self.narrative_gen
        )

    async def analyze(
        self,
        current_data: List[Dict[str, Any]],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Run complete analysis using all agents.

        Args:
            current_data: Current data points to analyze
            historical_data: Historical data for context

        Returns:
            Complete analysis results
        """
        logger.info("Starting multi-agent anomaly detection")

        # Run all agents in parallel
        import asyncio

        agent_tasks = [
            self.statistical_agent.analyze(current_data, historical_data),
            self.temporal_agent.analyze(current_data, historical_data),
            self.correlation_agent.analyze(current_data, historical_data),
            self.context_agent.analyze(current_data, historical_data)
        ]

        agent_results = await asyncio.gather(*agent_tasks)

        # Synthesize results
        final_results = await self.coordinator.synthesize(agent_results)

        # Add graph export
        final_results['knowledge_graph'] = self.knowledge_graph.export_graph()

        return final_results
