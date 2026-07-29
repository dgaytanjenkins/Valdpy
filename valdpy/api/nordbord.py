"""NordBord API client for VALD Performance"""

from typing import Optional, Dict, Any

import pandas as pd
import numpy as np
from datetime import datetime
import re

from ..utils import get_call,format_date_to_iso8601


class NordBordAPI:
    """
    Client for NordBord (leg press strength) test data from VALD Performance.
    
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
            self.url = 'https://prd-use-api-externalnordbord.valdperformance.com'
        elif region == 'Australia':
            self.url = 'https://prd-aue-api-externalnordbord.valdperformance.com'
        elif region == 'Europe':
            self.url = 'https://prd-euw-api-externalnordbord.valdperformance.com'
        else:
            raise ValueError(f"Region '{region}' not supported. Use 'USA', 'Australia', or 'Europe'.")
    
    def get_tests_info(self, modifiedDate: str, profile_id: Optional[str] = None, pattern = r"^([0-2][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4})$") -> pd.DataFrame:
        """
        Get test information from a specific date.
        
        Parameters
        ----------
        modifiedDate : str
            Test modified date (ISO 8601 format or 'dd/mm/yyyy'). The default pattern for 'dd/mm/yyyy' is r"^([0-2][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4})$"
        profile_id : str, optional
            Filter by specific profile ID
            
        Returns
        -------
        pd.DataFrame
            Tests information
        """
        # Parse date
        if 'tests_df' in dir(self):
            delattr(self,'tests_df')
        # Use Modified date only 
        if isinstance(modifiedDate,datetime):
            pass
        elif isinstance(modifiedDate,str) and re.match(pattern, modifiedDate):
            modifiedDate = datetime.strptime(modifiedDate, "%d/%m/%Y")
        else:
            print('Modified date does not match format - dd/mm/yyyy, ie 01/01/1900')
        parameters = {
            '/tests/v2': '',
            '?TenantId=': self.tenant_id,
            '&ModifiedFromUtc=': format_date_to_iso8601(modifiedDate.replace(hour=5)).replace(':','%3A'),
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
            '/tests/': test_id,
            '?tenantId=': self.tenant_id,
        }
        
        response = get_call(self.url, self.header, parameters=parameters)
        
        if response != '' and not isinstance(response, int):
            self.test = response.json()
            return self.test
        
        return None
    
    def get_force_trace(self, test_id: str) -> pd.DataFrame:
        """
        Get force trace for a specific test.
        
        Parameters
        ----------
        test_id : str
            Test ID
            
        Returns
        -------
        pd.DataFrame
            Force trace data
        """
        parameters = {
            '/tests':'',
            '/':test_id,
            '/nordbordtrace':'',
            '?TenantId=':self.tenant_id,
        }
        response = get_call(self.url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            self.raw = response.json()
            self.raw['forces'] = pd.DataFrame(response.json()['forces'])
            # ticks would be reported in nanoseconds but conversion does not align as off by a magnitude of 100.
            if 1e7 / np.mean(np.diff(self.raw['forces']['ticks'])) < 100:
                samplingFreq = 50
            elif 1e7 / np.mean(np.diff(self.raw['forces']['ticks'])) < 200:
                samplingFreq = 100
            elif 1e7 / np.mean(np.diff(self.raw['forces']['ticks'])) < 300:
                samplingFreq = 200
            elif 1e7 / np.mean(np.diff(self.raw['forces']['ticks'])) < 400:
                samplingFreq = 300
            else:
                samplingFreq = 400
            self.raw['forces']['sample_number'] = np.arange(len(self.raw['forces']))
            self.raw['forces']['time_s'] = self.raw['forces']['sample_number'] * (1/samplingFreq)
            self.raw['forces']['sampling_frequency_hz'] = samplingFreq
            return self.raw['forces']
