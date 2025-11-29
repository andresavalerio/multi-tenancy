from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from src.models.tenant import Tenant, TenantIn
import asyncpg
import logging

from src.db import get_db

logger = logging.getLogger("app_logger")

admin_router = APIRouter(
    prefix="/admin", tags=["admin"], responses={404: {"description": "Not found"}}
)

@admin_router.get("/")
async def admin_page():
    return {"msg": "Hello from admin"}

@admin_router.get("/tenants", status_code=200)
async def list_tenants(conn = Depends(get_db)):
    tenants = await conn.fetch("select * from multitenancy.tenants;")
    parsed_tenants: List[Tenant] = [Tenant(**dict(t)) for t in tenants]
    return parsed_tenants


async def insert_tenant(conn, name):
    tenant_id = await conn.fetchval(
        """
        insert into multitenancy.tenants (company_name)
        values ($1)
        returning id;""",
        name,
    )
    return tenant_id


@admin_router.post("/tenants", status_code=201)
async def create_tenant(tenant: TenantIn, conn = Depends(get_db)):
    name = tenant.company_name

    try:
        tid = await insert_tenant(conn, name)
    except asyncpg.exceptions.UniqueViolationError as err:
        logger.error(err)
        raise HTTPException(
            status_code=409,
            detail=f"Tenant {name} already exists!"
        )

    return {"ok": f"Tenant {tid} was created!"}


async def delete_tenant(conn, name):
    async with conn.transaction():
        await conn.execute(
            """
            delete from multitenancy.tenantgroups using multitenancy.tenants
                where tenant_id = tenants.id and tenants.company_name = $1;""",
            name,
        )
        tid = await conn.fetchval(
            """
            delete from multitenancy.tenants
                where company_name = $1
                returning id;""",
            name,
        )
        return tid


@admin_router.delete("/tenants", status_code=200)
async def remove_tenant(tenant: TenantIn, conn = Depends(get_db)):
    name = tenant.company_name

    tid = await delete_tenant(conn, name)

    if tid is None:
        logger.info(f"Tenant {name} was not found!")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return {"ok": f"Tenant {name} was deleted!"}