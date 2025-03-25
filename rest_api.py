"""
Model REST API and a respons using Pydantic

"""

import requests
from requests.exceptions import HTTPError, Timeout
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    IPvAnyAddress,
    ValidationError,
)


class IPGeo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ip: IPvAnyAddress  # Validate an IPv4 or IPv6 address. (REQUIRED)
    country: str | None = None
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    country_code3: str | None = Field(default=None, min_length=2, max_length=3)
    city: str | None = None
    region: str | None = None
    timezone: str | None = None
    organization_name: str | None = None

    @field_validator("organization_name", mode="after")
    @classmethod
    def set_unknown_to_none(cls, value: str):
        # The api returns "unknown" if organizayion_name is None
        # Conversion  is handled here -> None
        # organization_name: str | None = None
        if value.casefold() == "unknown":
            return None
        return value


# geo = IPGeo(
#     ip="8.8.8.8", country="test", country_code3="USA", organization_name="Unknown"
# )
# print(geo)


def create_ip_url(ip_address: str) -> str:
    return f"https://get.geojs.io/v1/geo/{ip_address}.json"


url = create_ip_url(ip_address="23.62.177.155")
data = None
try:
    response = requests.get(url)
    response.raise_for_status()
    response_json = response.json()

    data = IPGeo.model_validate(response.json())
    print(data)
except HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Timeout:
    print("The request timed out")
except Exception as err:
    print(f"Other error occurred: {err}")
finally:
    print("Success!")
