"""Utility functions for VALD API interactions"""

import requests
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any, Optional


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


def format_date_to_iso8601(date: datetime) -> str:
    """
    Format a datetime object to ISO 8601 format with milliseconds.
    
    Parameters
    ----------
    date : datetime
        DateTime object to format
        
    Returns
    -------
    str
        ISO 8601 formatted string (e.g., '2024-01-01T00:00:00.000Z')
    """
    return date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:23] + "Z"


def post_call(
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


def get_call(
    url: str,
    header: Dict[str, str],
    parameters: Optional[Dict[str, str]] = None
) -> requests.Response:
    """
    Make a GET request to the API.
    
    Parameters
    ----------
    url : str
        The API endpoint URL
    header : dict
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
    
    response = requests.get(url, headers=header)
    
    if response.status_code == 200:
        return response
    else:
        return response.status_code


def put_call(
    url: str,
    header: Dict[str, str],
    data: Dict[str, Any],
    parameters: Optional[Dict[str, str]] = None
) -> None:
    """
    Make a PUT request to the API.
    
    Parameters
    ----------
    url : str
        The API endpoint URL
    header : dict
        HTTP headers (typically with Bearer token)
    data : dict
        JSON payload for the PUT request
    parameters : dict, optional
        Query parameters to append to URL
    """
    if parameters is not None:
        for key, val in parameters.items():
            url = url + key + val
    
    response = requests.put(url, headers=header, json=data)
    
    if response.status_code != 204:
        print(f"Failed to retrieve tenants. Status Code: {response.status_code}")
