"""
Recommendation Engine

Generates evidence-based troubleshooting recommendations
based on historical incident data.
"""

from typing import List, Dict, Any
from app.models import Incident, HistoricalIncident, Recommendation, ActionOutcome


class RecommendationEngine:
    """Engine for generating troubleshooting recommendations."""

    def generate_recommendation(
        self,
        incident: Incident,
        historical_incidents: List[HistoricalIncident],
        successful_interventions: List[Dict[str, Any]],
        failed_interventions: List[Dict[str, Any]],
    ) -> Recommendation:
        """
        Generate a recommendation based on historical evidence.

        Args:
            incident: Current incident
            historical_incidents: Similar historical incidents
            successful_interventions: Previously successful actions
            failed_interventions: Previously failed actions

        Returns:
            Recommendation with reasoning
        """
        # No historical data
        if not historical_incidents:
            return self._generate_no_history_recommendation(incident)

        # Has successful interventions
        if successful_interventions:
            return self._generate_evidence_based_recommendation(
                incident,
                historical_incidents,
                successful_interventions,
                failed_interventions,
            )

        # Only failed interventions
        if failed_interventions:
            return self._generate_failed_only_recommendation(
                incident,
                failed_interventions,
            )

        # Historical incidents without outcomes
        return self._generate_partial_history_recommendation(
            incident,
            historical_incidents,
        )

    def _generate_no_history_recommendation(
        self,
        incident: Incident,
    ) -> Recommendation:
        """Generate recommendation when no history exists."""
        return Recommendation(
            suggested_action=self._get_default_action(incident),
            confidence="INSUFFICIENT_DATA",
            reasoning=(
                f"No relevant historical incidents found for {incident.machine_type} "
                f"with {incident.defect_type} defects. Recommendation is based on "
                "general troubleshooting principles. Please record the outcome of any "
                "intervention to improve future recommendations."
            ),
            supporting_incidents=[],
            warnings=[
                "This is the first recorded incident of this type.",
                "Verify the suggested action with experienced personnel.",
            ],
        )

    def _generate_evidence_based_recommendation(
        self,
        incident: Incident,
        historical: List[HistoricalIncident],
        successful: List[Dict[str, Any]],
        failed: List[Dict[str, Any]],
    ) -> Recommendation:
        """Generate recommendation based on successful interventions."""
        # Find the most common successful action
        action_counts = {}
        for s in successful:
            action = s["action"]
            action_counts[action] = action_counts.get(action, 0) + 1

        best_action = max(action_counts.keys(), key=lambda a: action_counts[a])
        success_count = action_counts[best_action]

        # Check if this action ever failed
        failed_actions = {f["action"] for f in failed}

        # Build reasoning
        reasoning_parts = [
            f"Found {len(historical)} relevant historical incident(s) for "
            f"{incident.machine_type} machines with {incident.defect_type} defects."
        ]

        reasoning_parts.append(
            f'"{best_action}" resolved {success_count} similar incident(s) successfully.'
        )

        # Mention failed alternatives
        if failed:
            failed_list = ", ".join(f'"{f["action"]}"' for f in failed[:3])
            reasoning_parts.append(
                f"Previously unsuccessful approaches: {failed_list}."
            )

        # Determine confidence
        if success_count >= 3 and best_action not in failed_actions:
            confidence = "HIGH"
        elif success_count >= 2:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        warnings = []
        if best_action in failed_actions:
            warnings.append(
                f'Note: "{best_action}" has also failed in some cases. '
                "Review the specific conditions of those failures."
            )

        return Recommendation(
            suggested_action=best_action,
            confidence=confidence,
            reasoning=" ".join(reasoning_parts),
            supporting_incidents=[s["incident_id"] for s in successful],
            warnings=warnings,
        )

    def _generate_failed_only_recommendation(
        self,
        incident: Incident,
        failed: List[Dict[str, Any]],
    ) -> Recommendation:
        """Generate recommendation when only failed interventions exist."""
        failed_actions = [f["action"] for f in failed]

        return Recommendation(
            suggested_action=self._get_default_action(incident),
            confidence="LOW",
            reasoning=(
                f"Previous interventions for similar incidents have failed: "
                f"{', '.join(f'\"' + a + '\"' for a in failed_actions[:3])}. "
                "A different approach may be needed. Consider escalating to "
                "engineering or investigating root cause more thoroughly."
            ),
            supporting_incidents=[f["incident_id"] for f in failed],
            warnings=[
                "Previous similar interventions have not been successful.",
                "Consider root cause analysis before proceeding.",
                "Escalation to engineering may be appropriate.",
            ],
        )

    def _generate_partial_history_recommendation(
        self,
        incident: Incident,
        historical: List[HistoricalIncident],
    ) -> Recommendation:
        """Generate recommendation when history exists but no outcomes recorded."""
        return Recommendation(
            suggested_action=self._get_default_action(incident),
            confidence="INSUFFICIENT_DATA",
            reasoning=(
                f"Found {len(historical)} historical incident(s) but none have "
                "recorded outcomes. Unable to determine which interventions were "
                "successful. Please record outcomes for historical incidents to "
                "improve future recommendations."
            ),
            supporting_incidents=[h.incident.incident_id for h in historical],
            warnings=[
                "Historical outcomes not recorded.",
                "Recommendation based on general principles.",
            ],
        )

    def _get_default_action(self, incident: Incident) -> str:
        """Get a default action based on defect type."""
        defaults = {
            "Surface Defect": "Inspect tooling and cutting parameters",
            "Dimensional Error": "Verify calibration and measure tool wear",
            "Vibration": "Check bearings, alignment, and mounting",
            "Temperature Anomaly": "Inspect cooling system and lubrication",
            "Noise": "Inspect bearings and mechanical components",
            "Power Fluctuation": "Check electrical connections and supply",
            "Pressure Drop": "Inspect seals, hoses, and pump",
            "Speed Variation": "Check drive system and encoder",
        }

        return defaults.get(
            incident.defect_type,
            "Perform visual inspection and basic diagnostics",
        )
