"""Youfone API Client Module.

This module provides a class to communicate with the Youfone API.

"""

import httpx

from .const import API_BASE_URL, API_HEADERS, COUNTRY_CHOICES, DEFAULT_COUNTRY


class YoufoneClient:
    """Class to communicate with the Youfone API."""

    def __init__(self, email, password, country, custom_headers=None):
        """Initialize the API to get data.

        Args:
        ----
            email (str): The email associated with the Youfone account.
            password (str): The password associated with the Youfone account.
            country (str): The country code for the Youfone account.
            custom_headers (dict, optional): Custom headers for HTTP requests. Defaults to None.

        """
        self.email = email
        self.password = password
        self.country = None
        self.client = None
        self.customer = None
        self.customer_id = None
        self.custom_headers = custom_headers or {}
        if country not in COUNTRY_CHOICES:
            self.country = DEFAULT_COUNTRY
        else:
            self.country = country
        self.base_api_endpoint = API_BASE_URL.replace(
            f"youfone.{DEFAULT_COUNTRY}", f"youfone.{self.country}"
        )

        # Update API_HEADERS based on self.country
        for key, value in API_HEADERS.items():
            API_HEADERS[key] = value.replace(
                f"youfone.{DEFAULT_COUNTRY}", f"youfone.{self.country}"
            )

    async def start_session(self):
        """Start the httpx session."""
        if self.client is None:
            self.client = httpx.AsyncClient(headers=self.custom_headers, http2=True)

    async def close_session(self):
        """Close the session."""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def __aenter__(self):
        """Async context manager enter method."""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Async context manager exit method."""
        await self.close_session()

    async def request(
        self,
        method,
        path,
        data=None,
        return_json=True,
        expected_status=200,
    ):
        """Send a request to the Youfone API.

        Args:
        ----
            method (str): HTTP method (POST, GET, etc.).
            path (str): Endpoint path.
            data (dict): Request payload.
            return_json (bool): Flag to return JSON response (default: True).
            expected_status (int): Expected HTTP status code.

        Returns:
        -------
            dict or None: Response payload as JSON or None if return_json is False.

        """
        if self.client is None:
            await self.start_session()

        endpoint_path = f"{self.base_api_endpoint}/{path}"
        headers = {**API_HEADERS, **self.custom_headers}
        response = None
        try:
            if method.lower() == "get":
                response = await self.client.get(endpoint_path, headers=headers)
            else:
                response = await self.client.post(
                    endpoint_path, json=data, headers=headers
                )
            if response.status_code == expected_status:
                if return_json:
                    return response.json()
                else:
                    return None
            else:
                raise Exception(
                    f"Request to {endpoint_path} failed with status code {response.status_code}"
                )
        finally:
            if response:
                await response.aclose()  # Use await to close the async response

    async def login(self):
        """Log in to the Youfone API.

        Returns
        -------
            dict: Response payload as JSON.

        """
        data = {"email": self.email, "password": self.password}
        for expected_status in [200]:
            json = await self.request(
                "POST",
                "authentication/login",
                data,
                return_json=True,
                expected_status=expected_status,
            )
            return json
        return False

    async def get_available_cards(self):
        """Retrieve available cards for the Youfone customer.

        Returns
        -------
            dict or False: A dictionary containing the available cards information if the request is successful,
            otherwise False.

        """
        data = {
            "customerId": self.customer_id,
        }
        for expected_status in [200]:
            json = await self.request(
                "POST",
                "Card/GetAvailableCards",
                data,
                return_json=True,
                expected_status=expected_status,
            )
            return json
        return False

    async def get_data(self):
        """Get the customer data from the Youfone API.

        Returns
        -------
            tuple or dict: If successful, returns a dictionary containing customer data.
                           If there's an error, returns a tuple with an error indicator and message.

        """
        try:
            self.customer = await self.login()
            self.customer_id = self.customer.get("customerId")
            for card in self.get_available_cards():
                print(f"Card: {card}")

        except Exception as e:
            error_message = e.args[0] if e.args else str(e)
            return {"error": error_message}
        return {"customer": self.customer}
