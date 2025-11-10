"""
Counterfactual Generator - Generates 'what-if' scenarios for anomalies.
"""

import logging
from typing import Any, Dict, List

import numpy as np

logger = logging.getLogger(__name__)


class CounterfactualGenerator:
    """
    Generates counterfactual explanations for anomalies.
    Answers questions like 'What if X didn't happen?' or 'What would be normal?'
    """

    def __init__(self, max_scenarios: int = 5):
        """
        Initialize counterfactual generator.

        Args:
            max_scenarios: Maximum number of counterfactual scenarios to generate
        """
        self.max_scenarios = max_scenarios

    def generate(self, anomaly: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate counterfactual scenarios for an anomaly.

        Args:
            anomaly: Anomaly data

        Returns:
            List of counterfactual scenarios
        """
        scenarios = []

        # Scenario 1: Normal value expectation
        expected_value = anomaly.get('expected_value')
        if expected_value is not None:
            scenarios.append({
                'type': 'expected_value',
                'title': 'If the value was normal',
                'description': (
                    f"If the value had been {expected_value:.2f} (expected) instead of "
                    f"{anomaly.get('value', 0):.2f}, no anomaly would have been detected."
                ),
                'expected_value': expected_value,
                'actual_value': anomaly.get('value'),
                'impact': 'No anomaly alert'
            })

        # Scenario 2: Threshold-based
        if 'z_score' in anomaly:
            z_score = anomaly['z_score']
            value = anomaly.get('value', 0)
            expected = anomaly.get('expected_value', 0)

            # Calculate what value would be just below threshold
            threshold_value = expected + (2.5 * (value - expected) / z_score)

            scenarios.append({
                'type': 'threshold',
                'title': 'If the deviation was smaller',
                'description': (
                    f"If the value had been {threshold_value:.2f}, it would have been "
                    f"within acceptable thresholds (Z-score < 3.0)."
                ),
                'threshold_value': threshold_value,
                'actual_zscore': z_score,
                'threshold_zscore': 2.5,
                'impact': 'Below detection threshold'
            })

        # Scenario 3: Trend continuation
        if 'local_slope' in anomaly and 'global_slope' in anomaly:
            scenarios.append({
                'type': 'trend',
                'title': 'If the trend had continued normally',
                'description': (
                    f"If the local trend had matched the global trend, "
                    f"the value would have followed the expected pattern."
                ),
                'expected_trend': anomaly['global_slope'],
                'actual_trend': anomaly['local_slope'],
                'impact': 'Consistent with historical trends'
            })

        # Scenario 4: No sudden change
        if 'mean_before' in anomaly and 'mean_after' in anomaly:
            scenarios.append({
                'type': 'no_changepoint',
                'title': 'If there was no regime change',
                'description': (
                    f"If the mean had remained at {anomaly['mean_before']:.2f} instead of "
                    f"shifting to {anomaly['mean_after']:.2f}, the pattern would have been normal."
                ),
                'stable_mean': anomaly['mean_before'],
                'actual_change': abs(anomaly['mean_after'] - anomaly['mean_before']),
                'impact': 'Stable pattern maintained'
            })

        # Scenario 5: Seasonal expectation
        if 'seasonal_component' in anomaly:
            scenarios.append({
                'type': 'seasonal',
                'title': 'If seasonal patterns were followed',
                'description': (
                    f"If the value had followed seasonal expectations "
                    f"({anomaly.get('expected_value', 0):.2f}), it would be consistent "
                    f"with historical seasonal patterns."
                ),
                'seasonal_expected': anomaly.get('expected_value'),
                'seasonal_component': anomaly['seasonal_component'],
                'impact': 'Aligned with seasonality'
            })

        # Limit to max scenarios
        return scenarios[:self.max_scenarios]

    def generate_what_if(
        self,
        anomaly: Dict[str, Any],
        parameter: str,
        new_value: float
    ) -> Dict[str, Any]:
        """
        Generate specific 'what-if' scenario by changing a parameter.

        Args:
            anomaly: Anomaly data
            parameter: Parameter to change
            new_value: New value for the parameter

        Returns:
            What-if scenario result
        """
        original_value = anomaly.get(parameter)

        if original_value is None:
            return {
                'success': False,
                'error': f'Parameter {parameter} not found in anomaly data'
            }

        # Simulate the impact
        impact_description = self._calculate_impact(
            anomaly, parameter, original_value, new_value
        )

        return {
            'success': True,
            'parameter': parameter,
            'original_value': original_value,
            'new_value': new_value,
            'impact': impact_description
        }

    def _calculate_impact(
        self,
        anomaly: Dict[str, Any],
        parameter: str,
        original: float,
        new: float
    ) -> str:
        """Calculate the impact of changing a parameter."""
        change = abs(new - original)
        percent_change = (change / original * 100) if original != 0 else 0

        if percent_change < 10:
            severity = "minimal"
        elif percent_change < 30:
            severity = "moderate"
        else:
            severity = "significant"

        return (
            f"Changing {parameter} from {original:.2f} to {new:.2f} "
            f"({percent_change:.1f}% change) would have a {severity} impact on "
            f"anomaly detection."
        )
