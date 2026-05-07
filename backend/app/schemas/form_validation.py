from pydantic import BaseModel
from typing import Optional

class FormValidationRequest(BaseModel):
    """
    Request schema for form validation operations.
    """
    filloutId: str
    userId: str
    projectId: Optional[str] = None 