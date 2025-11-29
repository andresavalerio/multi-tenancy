from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from ipaddress import IPv4Address

class MachineIn(BaseModel):
    macaddr: str
    ip: IPv4Address
    os: str
    os_ver: str
    # TODO: To properly assign owners we need user creation
    owner: UUID


class Machine(BaseModel):
    macaddr: str
    ip: IPv4Address
    os: str
    os_ver: str
    owner: UUID
    last_access: datetime
    active: bool
    # tenant_id: UUID
