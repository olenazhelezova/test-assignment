import json
import httpx
from exceptions import NetworkingException, DataException, ApiClientException


class DataCatalogClient:
    """
    A client for interacting with the data catalog service. It provides methods to retrieve entry groups
    and tag templates from the service endpoint.
    """
    def __init__(self, service_endpoint: str):
        """
        Initializes the DataCatalogClient with the given service endpoint.
        """
        self._client = httpx.Client(base_url=service_endpoint)

    def _perform_request(self, method, path, payload=None):
        """
        Sends an HTTP request to the data catalog service and returns the parsed JSON response.
        """
        response = self._client.request(method=method, url=path, json=payload)

        result = None
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            raise NetworkingException("Could not retrieve resources.") from e

        if response.is_error:  # but response json was parsed successfully
            raise ApiClientException("Error response in unsupported format")

        return result

    def _validate_resource(self, data: dict):
        """
        Validates that each resource in the data has an id and a type.
        """
        for record in data:
            if "id" not in record:
                raise DataException("Resource ID not found.")
            if "type" not in record:
                raise DataException("Resource type not found")

    def get_entry_groups(self) -> list[dict]:
        """
        Retrieves a list of entry groups from the data catalog.
        """
        data = self._perform_request("GET", "/data_catalog/EntryGroup")
        self._validate_resource(data)

        return data

    def get_tag_templates(self) -> list[dict]:
        """
        Retrieves a list of tag templates from the data catalog.
        """
        data = self._perform_request("GET", "/data_catalog/TagTemplate")
        self._validate_resource(data)

        return data
