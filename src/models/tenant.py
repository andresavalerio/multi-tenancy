from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TenantIn(BaseModel):
    company_name: str


class Tenant(BaseModel):
    id: UUID
    company_name: str
    created_at: datetime