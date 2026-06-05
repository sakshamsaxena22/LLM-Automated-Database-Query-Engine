from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Natural language query")


class QueryResponse(BaseModel):
    generated_query: Dict[str, Any]
    count: int
    results: List[Dict[str, Any]]
    raw_response: Dict[str, Any]
    execution_time_ms: Optional[float] = None
