"""
LLM-Powered Narrative Generator using Anthropic Claude with OpenAI fallback.
Generates intelligent, context-aware narratives for anomaly detections.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Try to import both LLM libraries
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available. Install with: pip install anthropic")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available. Install with: pip install openai")


class LLMNarrativeGenerator:
    """
    Generates human-readable narratives using Claude LLM with OpenAI fallback.
    Falls back to template-based generation if both LLMs are unavailable.
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229"
    ):
        """
        Initialize LLM narrative generator.

        Args:
            anthropic_api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: Claude model to use
        """
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.anthropic_client = None
        self.openai_client = None
        self.active_provider = None

        # Try to initialize Anthropic first
        if ANTHROPIC_AVAILABLE and self.anthropic_api_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                self.active_provider = "anthropic"
                logger.info(f"Anthropic LLM initialized with model: {model}")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                self.anthropic_client = None

        # ALWAYS try to initialize OpenAI as well (for runtime fallback)
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
                if not self.active_provider:  # Only set as active if Anthropic wasn't initialized
                    self.active_provider = "openai"
                logger.info("OpenAI LLM initialized as fallback provider with model: gpt-4")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None

        # Log fallback status
        if not self.anthropic_client and not self.openai_client:
            logger.warning("No LLM providers available. Using template-based fallback generation.")

    def generate_anomaly_narrative(
        self,
        anomaly_report: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a narrative for a single anomaly.

        Args:
            anomaly_report: Anomaly report data
            context_data: Additional context (market conditions, historical data, etc.)

        Returns:
            Natural language narrative
        """
        # Try Anthropic first
        if self.anthropic_client:
            try:
                return self._generate_with_anthropic(anomaly_report, context_data)
            except Exception as e:
                logger.warning(f"Anthropic generation failed: {e}, falling back to OpenAI")

        # Try OpenAI as fallback
        if self.openai_client:
            try:
                return self._generate_with_openai(anomaly_report, context_data)
            except Exception as e:
                logger.warning(f"OpenAI generation failed: {e}, using template fallback")

        # Final fallback to template
        return self._fallback_narrative(anomaly_report)

    def _generate_with_anthropic(
        self,
        anomaly_report: Dict[str, Any],
        context_data: Optional[Dict[str, Any]]
    ) -> str:
        """Generate narrative using Anthropic Claude."""
        prompt = self._build_anomaly_prompt(anomaly_report, context_data)

        message = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        narrative = message.content[0].text.strip()
        logger.info("Successfully generated Anthropic narrative")
        return narrative

    def _generate_with_openai(
        self,
        anomaly_report: Dict[str, Any],
        context_data: Optional[Dict[str, Any]]
    ) -> str:
        """Generate narrative using OpenAI GPT."""
        prompt = self._build_anomaly_prompt(anomaly_report, context_data)

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=500,
            temperature=0.7
        )

        narrative = response.choices[0].message.content.strip()
        logger.info("Successfully generated OpenAI narrative")
        return narrative

    def generate_analysis_summary(
        self,
        reports: List[Dict[str, Any]],
        system_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate an executive summary for multiple anomalies.

        Args:
            reports: List of anomaly reports
            system_stats: System statistics and metrics

        Returns:
            Executive summary narrative
        """
        if not reports:
            return "No anomalies detected. All systems are operating within normal parameters."

        # Try Anthropic first
        if self.anthropic_client:
            try:
                return self._generate_summary_anthropic(reports, system_stats)
            except Exception as e:
                logger.warning(f"Anthropic summary failed: {e}, falling back to OpenAI")

        # Try OpenAI as fallback
        if self.openai_client:
            try:
                return self._generate_summary_openai(reports, system_stats)
            except Exception as e:
                logger.warning(f"OpenAI summary failed: {e}, using template fallback")

        # Final fallback
        return self._fallback_summary(reports)

    def _generate_summary_anthropic(
        self,
        reports: List[Dict[str, Any]],
        system_stats: Optional[Dict[str, Any]]
    ) -> str:
        """Generate summary using Anthropic Claude."""
        prompt = self._build_summary_prompt(reports, system_stats)

        message = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=800,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        summary = message.content[0].text.strip()
        logger.info("Successfully generated Anthropic summary")
        return summary

    def _generate_summary_openai(
        self,
        reports: List[Dict[str, Any]],
        system_stats: Optional[Dict[str, Any]]
    ) -> str:
        """Generate summary using OpenAI GPT."""
        prompt = self._build_summary_prompt(reports, system_stats)

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": prompt
            }],
            max_tokens=800,
            temperature=0.7
        )

        summary = response.choices[0].message.content.strip()
        logger.info("Successfully generated OpenAI summary")
        return summary

    def _build_anomaly_prompt(
        self,
        anomaly_report: Dict[str, Any],
        context_data: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for single anomaly narrative."""

        # Extract key information
        source = anomaly_report.get('source', 'unknown')
        metric = anomaly_report.get('metric', 'unknown')
        severity = anomaly_report.get('severity', 'medium')
        confidence = anomaly_report.get('consensus_score', 0) * 100
        detecting_agents = anomaly_report.get('detecting_agents', [])
        detection_count = anomaly_report.get('detection_count', 0)
        explanation = anomaly_report.get('explanation', '')
        value = anomaly_report.get('value')
        timestamp = anomaly_report.get('timestamp', datetime.now())

        # Format timestamp
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(timestamp, datetime) else str(timestamp)

        prompt = f"""You are an AI analyst for a sophisticated anomaly detection system that monitors cryptocurrency markets, weather data, and GitHub activity. Your role is to explain anomalies in clear, actionable language that both technical and non-technical stakeholders can understand.

ANOMALY DETAILS:
- Source: {source}
- Metric: {metric}
- Severity: {severity.upper()}
- Confidence: {confidence:.1f}%
- Detected by: {detection_count} agents ({', '.join(detecting_agents)})
- Timestamp: {time_str}
- Value: {value}
- Technical Explanation: {explanation}

CONTEXT:
"""

        # Add OI-specific context if available
        if source == 'oi_derivatives':
            metadata = anomaly_report.get('metadata', {})
            divergence_type = metadata.get('divergence_type')
            funding_rate = metadata.get('funding_rate')
            long_short_ratio = metadata.get('long_short_ratio')

            prompt += f"""
This is an Open Interest (OI) derivatives anomaly from the futures market.
- Divergence Type: {divergence_type if divergence_type else 'N/A'}
- Funding Rate: {funding_rate if funding_rate else 'N/A'}
- Long/Short Ratio: {long_short_ratio if long_short_ratio else 'N/A'}
"""

        # Add general context
        if context_data:
            prompt += f"\nAdditional Context: {context_data}\n"

        prompt += """
YOUR TASK:
Generate a concise, insightful narrative (3-4 sentences) that:
1. Explains WHAT happened in plain language
2. Explains WHY this is significant (market implications, potential causes)
3. Suggests WHAT to watch for next or potential actions

Write as if briefing a trader or analyst who needs to make decisions. Be specific, actionable, and avoid jargon where possible. If this is an OI divergence, explain the market mechanics clearly.

Generate the narrative now:"""

        return prompt

    def _build_summary_prompt(
        self,
        reports: List[Dict[str, Any]],
        system_stats: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for analysis summary."""

        total = len(reports)
        high_severity = sum(1 for r in reports if r.get('severity') == 'high')

        # Group by source
        sources = {}
        for report in reports:
            source = report.get('source', 'unknown')
            if source not in sources:
                sources[source] = []
            sources[source].append(report)

        # Top 3 most critical anomalies
        sorted_reports = sorted(reports, key=lambda x: x.get('severity_score', 0), reverse=True)
        top_anomalies = sorted_reports[:3]

        prompt = f"""You are an AI analyst providing an executive summary for a multi-agent anomaly detection system monitoring cryptocurrency markets, weather patterns, and GitHub activity.

SYSTEM STATUS:
- Total Anomalies Detected: {total}
- High Severity Count: {high_severity}
- Data Sources Active: {len(sources)}
- Sources: {', '.join(sources.keys())}

TOP 3 ANOMALIES:
"""

        for i, anomaly in enumerate(top_anomalies, 1):
            source = anomaly.get('source', 'unknown')
            metric = anomaly.get('metric', 'unknown')
            severity = anomaly.get('severity', 'medium')
            confidence = anomaly.get('consensus_score', 0) * 100

            prompt += f"""
{i}. {source.upper()} - {metric}
   Severity: {severity.upper()} | Confidence: {confidence:.0f}%
   Details: {anomaly.get('narrative', anomaly.get('explanation', 'No details'))[:150]}
"""

        if system_stats:
            prompt += f"\nSYSTEM METRICS: {system_stats}\n"

        prompt += """
YOUR TASK:
Generate an executive summary (4-6 sentences) that:
1. Provides an overview of the current situation
2. Highlights the most critical findings and their implications
3. Identifies any patterns or correlations across sources
4. Offers actionable recommendations or areas requiring attention

Write for a technical audience that needs to quickly understand system health and take action. Be direct, specific, and prioritize the most important information.

Generate the executive summary now:"""

        return prompt

    def _fallback_narrative(self, anomaly_report: Dict[str, Any]) -> str:
        """Generate template-based narrative when LLM is unavailable."""
        source = anomaly_report.get('source', 'unknown')
        metric = anomaly_report.get('metric', 'unknown')
        severity = anomaly_report.get('severity', 'medium')
        confidence = anomaly_report.get('consensus_score', 0) * 100

        narrative = f"Anomaly detected in {source} {metric} (severity: {severity.upper()}, confidence: {confidence:.0f}%). "

        if 'explanation' in anomaly_report:
            narrative += anomaly_report['explanation']

        return narrative

    def _fallback_summary(self, reports: List[Dict[str, Any]]) -> str:
        """Generate template-based summary when LLM is unavailable."""
        total = len(reports)
        high_severity = sum(1 for r in reports if r.get('severity') == 'high')

        sources = set(r.get('source', 'unknown') for r in reports)

        return (
            f"System Analysis: Detected {total} anomalies across {len(sources)} data sources. "
            f"{high_severity} high-severity issues require attention. "
            f"Affected sources: {', '.join(sources)}."
        )


# Singleton instance
_llm_generator = None


def get_llm_generator() -> LLMNarrativeGenerator:
    """Get or create singleton LLM generator instance."""
    global _llm_generator
    if _llm_generator is None:
        # Import settings here to avoid circular imports
        from backend.utils.config import get_settings
        settings = get_settings()
        _llm_generator = LLMNarrativeGenerator(
            anthropic_api_key=settings.anthropic_api_key,
            openai_api_key=settings.openai_api_key
        )
    return _llm_generator
