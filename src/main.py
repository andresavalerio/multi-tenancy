from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import logging
import sys
import os

from src.db import init_db, close_db, get_db
from src.redis import init_redis, close_redis
from .api.admin import admin_router
from .api.public import public_router

logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)


async def lifespan(app):
    logger.info("Initializing DB pool...")
    await init_db()
    logger.info("AsyncPG pool was created!")
    logger.info("Starting Redis...")
    init_redis()
    logger.info("Redis client started!")
    yield
    await close_db()
    close_redis()


app = FastAPI(lifespan=lifespan)

app.include_router(admin_router, prefix="/api")
app.include_router(public_router, prefix="/api")
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/testdb")
async def main_db_page(conn = Depends(get_db)):
    rows = await conn.fetch("select * from information_schema.tables;")
    return {"Hello": [dict(r) for r in rows]}


@app.get("/")
async def root():
    return {"msg": "Hello World"}


@app.get("/favicon.ico")
async def favicon():
    file_name = "favicon.ico"
    file_path = os.path.join(app.root_path, "static", file_name)
    return FileResponse(
        path=file_path,
        headers={"Content-Disposition": "attachment; filename=" + file_name},
    )