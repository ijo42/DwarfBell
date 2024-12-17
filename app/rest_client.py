import httpx
from loguru import logger

_client = None

async def test_connection(base_url: str, token: str) -> bool | str:
    client = None
    try:
        headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}
        logger.debug(f"Testing connection to {base_url} with headers {headers}")
        client = httpx.AsyncClient(base_url=base_url, headers=headers, timeout=httpx.Timeout(3))
        response = await client.get("/api/v1/users/me", headers=headers)
        response.raise_for_status()
        global _client
        _client = client
        return response.json()["data"]["name"]
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred during test connection: {e.response.status_code} ({e.request.url})- {e.response.text}")
        return False
    except Exception as e:
        logger.error(f"An error occurred during test connection: {e}")
        return False
    finally:
        if client is not None:
            await client.aclose()

async def get_client() -> httpx.AsyncClient | None:
    global _client
    if _client is None:
        logger.error(f"An error occurred during request")
        return None
    return _client

async def get(endpoint: str, params: dict = None) -> httpx.Response:
    try:
        client = await get_client()
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
    try:
        client = await get_client()
        response = await client.post(endpoint, data=data, json=json)
        response.raise_for_status()
        return response
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

async def close_client():
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None