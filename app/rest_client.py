import httpx
from loguru import logger
from contextlib import asynccontextmanager

_cached_base_url = None
_cached_token = None

async def init_rest_client(endpoint: str, token: str) -> None:
    if len(endpoint) * len(token) == 0:
        logger.error("Base URL or token not found in Redis during initialization")
    else:
        name = await test_connection(endpoint, token)
        if not name:
            logger.error("Base URL or token from redis incorrect during initialization")
        else:
            global _cached_base_url, _cached_token
            _cached_base_url, _cached_token = endpoint, token
            logger.info(f"REST client initialized successfully - {name}")

@asynccontextmanager
async def get_client():
    if _cached_base_url is None or _cached_token is None:
        logger.error("REST client not initialized")
        raise RuntimeError("REST client not initialized. Call init_rest_client() first.")

    headers = {"Authorization": f"Token {_cached_token}", "Content-Type": "application/json"}
    # noinspection PyTypeChecker
    async with httpx.AsyncClient(base_url=_cached_base_url, headers=headers, timeout=httpx.Timeout(3)) as client:
        yield client

async def test_connection(base_url: str, token: str) -> bool | str:
    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
    logger.debug(f"Testing connection to {base_url} with headers {headers}")
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=httpx.Timeout(3)) as client:
        try:
            response = await client.get("/api/v1/users/me")
            response.raise_for_status()
            return response.json()["data"]["name"]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred during test connection: {e.response.status_code} ({e.request.url})- {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"An error occurred during test connection: {e}")
            return False

async def get(endpoint: str, params: dict = None) -> httpx.Response:
    async with get_client() as client:
        try:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

async def post(endpoint: str, data: dict = None, json: dict = None) -> httpx.Response:
    async with get_client() as client:
        try:
            response = await client.post(endpoint, data=data, json=json)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

async def get_all_tasks() -> list | None:
    try:
        async with get_client() as client:
            response = await client.get("/api/v1/challenges")
            response.raise_for_status()
            return response.json()['data']
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to fetch tasks. Status: {e.response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        return None