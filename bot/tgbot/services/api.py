import logging
import httpx
from typing import Optional, Any, Dict, Union

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str, timeout: float = 240.0, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        data: Optional[Union[dict, str]] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        files: Optional[dict] = None
    ) -> Optional[Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        req_headers = self.headers.copy()
        if headers:
            req_headers.update(headers)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    data=data,
                    json=json,
                    headers=req_headers,
                    files=files,
                    timeout=self.timeout
                )
                resp.raise_for_status()
                # Вернем dict если json, иначе — bytes
                try:
                    return resp.json()
                except Exception:
                    return resp.content
        except httpx.RequestError as exc:
            logger.error(f"Request error while calling {url}: {exc}")
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error response from {url}: {exc.response.status_code} - {exc.response.text}")
        except Exception as exc:
            logger.exception(f"Unexpected error while calling {url}: {exc}")
        return None

    # Методы под каждую операцию

    async def get(self, path: str, params: dict = None, headers: dict = None) -> Optional[Any]:
        return await self._request("GET", path, params=params, headers=headers)

    async def post(self, path: str, json: dict = None, data: dict = None, headers: dict = None, files: dict = None) -> Optional[Any]:
        return await self._request("POST", path, json=json, data=data, headers=headers, files=files)

    async def patch(self, path: str, json: dict = None, headers: dict = None) -> Optional[Any]:
        return await self._request("PATCH", path, json=json, headers=headers)

    async def delete(self, path: str, params: dict = None, headers: dict = None) -> Optional[Any]:
        return await self._request("DELETE", path, params=params, headers=headers)

    # Shortcut для быстрого вызова любых методов
    async def request(self, method: str, path: str, **kwargs) -> Optional[Any]:
        return await self._request(method, path, **kwargs)