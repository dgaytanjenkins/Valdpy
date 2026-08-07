"""Utility functions for VALD API interactions"""

import requests
import pandas as pd
import json
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional


ALLOWED_TIMEZONES = {
    "UTC",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
}

def convert_ticks_to_datetime(ticks: float) -> pd.Timestamp:
    """
    Convert .NET ticks (100-nanosecond intervals since 0001-01-01) to UTC datetime.
    
    Parameters
    ----------
    ticks : float
        .NET ticks value
        
    Returns
    -------
    pd.Timestamp
        Converted UTC datetime
    """
    # .NET ticks offset: seconds from year 1 to 1970
    TICKS_OFFSET = 62135596800
    # Convert ticks to seconds (ticks are in 100-nanosecond intervals)
    seconds = (ticks / 10_000_000) - TICKS_OFFSET
    return pd.to_datetime(seconds, unit='s', utc=True)


def read_credentials(filepath: str = 'vald_api_cred.txt') -> Dict[str, str]:
    """
    Read credentials from a JSON file.
    
    Parameters
    ----------
    filepath : str
        Path to the credentials JSON file (default: 'vald_api_cred.txt')
        Expected format: {"client_id": "...", "client_secret": "...", "tenant_id": "..."}
    
    Returns
    -------
    dict
        Dictionary containing 'client_id', 'client_secret', and 'tenant_id'
    """
    with open(filepath, 'r') as f:
        creds = json.load(f)
    return creds


def format_date_to_iso8601(
    date_entry: datetime | date | str,
    input_timezone: str | None = "America/Los_Angeles",
) -> str:
    """
    Format a date/datetime value to ISO 8601 in UTC.

    Accepted string formats:
    - dd/mm/yyyy
    - dd/mm/yyyy hh:mm
    - dd/mm/yyyy hh:mm:ss

    If no time is present, midnight is assumed.
    """
    if isinstance(date_entry, str):
        value = date_entry.strip()

        dt = None
        for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y"):
            try:
                dt = datetime.strptime(value, fmt)
                break
            except ValueError:
                continue

        if dt is None:
            raise ValueError(
                "Invalid date format. Use 'dd/mm/yyyy' or 'dd/mm/yyyy hh:mm'."
            )

    elif isinstance(date_entry, date) and not isinstance(date_entry, datetime):
        dt = datetime.combine(date_entry, datetime.min.time())
    elif isinstance(date_entry, datetime):
        dt = date_entry
    else:
        raise TypeError("date_entry must be datetime, date, or str")


    if dt.tzinfo is None:
        if input_timezone is None:
            raise ValueError("input_timezone is required for naive datetimes")

        if input_timezone not in ALLOWED_TIMEZONES:
            raise ValueError(
                f"Invalid timezone '{input_timezone}'. "
                f"Allowed values: {sorted(ALLOWED_TIMEZONES)}"
            )

        dt = dt.replace(tzinfo=ZoneInfo(input_timezone))

    utc_date = dt.astimezone(timezone.utc)
    return utc_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:23] + "Z"


def token_post_call(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> requests.Response:
    """
    Make a POST request to the API.
    
    Parameters
    ----------
    url : str
        The API endpoint URL
    data : dict, optional
        POST data payload
    headers : dict, optional
        HTTP headers (default: application/x-www-form-urlencoded)
        
    Returns
    -------
    requests.Response
        Response object if status code is 200, empty string otherwise
    """
    if headers is None:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    if data is not None:
        response = requests.post(url, data=data, headers=headers)
    else:
        response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        return response
    else:
        print(f"Failed to obtain token. Status Code: {response.status_code}, Response: {response.text}")
        return ''

def post_call(
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        parameters: Optional[Dict[str, str]] = None
) -> requests.Response:
    """
    Make a POST request to the API.
    
    Parameters
    ----------
    url : str
        The API endpoint URL
    data : dict, optional
        POST data payload
    headers : dict, optional
        HTTP headers (default: application/json)
        
    Returns
    -------
    requests.Response
        Response object if status code is 200, empty string otherwise
    """
    if parameters is not None:
        for key, val in parameters.items():
            url = url + key + val

    if headers is None:
        headers = {"Content-Type": "application/json"}
    # print(f"Making POST request to {url} with headers {headers} and data {data}...")
    if data is not None:
        try:
            response = requests.post(url, headers=headers, json=data)
            # response.raise_for_status()  # Raise exception for bad status codes
            # return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
    else:
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()  # Raise exception for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

def get_call(
    url: str,
    headers: Dict[str, str],
    parameters: Optional[Dict[str, str]] = None
) -> requests.Response:
    """
    Make a GET request to the API.
    
    Parameters
    ----------
    url : str
        The API endpoint URL
    headers : dict
        HTTP headers (typically with Bearer token)
    parameters : dict, optional
        Query parameters to append to URL
        
    Returns
    -------
    requests.Response or int
        Response object if successful, status code if error occurs
    """
    if parameters is not None:
        for key, val in parameters.items():
            url = url + key + val
    # print(f"Making GET request to {url} with headers {headers}...")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response
    else:
        return response


def put_call(
    url: str,
    headers: Dict[str, str],
    data: Dict[str, Any],
    parameters: Optional[Dict[str, str]] = None
) -> None:
    """
    Make a PUT request to the API.
    
    Parameters
    ----------
    url : str
        The API endpoint URL
    headers : dict
        HTTP headers (typically with Bearer token)
    data : dict
        JSON payload for the PUT request
    parameters : dict, optional
        Query parameters to append to URL
    """
    if parameters is not None:
        for key, val in parameters.items():
            url = url + key + val
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code != 204:
        print(f"Failed to retrieve tenants. Status Code: {response.status_code}")

def delete_call(
    url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        parameters: Optional[Dict[str, str]] = None
) -> requests.Response:
    """
    Make a DELETE request to the API.
    
    Parameters
    ----------
    url : str
        The API endpoint URL
    data : dict, optional
        DELETE data payload
    headers : dict, optional
        HTTP headers (default: application/json)
        
    Returns
    -------
    requests.Response
        Response object if status code is 200, empty string otherwise
    """
    if parameters is not None:
        for key, val in parameters.items():
            url = url + key + val

    if headers is None:
        headers = {"Content-Type": "application/json"}
    
    if data is not None:
        try:
            response = requests.delete(url, headers=headers, json=data)
            response.raise_for_status()  # Raise exception for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    else:
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()  # Raise exception for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None