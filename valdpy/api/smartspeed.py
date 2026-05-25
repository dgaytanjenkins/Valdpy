"""SmartSpeed API client for VALD Performance"""

from typing import Optional, Dict, Any

import pandas as pd

from ..utils import get_call


class SmartSpeedAPI:
    """
    Client for SmartSpeed (timing gate) test data from VALD Performance.
    
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
            self.url = 'https://prd-use-api-extsmartspeed.valdperformance.com'
        elif region == 'Australia':
            self.url = 'https://prd-aue-api-extsmartspeed.valdperformance.com'
        elif region == 'Europe':
            self.url = 'https://prd-euw-api-extsmartspeed.valdperformance.com'
        else:
            raise ValueError(f"Region '{region}' not supported. Use 'USA', 'Australia', or 'Europe'.")
    
    def get_tests_info(self, date: str, profile_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get test information from a specific date.
        
        Parameters
        ----------
        date : str
            Test date (ISO 8601 format or 'dd/mm/yyyy')
        profile_id : str, optional
            Filter by specific profile ID
            
        Returns
        -------
        pd.DataFrame
            Tests information
        """
        parameters = {
            '/tests': '',
            '?TenantId=': self.tenant_id,
            '&ModifiedFromUtc=': date,
        }
        
        if profile_id:
            parameters['&ProfileId='] = profile_id
        
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
            Test results
        """
        parameters = {
            '/v2019q3/': '',
            'teams/': self.tenant_id,
            '/tests/': test_id,
            '/trials': '',
        }
        
        response = get_call(self.url, self.header, parameters=parameters)
        
        if response != '' and not isinstance(response, int):
            self.results_df = pd.DataFrame(response.json())
            return self.results_df
        
        return None
