"""
Abstract base translator for converting IQR to native queries.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from app.iqr.models import QueryRepresentation


class BaseTranslator(ABC):
    """Convert a ``QueryRepresentation`` into a database-native query dict."""

    @abstractmethod
    def translate(self, iqr: QueryRepresentation) -> Dict[str, Any]:
        """Return the native query structure for the target database."""
        ...
