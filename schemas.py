from pydantic import BaseModel, Field
from typing import Literal, List, Optional

class TicketExtraction(BaseModel):
    """Schema for structured ticket classification and details."""
    
    category: Literal["database", "billing", "account_access", "network", "other"] = Field(
        description="Primary technical domain of the request"
    )
    urgency_level: Literal["low", "medium", "high", "critical"] = Field(
        description="Assessed issue severity based on operational impact"
    )
    requested_actions: List[str] = Field(
        description="List of specific actions requested (e.g., 'password_reset', 'refund', 'db_restart')"
    )
    extracted_error_logs: Optional[str] = Field(
        default=None,
        description="Cleaned error message or stack trace if present in query"
    )
    summary: str = Field(
        description="A concise 1-sentence summary of the ticket stripping out all user identity details"
    )