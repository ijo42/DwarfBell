# -*- coding: utf-8 -*-

from fastapi import APIRouter

from app.settings import get_settings

cfg = get_settings()

root_router = APIRouter(
    prefix="",
    tags=["root"],
    responses={404: {"description": "Not found"}},
)


@root_router.get("/")
async def root() -> dict:
    return {"message": "Hello World"}
