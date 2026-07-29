"""ForceFrame API client for VALD Performance"""

from typing import Optional, Dict, Any
from datetime import datetime
import pandas as pd
import re

from ..utils import get_call,format_date_to_iso8601


class ForceFrameAPI:
    """
    Client for ForceFrame test data from VALD Performance.
    
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
            self.url = 'https://prd-use-api-externalforceframe.valdperformance.com'
        elif region == 'Australia':
            self.url = 'https://prd-aue-api-externalforceframe.valdperformance.com'
        elif region == 'Europe':
            self.url = 'https://prd-euw-api-extforceframe.valdperformance.com'
        else:
            raise ValueError(f"Region '{region}' not supported. Use 'USA', 'Australia', or 'Europe'.")
    
    def get_tests(self, modifiedDate: str, profileID: Optional[str] = None, pattern = r"^([0-2][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4})$") -> pd.DataFrame:
        """
        Get test information from a specific date.
        
        Parameters
        ----------
        modifiedDate : str
            Test modified date (ISO 8601 format or 'dd/mm/yyyy')
        profileID : str, optional
            Filter by specific profile ID (use 'None' to ignore)
            
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
        
        if profileID != None:
            parameters['&ProfileId='] = profileID
        
        response = get_call(self.url, self.header, parameters=parameters)
        
        if response == 400:
            if 'tests_df' in dir(self):
                delattr(self,'tests_df')
            return 'Get request failed.'
        elif response == 204:
            return 'No Content'
        else:
            self.tests_df = pd.DataFrame(response.json()['tests'])
            while response != 204:
                parameters['&ModifiedFromUtc='] = self.tests_df['modifiedDateUtc'].tolist()[-1].replace(':','%3A')
                response = get_call(self.url,self.header,parameters=parameters)
                if response == 400:
                    if 'tests_df' in dir(self):
                        delattr(self,'tests_df')
                    print('Get request failed.')
                elif response == 204:
                    print('No Content.')
                else:
                    temp_df = pd.DataFrame(response.json()['tests'])
                    self.tests_df = pd.concat([self.tests_df,temp_df])
        
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
            '/tests': '',
            '/': test_id,
            '?TenantId=': self.tenant_id,
        }
        
        response = get_call(self.url, self.header, parameters=parameters)
        
        # if response != '' and not isinstance(response, int):
        #     self.results_df = pd.DataFrame(response.json())
        #     return self.results_df
        if response == '':
            pass
        else:
            self.test = response.json()
        # return None
    
    def get_force_trace(self, test_id):
        """
        Get force trace data for a specific test.
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
            '/forceframetrace':'',
            '?TenantId=':self.tenant_id,
        }
        response = get_call(self.url,self.header,parameters=parameters)
        if response == '':
            pass
        else:
            self.raw = response.json()
            self.raw['forces'] = pd.DataFrame(response.json()['forces'])
            self.raw['forces']['sample_number'] = np.arange(len(self.raw['forces']))
            self.raw['forces']['time_s'] = self.raw['forces']['sample_number'] * (1/samplingFreq)
            return self.raw['forces']