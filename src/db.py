import asyncpg

pool: asyncpg.pool.Pool = None

# pass the fastapi app to make use of lifespan asgi events
# admin:admin is superuser with bypassrls
# application_user:mypwd is an application_user
DSN = "postgresql://admin:admin@0.0.0.0:5432/postgres"

async def init_db():
    global pool
    pool = await asyncpg.create_pool(dsn=DSN)
    return pool

async def close_db():
    global pool
    await pool.close()

# Dependency
async def get_db():
    async with pool.acquire() as conn:
        yield conn
