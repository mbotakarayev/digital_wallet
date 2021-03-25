from typing import IO, Any, Dict, List, Literal, Optional, Tuple, Union
from urllib.parse import urljoin

from aiohttp import ClientResponse, ClientSession


class APIConnector:
    base_url = None
    raise_for_status = True
    verify = None
    auth: Optional[Tuple[str, str]] = None

    def __init__(self, base_url: str = None):
        base_url = base_url or self.base_url
        assert base_url is not None
        self._session = ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self._session.close()

    async def post_fetch(self, response: ClientResponse) -> ClientResponse:
        return response

    async def fetch(
            self,
            method: Literal["GET", "POST", "PUT", "DELETE"],
            resource_path: str,
            *,
            query_params: Optional[Dict[str, str]] = None,
            json: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
            data: Optional[Dict[str, Any]] = None,
            files: Optional[Union[Tuple[str, Tuple[str, IO, ]]]] = None,
            headers: Optional[Dict[str, str]] = None,
            verify: Optional[bool] = None,
            auth: Optional[Tuple[str, str]] = None
    ):
        assert not(files is not None and data is not None), (
            "files"
        )
        data = data or files

        verify = verify or self.verify
        auth = auth or self.auth

        url = urljoin(self.base_url, resource_path)
        response = await self._session.request(
            method, url,
            params=query_params, json=json, data=data, headers=headers, verify_ssl=verify, auth=auth
        )
        if self.raise_for_status:
            print(response)
            response.raise_for_status()
        response = await self.post_fetch(response)
        return response
