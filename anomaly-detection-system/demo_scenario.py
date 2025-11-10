"""
Demo scenario generator for anomaly detection system.
Creates synthetic data with known anomalies for demonstration.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

import numpy as np


class DemoScenarioGenerator:
    """Generates demo scenarios with synthetic anomalies."""

    def __init__(self):
        self.base_crypto_price = 50000
        self.base_temp = 20
        self.base_github_commits = 10

    def generate_flash_crash_scenario(self) -> List[Dict[str, Any]]:
        """
        Generate a flash crash scenario in cryptocurrency
        correlating with GitHub API anomaly.
        """
        data_points = []
        base_time = datetime.now() - timedelta(hours=2)

        for i in range(120):  # 2 hours of data at 1-minute intervals
            timestamp = base_time + timedelta(minutes=i)

            # Normal crypto price
            crypto_price = self.base_crypto_price + random.uniform(-100, 100)

            # Flash crash at minute 60
            if 58 <= i <= 62:
                crypto_price *= 0.7  # 30% drop

            # Normal GitHub commits
            github_commits = self.base_github_commits + random.randint(-2, 2)

            # GitHub anomaly correlating with crash
            if 59 <= i <= 61:
                github_commits *= 3  # Spike in commits

            # Add data points
            data_points.extend([
                {
                    'source': 'cryptocurrency',
                    'metric': 'price_usd',
                    'value': crypto_price,
                    'timestamp': timestamp
                },
                {
                    'source': 'github',
                    'metric': 'commit_count',
                    'value': github_commits,
                    'timestamp': timestamp
                }
            ])

        return data_points

    def generate_weather_anomaly_scenario(self) -> List[Dict[str, Any]]:
        """Generate unusual weather pattern with GitHub correlation."""
        data_points = []
        base_time = datetime.now() - timedelta(hours=1)

        for i in range(60):
            timestamp = base_time + timedelta(minutes=i)

            # Normal temperature with daily pattern
            temp = self.base_temp + 5 * np.sin(i / 10) + random.uniform(-1, 1)

            # Weather anomaly
            if 30 <= i <= 35:
                temp += 15  # Sudden temperature spike

            # GitHub activity
            github_issues = 5 + random.randint(-1, 1)

            if 31 <= i <= 34:
                github_issues += 10  # Spike in issues

            data_points.extend([
                {
                    'source': 'weather',
                    'metric': 'temperature',
                    'value': temp,
                    'timestamp': timestamp
                },
                {
                    'source': 'github',
                    'metric': 'issue_count',
                    'value': github_issues,
                    'timestamp': timestamp
                }
            ])

        return data_points

    def generate_cascading_scenario(self) -> List[Dict[str, Any]]:
        """Generate cascading anomalies across all sources."""
        data_points = []
        base_time = datetime.now() - timedelta(minutes=30)

        for i in range(30):
            timestamp = base_time + timedelta(minutes=i)

            # Crypto price
            crypto_price = self.base_crypto_price + random.uniform(-50, 50)
            if i >= 10:  # Start anomaly
                crypto_price *= 1.1 + (i - 10) * 0.01

            # Weather
            temp = self.base_temp + random.uniform(-1, 1)
            if i >= 12:  # Cascade effect
                temp += (i - 12) * 0.5

            # GitHub
            commits = self.base_github_commits + random.randint(-1, 1)
            if i >= 15:  # Further cascade
                commits += (i - 15)

            data_points.extend([
                {
                    'source': 'cryptocurrency',
                    'metric': 'price_usd',
                    'value': crypto_price,
                    'timestamp': timestamp
                },
                {
                    'source': 'weather',
                    'metric': 'temperature',
                    'value': temp,
                    'timestamp': timestamp
                },
                {
                    'source': 'github',
                    'metric': 'commit_count',
                    'value': commits,
                    'timestamp': timestamp
                }
            ])

        return data_points


async def run_demo():
    """Run the demo scenarios."""
    print("=" * 60)
    print("🎬 ANOMALY DETECTION DEMO SCENARIOS")
    print("=" * 60)

    generator = DemoScenarioGenerator()

    # Import the orchestrator
    from backend.agents import AgentOrchestrator

    orchestrator = AgentOrchestrator()

    # Scenario 1: Flash Crash
    print("\n📉 Scenario 1: Flash Crash with Correlated GitHub Anomaly")
    print("-" * 60)
    flash_crash_data = generator.generate_flash_crash_scenario()
    result1 = await orchestrator.analyze(flash_crash_data)

    print(f"✓ Detected {result1['total_anomalies']} anomalies")
    print(f"✓ {result1['high_severity_count']} high severity anomalies")

    for report in result1['reports'][:3]:
        print(f"\n  • {report['source']} - {report['metric']}")
        print(f"    Severity: {report['severity']} | Confidence: {report['consensus_score']:.2f}")
        print(f"    {report['narrative'][:100]}...")

    # Scenario 2: Weather Anomaly
    print("\n\n🌡️  Scenario 2: Weather Anomaly with GitHub Correlation")
    print("-" * 60)
    weather_data = generator.generate_weather_anomaly_scenario()
    result2 = await orchestrator.analyze(weather_data)

    print(f"✓ Detected {result2['total_anomalies']} anomalies")
    print(f"✓ {result2['high_severity_count']} high severity anomalies")

    # Scenario 3: Cascading Failures
    print("\n\n⚡ Scenario 3: Cascading Anomalies Across Sources")
    print("-" * 60)
    cascade_data = generator.generate_cascading_scenario()
    result3 = await orchestrator.analyze(cascade_data)

    print(f"✓ Detected {result3['total_anomalies']} anomalies")
    print(f"✓ {result3['high_severity_count']} high severity anomalies")

    # Knowledge graph stats
    print("\n\n🕸️  Knowledge Graph Statistics")
    print("-" * 60)
    kg_stats = result3['knowledge_graph']['stats']
    print(f"✓ Nodes: {kg_stats['num_nodes']}")
    print(f"✓ Edges: {kg_stats['num_edges']}")
    print(f"✓ Average Degree: {kg_stats['avg_degree']:.2f}")

    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_demo())
