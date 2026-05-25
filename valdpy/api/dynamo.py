"""Dynamo API client for VALD Performance"""

import re
from datetime import datetime
from typing import Optional, Dict, Any

import pandas as pd

from ..utils import get_call, format_date_to_iso8601


class DynamoAPI:
    """
    Client for Dynamo (jump/power) test data from VALD Performance.
    
    Parameters
    ----------
    tenant_id : str
        VALD tenant ID
    header : dict
        Authorization header with Bearer token
    region : str, optional
        API region: 'USA', 'Australia', or 'Europe' (default: 'USA')
    """
    
    def __init__(self, tenant_id: str, header: Dict[str, str], region: str = 'USA'):
        self.tenant_id = tenant_id
        self.header = header
        
        if region == 'USA':
            self.url = 'https://prd-use-api-extdynamo.valdperformance.com'
        elif region == 'Australia':
            self.url = 'https://prd-aue-api-extdynamo.valdperformance.com'
        elif region == 'Europe':
            self.url = 'https://prd-euw-api-extdynamo.valdperformance.com'
        else:
            raise ValueError(f"Region '{region}' not supported. Use 'USA', 'Australia', or 'Europe'.")
    
    def get_tests(
        self,
        start_date: datetime | str,
        stop_date: datetime | str,
        modified_date: Optional[str] = None,
        profile_id: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get tests between two dates.
        
        Parameters
        ----------
        start_date : datetime or str
            Start date (format: 'dd/mm/yyyy' or datetime object)
        stop_date : datetime or str
            Stop date (format: 'dd/mm/yyyy' or datetime object)
        modified_date : str, optional
            Filter by modification date
        profile_id : str, optional
            Filter by specific profile ID
            
        Returns
        -------
        pd.DataFrame
            Tests information
            
        Raises
        ------
        AssertionError
            If date range exceeds 180 days
        """
        # Parse dates
        pattern = r"^([0-2][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4})$"
        
        if isinstance(start_date, datetime):
            pass
        elif isinstance(start_date, str) and re.match(pattern, start_date):
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
        else:
            raise ValueError('Start date does not match format - dd/mm/yyyy')
        
        if isinstance(stop_date, datetime):
            pass
        elif isinstance(stop_date, str) and re.match(pattern, stop_date):
            stop_date = datetime.strptime(stop_date, "%d/%m/%Y")
        else:
            raise ValueError('Stop date does not match format - dd/mm/yyyy')
        
        # Validate date range
        assert (stop_date - start_date).days < 180, 'Date range cannot exceed 180 days'
        
        # Build parameters
        parameters = {
            '/v2022q2/teams/': self.tenant_id,
            '/tests': '',
            '?testFromUtc=': format_date_to_iso8601(start_date.replace(hour=0)).replace(':', '%3A'),
            '&testToUtc=': format_date_to_iso8601(stop_date.replace(hour=23)).replace(':', '%3A'),
        }
        
        if modified_date:
            parameters['&modifiedDateUtc='] = modified_date
        if profile_id:
            parameters['&profileId='] = profile_id
        
        response = get_call(self.url, self.header, parameters=parameters)
        
        if response != '' and not isinstance(response, int):
            self.tests_df = pd.DataFrame(response.json()['tests'])
            return self.tests_df
        
        return None
    
    def get_test_results(self, test_id: str) -> pd.DataFrame:
        """
        Get results for a specific test.
        
        Parameters
        ----------
        test_id : str
            Test ID
            
        Returns
        -------
        pd.DataFrame
            Test results data
        """
        parameters = {
            '/v2022q2/teams/': self.tenant_id,
            '/tests/': test_id,
            '/trials': '',
        }
        
        response = get_call(self.url, self.header, parameters=parameters)
        
        if response != '' and not isinstance(response, int):
            self.results_df = pd.DataFrame(response.json())
            return self.results_df
        
        return None
