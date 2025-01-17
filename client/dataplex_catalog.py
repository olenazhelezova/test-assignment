import json
import asyncio
import httpx
from exceptions import ApiClientException, DataException


class DataplexCatalogClient:
    def __init__(self, service_endpoint: str):
        self._client = httpx.AsyncClient(base_url=service_endpoint + "dataplex_catalog")
        self._delay = 2
        self._retries = 5

    async def _initiate_resource_transfer(self, url, resource):
        response = await self._client.post(url, json=resource)

        result = None
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            raise ApiClientException("Unable to decode response") from e

        if response.is_client_error:
            raise DataException(
                f'Error "{result["error"]}" when initiating {resource["type"]} "{resource["id"]}" transfer'
            )
        if response.is_error:
            raise ApiClientException(
                f"Server Error {result["error"]}."
            )  # worth a retry probably

        return result

    async def _poll_with_backoff(self, url):
        i = 0
        timeout = self._delay

        while i < self._retries:
            response = await self._client.get(url)

            data = None
            try:
                data = response.json()
            except json.JSONDecodeError:
                pass  # Don't want to break the loop in case it's a one-time occasion

            if data and data["transfer_finished"]:
                return True

            await asyncio.sleep(timeout)
            i += 1
            timeout *= 2

        raise ApiClientException("Unable to validate resource transfer: timeout.")

    async def initiate_entrygroup_transfer(self, entry_group: dict):
        return await self._initiate_resource_transfer(
            f"/EntryGroup/{entry_group["id"]}", resource=entry_group
        )

    async def poll_for_entrygroup_transfer_completion(self, resource_id):
        return await self._poll_with_backoff(f"/EntryGroup/{resource_id}")

    async def initiate_tag_template_transfer(self, tag_template: dict):
        return await self._initiate_resource_transfer(
            f"/TagTemplate/{tag_template["id"]}", resource=tag_template
        )

    async def poll_for_tag_template_transfer_completion(self, resource_id):
        return await self._poll_with_backoff(f"/TagTemplate/{resource_id}")

    def __del__(self):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(self._client.aclose())
        else:
            # in case the event loop has already finished runnign we still want to cleanup properly
            loop.run_until_complete(self._client.aclose())
