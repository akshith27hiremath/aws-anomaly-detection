"""
Tests for multi-agent system.
"""

import pytest
from datetime import datetime

from backend.agents.statistical_agent import StatisticalAgent
from backend.agents.coordinator_agent import AgentOrchestrator


class TestStatisticalAgent:
    """Test statistical agent."""

    @pytest.mark.asyncio
    async def test_analyze(self):
        """Test agent analysis."""
        agent = StatisticalAgent()

        # Create test data
        data_points = []
        for i in range(100):
            data_points.append({
                'source': 'test',
                'metric': 'value',
                'value': 10 if i != 50 else 100,  # Anomaly at index 50
                'timestamp': datetime.now()
            })

        result = await agent.analyze(data_points)

        assert 'agent' in result
        assert result['agent'] == 'StatisticalAgent'
        assert 'anomalies' in result
        assert 'weight' in result
        assert isinstance(result['anomalies'], list)


class TestAgentOrchestrator:
    """Test agent orchestration."""

    @pytest.mark.asyncio
    async def test_orchestrator(self):
        """Test full orchestration."""
        orchestrator = AgentOrchestrator()

        # Create test data
        data_points = []
        for i in range(50):
            data_points.extend([
                {
                    'source': 'crypto',
                    'metric': 'price',
                    'value': 100 + i,
                    'timestamp': datetime.now()
                },
                {
                    'source': 'weather',
                    'metric': 'temperature',
                    'value': 20 + (i % 10),
                    'timestamp': datetime.now()
                }
            ])

        result = await orchestrator.analyze(data_points)

        assert 'total_anomalies' in result
        assert 'reports' in result
        assert isinstance(result['reports'], list)
