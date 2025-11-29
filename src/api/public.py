from typing import List, Optional
from fastapi import APIRouter, Header, Depends, HTTPException
from src.models.machine import Machine, MachineIn
import asyncpg
import logging

from src.db import get_db
from src.redis import get_redis, log_redis_info

logger = logging.getLogger("app_logger")

public_router = APIRouter(
    prefix="/public", tags=["public"], responses={404: {"description": "Not found"}}
)

async def check_tenant(conn, tid):
    found = await conn.fetchval(
        "select exists(select 1 from multitenancy.tenants where id = $1);", tid
    )
    return found


async def validate_or_insert_tenant(conn, redis, tid):
    # Search the cache (Dragonfly) for the tenant_id key
    # If not found then check if it exists in the database
    if not redis.sismember("tenants", tid):
        # Should exist on the db multitenancy.tenants
        try:
            found = await check_tenant(conn, tid)
        except asyncpg.exceptions.DataError as err:
            logger.error(err)
            raise HTTPException(
                status_code=422, detail=f"Invalid TenantId {tid}, not UUID formatted!"
            )
        # If it exists then insert on cache
        if found:
            redis.sadd("tenants", tid)
        # If not exists -> error (invalid tenant)
        else:
            raise HTTPException(status_code=404, detail="TenantId does not exist!")


@public_router.get("/")
async def public_page():
    return {"msg": f"Hello from public"}


async def insert_machine(conn, m: MachineIn, tid):
    async with conn.transaction():
        await conn.execute("set local role application_user;")
        await conn.execute(
            "select set_config('app.current_tenant', $1, true);", tid
        )
        macaddr = await conn.fetchval(
            """
            insert into application.machines (macaddr, ip, os, os_ver, owner, tenant_id)
            values ($1, $2, $3, $4, $5, $6)
            returning macaddr;""",
            m.macaddr,
            m.ip,
            m.os,
            m.os_ver,
            m.owner,
            tid,
        )
        return macaddr


@public_router.post("/machines", status_code=201)
async def create_machine(machine: MachineIn, x_tenantid: Optional[str] = Header(None), conn = Depends(get_db), redis = Depends(get_redis)):
    logger.debug(f"Received TenantId: {x_tenantid}")

    if x_tenantid is None:
        raise HTTPException(status_code=400, detail="Header X-TenantId is required!")

    await validate_or_insert_tenant(conn, redis, x_tenantid)
    log_redis_info()

    try:
        macaddr = await insert_machine(conn, machine, x_tenantid)
    except asyncpg.exceptions.UniqueViolationError as err:
        logger.error(err)
        raise HTTPException(
            status_code=409, detail=f"Machine {machine.macaddr} already exists!"
        )
    except asyncpg.exceptions.InsufficientPrivilegeError as err:
        logger.error(err)
        raise HTTPException(
            status_code=403,
            detail=f"Tenant {x_tenantid} doesn't have permission to create machine {machine.macaddr}!",
        )

    return {"ok": f"Machine {macaddr} was created!"}


async def get_machines(conn, tid):
    async with conn.transaction():
        await conn.execute("set local role application_user;")
        await conn.execute(
            "select set_config('app.current_tenant', $1, true);", tid
        )
        machines = await conn.fetch("select * from application.machines;")
        return machines


@public_router.get("/machines")
async def list_machines(x_tenantid: Optional[str] = Header(None), conn = Depends(get_db), redis = Depends(get_redis)) -> List[Machine]:
    logger.debug(f"Received TenantId: {x_tenantid}")

    if x_tenantid is None:
        raise HTTPException(status_code=400, detail="Header X-TenantId is required!")

    await validate_or_insert_tenant(conn, redis, x_tenantid)
    log_redis_info()

    # Return machines w/ tenant isolation assuming is correct with its origin either from cache or DB.
    machines = await get_machines(conn, x_tenantid)
    parsed_machines: List[Machine] = [Machine(**dict(m)) for m in machines]
    return parsed_machines
