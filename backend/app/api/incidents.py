"""
Incidents API

Endpoints for reporting, analyzing, and updating manufacturing incidents.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.models import (
    IncidentCreate,
    IncidentUpdate,
    AnalysisResult,
    Incident,
)
from app.services import AnalysisService

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_incident(incident: IncidentCreate) -> AnalysisResult:
    """
    Submit an incident for analysis.

    This endpoint:
    1. Stores the incident in Hindsight memory
    2. Searches for similar historical incidents
    3. Analyzes successful vs failed interventions
    4. Generates an evidence-based recommendation

    Returns the complete analysis including historical evidence.
    """
    service = AnalysisService()
    try:
        result = await service.analyze_incident(incident)
        return result
    finally:
        await service.close()


@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: str) -> Incident:
    """
    Retrieve a specific incident by ID.
    """
    service = AnalysisService()
    try:
        incident = await service.memory.get_incident(incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        return incident
    finally:
        await service.close()


@router.patch("/{incident_id}/outcome", response_model=Incident)
async def record_outcome(incident_id: str, update: IncidentUpdate) -> Incident:
    """
    Record the outcome of a troubleshooting action.

    This endpoint updates the incident with:
    - Action performed
    - Outcome (SUCCESS/PARTIAL/FAILED/UNKNOWN)
    - Confirmed root cause (if determined)
    - Resolution details
    - Resolution time
    - Technician notes

    The updated incident is stored in Hindsight memory for future retrieval.
    """
    service = AnalysisService()
    try:
        incident = await service.memory.update_incident_outcome(incident_id, update)
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        return incident
    finally:
        await service.close()


@router.get("/machine/{machine_id}/memory", response_model=Dict[str, Any])
async def get_machine_memory(machine_id: str) -> Dict[str, Any]:
    """
    Get the accumulated memory for a specific machine.

    Returns:
    - Total incidents
    - Recurring defects
    - Successful interventions
    - Failed interventions
    - Recent incident history
    """
    service = AnalysisService()
    try:
        return await service.get_machine_memory(machine_id)
    finally:
        await service.close()
