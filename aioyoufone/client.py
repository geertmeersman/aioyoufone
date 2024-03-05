"""Youfone API Client Module.

This module provides a class to communicate with the Youfone API.

"""

import logging

import httpx

from .const import API_BASE_URL, API_HEADERS, COUNTRY_CHOICES, DEFAULT_COUNTRY

_LOGGER = logging.getLogger(__name__)


class YoufoneClient:
    """Class to communicate with the Youfone API."""

    def __init__(self, email, password, country, custom_headers=None, debug=False):
        """Initialize the API to get data.

        Args:
        ----
            email (str): The email associated with the Youfone account.
            password (str): The password associated with the Youfone account.
            country (str): The country code for the Youfone account.
            custom_headers (dict, optional): Custom headers for HTTP requests. Defaults to None.
            debug (bool, optional): Whether to enable debug mode. Defaults to False.

        """
        self.email = email
        self.password = password
        self.country = None
        self.client = None
        self.customer = None
        self.customer_id = None
        self.security_key = None  # Store the security key
        self.custom_headers = custom_headers or {}
        self.debug = debug  # Set debug mode
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

        # Add security key to headers if available
        if self.security_key:
            headers["securitykey"] = self.security_key

        response = None
        try:
            if method.lower() == "get":
                response = await self.client.get(endpoint_path, headers=headers)
            else:
                response = await self.client.post(
                    endpoint_path, json=data, headers=headers
                )
            if self.debug:  # Check if debug mode is active
                _LOGGER.debug(
                    f"HTTP {method} {endpoint_path} - Status: {response.status_code}"
                )
                _LOGGER.debug(f"Request Headers: {headers}")
                _LOGGER.debug(f"Response Headers: {response.headers}")
                _LOGGER.debug(f"Response Content: {response.content}")

            if response.status_code == expected_status:
                # Update security key if present in response headers
                if "securitykey" in response.headers:
                    self.security_key = response.headers["securitykey"]

                if return_json:
                    return response.json()
                else:
                    return response.text()
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

    async def get_sim_only(self, data):
        """Retrieve SIM-only options from the Youfone API.

        Args:
        ----
            data (dict): The payload to be passed to the GetSimOnly endpoint.

        Returns:
        -------
            dict or None: A dictionary containing SIM-only information or None if the request fails.

        """
        for expected_status in [200]:
            json = await self.request(
                "POST",
                "Card/GetSimOnly",
                data,
                return_json=True,
                expected_status=expected_status,
            )
            return json
        return None

    async def get_abonnement(self, data):
        """Retrieve SIM-only abonnement information from the Youfone API.

        Args:
        ----
            data (dict): The payload to be passed to the GetAbonnement endpoint.

        Returns:
        -------
            dict or None: A dictionary containing SIM-only abonnement information or None if the request fails.

        """
        for expected_status in [200]:
            json = await self.request(
                "POST",
                "Products/SimOnly/GetAbonnement",
                data,
                return_json=True,
                expected_status=expected_status,
            )
            return json
        return None

    def transform_sim_only_usage(self, json_data):
        """Transform the given JSON data representing SIM-only usage into a specific format.

        This function takes a JSON object representing SIM-only usage and transforms it into a list of dictionaries
        containing information about usage progress bars associated with the SIM-only plan.

        Args:
        ----
            json_data (dict): The JSON object representing the SIM-only usage.

        Returns:
        -------
            list: A list of dictionaries, each containing information about a usage progress bar.

        """
        transformed_data = []
        # Iterate over each progress bar
        for progress_bar in json_data.get("progressBars", []):
            transformed_bar = {
                "is_unlimited": progress_bar.get("isUnlimited"),
                "current": progress_bar.get("leftSideData"),
                "max": progress_bar.get("rightSideData"),
                "percentage": progress_bar.get("percentage"),
                "remaining_days": json_data.get("remainingDays"),
                "type": progress_bar.get("type"),
                "units": progress_bar.get("units"),
            }
            # Convert camelCase keys to snake_case
            transformed_bar = {
                self.convert_camel_to_snake(k): v for k, v in transformed_bar.items()
            }
            transformed_data.append(transformed_bar)
        return transformed_data

    def convert_camel_to_snake(self, name):
        """Convert a camelCase string to snake_case.

        Args:
        ----
            name (str): The camelCase string to convert.

        Returns:
        -------
            str: The snake_case representation of the input string.

        """
        s1 = name[0].lower()
        for c in name[1:]:
            if c.isupper():
                s1 += "_" + c.lower()
            else:
                s1 += c
        return s1

    async def fetch_data(self):
        """Get the customer data from the Youfone API.

        Returns
        -------
            dict: A dictionary containing customer data or an error indicator and message.

        """
        try:
            self.customer = {
                self.convert_camel_to_snake(k): v
                for k, v in (await self.login()).items()
            }
            self.customer_id = self.customer.get("customer_id")
            sim_only = []
            if self.customer.get("has_simonly"):
                for card in await self.get_available_cards():
                    card_type = card.get("cardType")
                    if card_type == "SIM_ONLY":
                        for options in card.get("options"):
                            usage = await self.get_sim_only(options)
                            if usage:
                                subscription_info = await self.get_abonnement(options)
                                if subscription_info:
                                    sim_only.append(
                                        {
                                            "msisdn": options.get("msisdn", ""),
                                            "usage": self.transform_sim_only_usage(
                                                usage
                                            ),
                                            "subscription_info": {
                                                self.convert_camel_to_snake(k): v
                                                for k, v in subscription_info.get(
                                                    "generalInfo", ""
                                                ).items()
                                            },
                                        }
                                    )

        except Exception as e:
            error_message = e.args[0] if e.args else str(e)
            return {"error": error_message}
        return {"customer": self.customer, "sim_only": sim_only}
