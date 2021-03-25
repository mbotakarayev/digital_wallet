from aiohttp import ClientResponse, hdrs

from app.core.api_connector import APIConnector
from app.core.config import settings


class WalletAPIClient(APIConnector):
    base_url = settings.WALLET_SERVICE_BASE

    async def notify_transaction(self, *, uuid: str) -> ClientResponse:
        return await self.fetch(
            hdrs.METH_POST,
            "api/v1/wallets/notify_transaction", json={"uuid": uuid}
        )
