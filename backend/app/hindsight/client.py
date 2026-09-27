"""
Hindsight API Client

This module provides the interface for connecting to the Hindsight
persistent memory service.
"""

import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings


class HindsightClient:
    """Client for interacting with the Hindsight memory API."""

    def __init__(self):
        self.base_url = settings.hindsight_api_url
        self.api_key = settings.hindsight_api_key
        self.namespace = settings.hindsight_namespace
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def store_memory(
        self,
        memory_id: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store a memory in Hindsight.

        Args:
            memory_id: Unique identifier for this memory
            content: The memory content to store
            metadata: Optional metadata for filtering/retrieval

        Returns:
            Response from Hindsight API
        """
        client = await self._get_client()

        payload = {
            "namespace": self.namespace,
            "memory_id": memory_id,
            "content": content,
            "metadata": metadata or {},
        }

        response = await client.post("/memories", json=payload)
        response.raise_for_status()
        return response.json()

    async def search_memories(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant memories in Hindsight.

        Args:
            query: Search query (natural language or structured)
            filters: Optional filters (machine_id, defect_type, etc.)
            limit: Maximum number of results

        Returns:
            List of relevant memories with similarity scores
        """
        client = await self._get_client()

        payload = {
            "namespace": self.namespace,
            "query": query,
            "filters": filters or {},
            "limit": limit,
        }

        response = await client.post("/memories/search", json=payload)
        response.raise_for_status()
        return response.json().get("memories", [])

    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: The memory identifier

        Returns:
            Memory content or None if not found
        """
        client = await self._get_client()

        response = await client.get(
            f"/memories/{memory_id}",
            params={"namespace": self.namespace},
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    async def update_memory(
        self,
        memory_id: str,
        content: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update an existing memory.

        Args:
            memory_id: The memory identifier
            content: Updated content
            metadata: Updated metadata

        Returns:
            Updated memory
        """
        client = await self._get_client()

        payload = {
            "namespace": self.namespace,
            "content": content,
            "metadata": metadata or {},
        }

        response = await client.put(f"/memories/{memory_id}", json=payload)
        response.raise_for_status()
        return response.json()

    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: The memory identifier

        Returns:
            True if deleted successfully
        """
        client = await self._get_client()

        response = await client.delete(
            f"/memories/{memory_id}",
            params={"namespace": self.namespace},
        )

        return response.status_code == 204

    async def list_memories(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        List memories with optional filtering.

        Args:
            filters: Optional filters
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of memories
        """
        client = await self._get_client()

        params = {
            "namespace": self.namespace,
            "limit": limit,
            "offset": offset,
        }

        if filters:
            params["filters"] = filters

        response = await client.get("/memories", params=params)
        response.raise_for_status()
        return response.json().get("memories", [])
