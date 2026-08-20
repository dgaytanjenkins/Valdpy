"""ForceDecks API client for VALD Performance"""

import re
import gzip
from io import StringIO
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

import pandas as pd

from ..utils import get_call, format_date_to_iso8601
from ..configs import Settings


class ForeDecksAPI:
    """
    Client for ForceDecks test data from VALD Performance.
    
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
            self.url = 'https://prd-use-api-extforcedecks.valdperformance.com'
        elif region == 'Australia':
            self.url = 'https://prd-aue-api-extforcedecks.valdperformance.com'
        elif region == 'Europe':
            self.url = 'https://prd-euw-api-extforcedecks.valdperformance.com'
        else:
            raise ValueError(f"Region '{region}' not supported. Use 'USA', 'Australia', or 'Europe'.")
        
        # Load result definitions on initialization
        parameters = {'/resultdefinitions': ''}
        response = get_call(self.url, self.header, parameters=parameters)
        
        if isinstance(response, int):
            print(f"Warning: Could not load result definitions. Status: {response}")
        elif response != '':
            self.result_def_df = pd.DataFrame(response.json()['resultDefinitions'])
    
    def get_single_result_definition(self, result_id: str) -> Dict[str, Any]:
        """
        Get definition for a specific result ID.
        
        Parameters
        ----------
        result_id : str
            Result definition ID
            
        Returns
        -------
        dict
            Result definition data
        """
        parameters = {'/resultdefinitions/': result_id}
        response = get_call(self.url, self.header, parameters=parameters)
        
        if response != '':
            self.result_def = response.json()
            return self.result_def
        return None
    
    def get_tests_info(
        self,
        date: datetime | str,
        profile_id: Optional[str] = None,
        timezone: str | None = Settings.DEFAULT_TIMEZONE
        
    ) -> pd.DataFrame | str:
        """
        Get test information from a specific date.
        
        Parameters
        ----------
        date : datetime or str
            Test date (format: 'dd/mm/yyyy', 'dd/mm/yyyy hh:mm', or datetime object)
        profile_id : str, optional
            Filter by specific profile ID
            
        Returns
        -------
        pd.DataFrame or str
            Tests dataframe or error message
        """
        # Parse date
        date_pattern = r"^([0-2][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4})$"
        datetime_pattern = r"^([0-2][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4}) ([0-1][0-9]|2[0-3]):([0-5][0-9])$"
        
        if isinstance(date, datetime):
            date_str = format_date_to_iso8601(date, timezone).replace(':', '%3A')
        elif isinstance(date, str) and re.match(date_pattern, date):
            date_obj = datetime.strptime(date, "%d/%m/%Y")
            date_str = format_date_to_iso8601(date_obj, timezone).replace(':', '%3A')
        elif isinstance(date, str) and re.match(datetime_pattern, date):
            date_obj = datetime.strptime(date, "%d/%m/%Y %H:%M")
            date_str = format_date_to_iso8601(date_obj, timezone).replace(':', '%3A')
        elif isinstance(date, str) and re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$', date):
            date_str = date.replace(':', '%3A')
        else:
            return 'Date does not match format - dd/mm/yyyy or dd/mm/yyyy hh:mm, ie 01/01/1900 or 01/01/1900 09:00'
        
        # Build parameters
        parameters = {
            '/tests': '',
            '?TenantId=': self.tenant_id,
            '&ModifiedFromUtc=': date_str,
        }
        if profile_id:
            parameters['&ProfileId='] = profile_id
        response = get_call(self.url, self.header, parameters=parameters)
        
        if response == '' or isinstance(response, int):
            if 'tests_df' in dir(self):
                delattr(self, 'tests_df')
            return 'Get request failed.'
        elif response.status_code == 204:
            if 'tests_df' in dir(self):
                delattr(self, 'tests_df')
            return 'No data found.'
        else:
            self.tests_df = pd.DataFrame(response.json()['tests'])
            
            # Paginate through results
            while response.status_code != 204:
                parameters['&ModifiedFromUtc='] = self.tests_df['modifiedDateUtc'].tolist()[-1].replace(':', '%3A')
                response = get_call(self.url, self.header, parameters=parameters)
                if response.status_code == 400:
                    print('Secondary request failed.')
                    break
                elif response.status_code == 204:
                    print('Request Completed.')
                else:
                    temp_df = pd.DataFrame(response.json()['tests'])
                    self.tests_df = pd.concat([self.tests_df, temp_df])
            
            return self.tests_df
    
    def get_test_results(self, test_id: str) -> Tuple[list, pd.DataFrame]:
        """
        Get trial results for a specific test.
        
        Parameters
        ----------
        test_id : str
            Test ID
            
        Returns
        -------
        tuple
            (raw response JSON, results dataframe)
        """
        parameters = {
            '/v2019q3/': '',
            'teams/': self.tenant_id,
            '/tests/': test_id,
            '/trials': '',
        }
        response = get_call(self.url, self.header, parameters=parameters)
        
        if response == '':
            return None, None
        
        # Parse first trial
        df = pd.DataFrame(response.json()[0]['results'])
        df['testId'] = test_id
        df['rep'] = 1
        
        # Add metadata columns from response
        for key, val in response.json()[0].items():
            if key not in ['results', 'limb']:
                df[key] = val
        
        if len(df['limb'].unique()) == 1:
            df['limb'] = response.json()[0]['limb']
        
        # Merge with result definitions
        def_df = pd.DataFrame(list(df['definition'].values))
        def_df.rename(columns={"id": "resultId"}, inplace=True)
        def_df = def_df.drop_duplicates(subset=["resultId"])  # prevent many-to-many explode
        df = pd.merge(df, def_df, how='left', on='resultId', validate='many_to_one')
        df = df.drop(columns=['definition'])
        
        # Parse additional trials
        if len(response.json()) > 1:
            for rep, entry in enumerate(response.json()[1:]):
                if len(pd.DataFrame(entry['results'])) == 0:
                    continue
                
                temp_df = pd.DataFrame(entry['results'])
                temp_df['testId'] = test_id
                temp_df['rep'] = rep + 2
                
                for key, val in entry.items():
                    if key not in ['results', 'limb']:
                        temp_df[key] = val
                
                if len(temp_df['limb'].unique()) == 1:
                    temp_df['limb'] = entry['limb']
                
                def_df = pd.DataFrame(list(temp_df['definition'].values))
                def_df.rename(columns={"id": "resultId"}, inplace=True)
                def_df = def_df.drop_duplicates(subset=["resultId"])  # prevent many-to-many explode
                temp_df = pd.merge(temp_df, def_df, how='left', on='resultId', validate='many_to_one')
                temp_df = temp_df.drop(columns=['definition'])
                df = pd.concat([df, temp_df], ignore_index=True)
        
        self.results_df = df.drop_duplicates(subset=["testId", "resultId", "limb", "result", "rep"], keep="first")
        return response.json(), def_df
    
    def get_force_trace(self, test_id: str) -> pd.DataFrame:
        """
        Get raw force trace data for a test.
        
        Parameters
        ----------
        test_id : str
            Test ID
            
        Returns
        -------
        pd.DataFrame
            Raw force trace data
        """
        parameters = {
            '/v2019q3/': '',
            'teams/': self.tenant_id,
            '/tests/': test_id,
            '/recording': '',
            '/file': '',
        }
        response = get_call(self.url, self.header, parameters=parameters)
        
        if response == '':
            return None
        
        # Decompress gzipped response
        compressed_data = response.content
        decompressed_data = gzip.decompress(compressed_data)
        decoded_text = decompressed_data.decode('utf-8')
        cleaned_text = '\n'.join(decoded_text.splitlines()[2:])
        
        self.raw_df = pd.read_csv(StringIO(cleaned_text))
        # self.raw_df['test_id'] = test_id
        
        return self.raw_df
    
    def get_recording_details(self, test_id: str) -> Dict[str, Any]:
        """
        Get recording metadata for a test.
        
        Parameters
        ----------
        test_id : str
            Test ID
            
        Returns
        -------
        dict
            Recording details
        """
        parameters = {
            '/v2019q3/': '',
            'teams/': self.tenant_id,
            '/tests/': test_id,
            '/recording': '',
        }
        response = get_call(self.url, self.header, parameters=parameters)
        
        if response != '':
            return response.json()
        return None
