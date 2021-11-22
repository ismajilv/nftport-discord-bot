from dataclasses import dataclass
from typing import ClassVar

from aiohttp import ClientResponse, ClientSession

from bot.constants import Chains


@dataclass
class NftPortApi:
    BASE_URL: ClassVar[str] = "https://api.nftport.xyz/v0"
    MINT_EASY_URL_ENDPOINT: ClassVar[str] = "mints/easy/urls"

    async def _build_url(self, endpoint: str):
        return self.BASE_URL + "/" + endpoint

    async def _request(self, method: str, endpoint: str, **kwargs) -> ClientResponse:
        url = await self._build_url(endpoint)

        print(f"REQUEST: method={method}; url={url}; kwargs={kwargs}")

        async with ClientSession() as client:
            resp: ClientResponse = await getattr(client, method)(
                url=url,
                **kwargs,
            )

        return resp

    async def mint_with_url(
        self,
        api_key: str,
        file_url: str,
        to_address: str,
        name: str = "Name",
        description: str = "Description",
        chain: Chains = Chains.POLYGON,
    ):
        resp = await self._request(
            "post",
            self.MINT_EASY_URL_ENDPOINT,
            json={
                "file_url": file_url,
                "mint_to_address": to_address,
                "name": name,
                "description": description,
                "chain": chain.value,
            },
            headers={"Authorization": api_key},
        )

        if resp.ok:
            json_ = await resp.json()
            return json_["transaction_external_url"]
