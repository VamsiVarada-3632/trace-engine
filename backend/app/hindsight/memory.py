"""
Memory Service

High-level service for managing manufacturing incident memories
using Hindsight as the persistence layer.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.models import (
    Incident,
    IncidentCreate,
    IncidentUpdate,
    HistoricalIncident,
    ActionOutcome,
)
from .client import HindsightClient


class MemoryService:
    """Service for storing and retrieving incident memories."""

    def __init__(self):
        self.client = HindsightClient()

    async def close(self):
        """Close the underlying client."""
        await self.client.close()

    def _incident_to_memory(self, incident: Incident) -> Dict[str, Any]:
        """Convert an Incident to memory format for Hindsight."""
        return {
            "type": "manufacturing_incident",
            "incident_id": incident.incident_id,
            "machine_id": incident.machine_id,
            "machine_type": incident.machine_type,
            "production_line": incident.production_line,
            "timestamp": incident.timestamp.isoformat(),
            "defect_type": incident.defect_type,
            "symptoms": incident.symptoms,
            "sensor_values": incident.sensor_values,
            "operating_conditions": incident.operating_conditions,
            "description": incident.description,
            "suspected_root_cause": incident.suspected_root_cause,
            "confirmed_root_cause": incident.confirmed_root_cause,
            "action_taken": incident.action_taken,
            "action_outcome": incident.action_outcome.value if incident.action_outcome else None,
            "resolution_details": incident.resolution_details,
            "resolution_time_minutes": incident.resolution_time_minutes,
            "technician_notes": incident.technician_notes,
            # Searchable text for semantic retrieval
            "searchable_text": self._build_searchable_text(incident),
        }

    def _build_searchable_text(self, incident: Incident) -> str:
        """Build a searchable text representation of the incident."""
        parts = [
            f"Machine: {incident.machine_id} ({incident.machine_type})",
            f"Line: {incident.production_line}",
            f"Defect: {incident.defect_type}",
            f"Symptoms: {', '.join(incident.symptoms)}",
            f"Description: {incident.description}",
        ]

        if incident.suspected_root_cause:
            parts.append(f"Suspected cause: {incident.suspected_root_cause}")

        if incident.confirmed_root_cause:
            parts.append(f"Confirmed cause: {incident.confirmed_root_cause}")

        if incident.action_taken:
            parts.append(f"Action: {incident.action_taken}")

        if incident.action_outcome:
            parts.append(f"Outcome: {incident.action_outcome.value}")

        if incident.resolution_details:
            parts.append(f"Resolution: {incident.resolution_details}")

        return " | ".join(parts)

    def _memory_to_incident(self, memory: Dict[str, Any]) -> Incident:
        """Convert memory data back to an Incident."""
        content = memory.get("content", memory)

        return Incident(
            incident_id=content["incident_id"],
            machine_id=content["machine_id"],
            machine_type=content["machine_type"],
            production_line=content["production_line"],
            timestamp=datetime.fromisoformat(content["timestamp"]),
            defect_type=content["defect_type"],
            symptoms=content.get("symptoms", []),
            sensor_values=content.get("sensor_values"),
            operating_conditions=content.get("operating_conditions"),
            description=content["description"],
            suspected_root_cause=content.get("suspected_root_cause"),
            confirmed_root_cause=content.get("confirmed_root_cause"),
            action_taken=content.get("action_taken"),
            action_outcome=(
                ActionOutcome(content["action_outcome"])
                if content.get("action_outcome")
                else None
            ),
            resolution_details=content.get("resolution_details"),
            resolution_time_minutes=content.get("resolution_time_minutes"),
            technician_notes=content.get("technician_notes"),
        )

    async def store_incident(self, incident: Incident) -> str:
        """
        Store an incident in Hindsight memory.

        Args:
            incident: The incident to store

        Returns:
            The incident_id
        """
        content = self._incident_to_memory(incident)

        metadata = {
            "machine_id": incident.machine_id,
            "machine_type": incident.machine_type,
            "production_line": incident.production_line,
            "defect_type": incident.defect_type,
            "has_outcome": incident.action_outcome is not None,
            "outcome": incident.action_outcome.value if incident.action_outcome else None,
        }

        await self.client.store_memory(
            memory_id=incident.incident_id,
            content=content,
            metadata=metadata,
        )

        return incident.incident_id

    async def search_similar_incidents(
        self,
        incident: IncidentCreate,
        limit: int = 10,
    ) -> List[HistoricalIncident]:
        """
        Search for historical incidents similar to the given incident.

        Args:
            incident: The current incident to find matches for
            limit: Maximum number of results

        Returns:
            List of similar historical incidents with relevance scores
        """
        # Build search query from incident details
        query_parts = [
            f"Machine type: {incident.machine_type}",
            f"Defect: {incident.defect_type}",
            f"Symptoms: {', '.join(incident.symptoms)}",
            incident.description,
        ]

        if incident.suspected_root_cause:
            query_parts.append(f"Suspected cause: {incident.suspected_root_cause}")

        query = " ".join(query_parts)

        # Add filters for better matching
        filters = {
            "machine_type": incident.machine_type,
            "has_outcome": True,  # Only retrieve incidents with recorded outcomes
        }

        # Search Hindsight
        memories = await self.client.search_memories(
            query=query,
            filters=filters,
            limit=limit,
        )

        # Convert to HistoricalIncident objects
        results = []
        for memory in memories:
            try:
                hist_incident = self._memory_to_incident(memory)
                similarity = memory.get("similarity_score", memory.get("score", 0.5))

                # Determine relevance factors
                relevance_factors = self._compute_relevance_factors(incident, hist_incident)

                results.append(
                    HistoricalIncident(
                        incident=hist_incident,
                        similarity_score=similarity,
                        relevance_factors=relevance_factors,
                    )
                )
            except Exception:
                # Skip malformed memories
                continue

        return results

    def _compute_relevance_factors(
        self,
        current: IncidentCreate,
        historical: Incident,
    ) -> List[str]:
        """Compute why a historical incident is relevant."""
        factors = []

        if current.machine_id == historical.machine_id:
            factors.append("Same machine")

        if current.machine_type == historical.machine_type:
            factors.append("Same machine type")

        if current.production_line == historical.production_line:
            factors.append("Same production line")

        if current.defect_type == historical.defect_type:
            factors.append("Same defect type")

        # Check symptom overlap
        current_symptoms = set(s.lower() for s in current.symptoms)
        hist_symptoms = set(s.lower() for s in historical.symptoms)
        overlap = current_symptoms & hist_symptoms

        if overlap:
            factors.append(f"Shared symptoms: {', '.join(overlap)}")

        return factors

    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Retrieve a specific incident by ID."""
        memory = await self.client.get_memory(incident_id)
        if memory:
            return self._memory_to_incident(memory)
        return None

    async def update_incident_outcome(
        self,
        incident_id: str,
        update: IncidentUpdate,
    ) -> Optional[Incident]:
        """
        Update an incident with its outcome.

        Args:
            incident_id: The incident to update
            update: The outcome information

        Returns:
            Updated incident or None if not found
        """
        incident = await self.get_incident(incident_id)
        if not incident:
            return None

        # Update fields
        incident.action_taken = update.action_taken
        incident.action_outcome = update.action_outcome
        incident.confirmed_root_cause = update.confirmed_root_cause or incident.confirmed_root_cause
        incident.resolution_details = update.resolution_details
        incident.resolution_time_minutes = update.resolution_time_minutes
        incident.technician_notes = update.technician_notes

        # Store updated incident
        content = self._incident_to_memory(incident)
        metadata = {
            "machine_id": incident.machine_id,
            "machine_type": incident.machine_type,
            "production_line": incident.production_line,
            "defect_type": incident.defect_type,
            "has_outcome": True,
            "outcome": incident.action_outcome.value,
        }

        await self.client.update_memory(
            memory_id=incident_id,
            content=content,
            metadata=metadata,
        )

        return incident

    async def get_machine_history(
        self,
        machine_id: str,
        limit: int = 50,
    ) -> List[Incident]:
        """
        Get incident history for a specific machine.

        Args:
            machine_id: The machine identifier
            limit: Maximum number of results

        Returns:
            List of incidents for this machine
        """
        memories = await self.client.list_memories(
            filters={"machine_id": machine_id},
            limit=limit,
        )

        incidents = []
        for memory in memories:
            try:
                incidents.append(self._memory_to_incident(memory))
            except Exception:
                continue

        # Sort by timestamp descending
        incidents.sort(key=lambda x: x.timestamp, reverse=True)
        return incidents

    async def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics from memory."""
        memories = await self.client.list_memories(limit=1000)

        total = len(memories)
        with_outcome = 0
        outcomes = {"SUCCESS": 0, "PARTIAL": 0, "FAILED": 0, "UNKNOWN": 0}
        machines = set()
        defect_types = {}

        for memory in memories:
            content = memory.get("content", memory)
            machines.add(content.get("machine_id"))

            defect = content.get("defect_type")
            if defect:
                defect_types[defect] = defect_types.get(defect, 0) + 1

            outcome = content.get("action_outcome")
            if outcome:
                with_outcome += 1
                outcomes[outcome] = outcomes.get(outcome, 0) + 1

        return {
            "total_incidents": total,
            "incidents_with_outcome": with_outcome,
            "unique_machines": len(machines),
            "outcome_distribution": outcomes,
            "defect_type_distribution": defect_types,
        }
