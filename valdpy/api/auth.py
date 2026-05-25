"""Authentication and base API client for VALD services"""

import pandas as pd
from typing import Dict, List, Optional

from ..utils import post_call, get_call, put_call


class ValdAuth:
    """
    Authentication handler for VALD APIs.
    
    Manages OAuth 2.0 authentication and provides access to tenant/profile management APIs.
    
    Parameters
    ----------
    client_id : str
        Your VALD API client ID
    client_secret : str
        Your VALD API client secret
    tenant_id : str, optional
        Default tenant ID for API calls
    region : str, optional
        API region: 'USA', 'Australia', or 'Europe' (default: 'USA')
        
    Attributes
    ----------
    token : str
        Current OAuth access token
    header : dict
        Authorization header with Bearer token and content type
    """
    
    def __init__(self, client_id: str, client_secret: str, tenant_id: Optional[str] = None, region: str = 'USA'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        
        # Set regional endpoints
        if region == 'USA':
            self.tenant_url = 'https://prd-use-api-externaltenants.valdperformance.com'
            self.profile_url = 'https://prd-use-api-externalprofile.valdperformance.com'
        elif region == 'Australia':
            self.tenant_url = 'https://prd-aue-api-externaltenants.valdperformance.com'
            self.profile_url = 'https://prd-aue-api-externalprofile.valdperformance.com'
        elif region == 'Europe':
            self.tenant_url = 'https://prd-euw-api-externaltenants.valdperformance.com'
            self.profile_url = 'https://prd-euw-api-externalprofile.valdperformance.com'
        else:
            raise ValueError(f"Region '{region}' not supported. Use 'USA', 'Australia', or 'Europe'.")
        
        self.token = None
        self.header = None
    
    def get_token(self, url: str = 'https://auth.prd.vald.com/oauth/token') -> str:
        """
        Obtain an OAuth 2.0 access token.
        
        Parameters
        ----------
        url : str
            OAuth token endpoint (default provided by VALD)
            
        Returns
        -------
        str
            Access token for API calls
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': "vald-api-external"
        }
        
        response = post_call(url, data=payload, headers=headers)
        if response == '':
            raise Exception("Failed to obtain token")
        
        self.token = response.json().get('access_token')
        self.header = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        return self.token
    
    def get_all_tenants(self) -> List[Dict]:
        """
        Retrieve all tenants accessible with current credentials.
        
        Returns
        -------
        list
            List of tenant dictionaries
        """
        parameters = {'/tenants': ''}
        response = get_call(self.tenant_url, self.header, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to retrieve tenants")
        
        self.tenants = response.json()['tenants']
        return self.tenants
    
    def get_tenant_info(self, tenant_id: Optional[str] = None) -> Dict:
        """
        Get information for a specific tenant.
        
        Parameters
        ----------
        tenant_id : str, optional
            Tenant ID (uses instance tenant_id if not provided)
            
        Returns
        -------
        dict
            Tenant information
        """
        if self.tenant_id is None and tenant_id is None:
            raise ValueError("No tenant ID found. Please provide a tenant ID.")
        
        if tenant_id:
            self.tenant_id = tenant_id
        
        parameters = {'/tenants/': self.tenant_id}
        response = get_call(self.tenant_url, self.header, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to retrieve tenant info")
        
        self.tenant_info = response.json()
        return self.tenant_info
    
    def get_tenant_categories(self) -> pd.DataFrame:
        """
        Get all categories for the tenant.
        
        Returns
        -------
        pd.DataFrame
            Categories dataframe
        """
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        
        parameters = {
            '/categories': '',
            '?TenantId=': self.tenant_id,
        }
        response = get_call(self.tenant_url, self.header, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to retrieve categories")
        
        self.categories_df = pd.DataFrame(response.json()['categories'])
        return self.categories_df
    
    def get_tenant_groups(self) -> pd.DataFrame:
        """
        Get all groups for the tenant.
        
        Returns
        -------
        pd.DataFrame
            Groups dataframe
        """
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        
        parameters = {
            '/groups': '',
            '?TenantId=': self.tenant_id,
        }
        response = get_call(self.tenant_url, self.header, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to retrieve groups")
        
        self.groups_df = pd.DataFrame(response.json()['groups'])
        return self.groups_df
    
    def get_group_profiles(self, group_name: Optional[str] = None, category_name: str = 'Team') -> pd.DataFrame:
        """
        Get profiles for a specific group.
        
        Parameters
        ----------
        group_name : str, optional
            Name of the group (retrieves all if not specified)
        category_name : str
            Category name (default: 'Team')
            
        Returns
        -------
        pd.DataFrame
            Profiles dataframe
        """
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        
        if group_name is None:
            parameters = {
                '/profiles': '',
                '?TenantId=': self.tenant_id,
            }
        else:
            cat_id = self.categories_df.loc[self.categories_df['name'] == category_name, 'id'].values[0]
            group_id = self.groups_df.loc[
                (self.groups_df['name'] == group_name) & (self.groups_df['categoryId'] == cat_id),
                'id'
            ].values[0]
            
            parameters = {
                '/profiles': '',
                '?TenantId=': self.tenant_id,
                '&GroupId=': group_id,
            }
        
        response = get_call(self.profile_url, self.header, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to retrieve profiles")
        
        self.profile_df = pd.DataFrame(response.json()['profiles'])
        return self.profile_df
    
    def assign_groups(self, profile_id: str, group_ids: List[str]) -> None:
        """
        Assign groups to a profile.
        
        Parameters
        ----------
        profile_id : str
            Profile ID
        group_ids : list
            List of group IDs to assign
        """
        if not isinstance(group_ids, list):
            group_ids = [group_ids]
        
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        
        data = {
            'tenantId': self.tenant_id,
            'profileId': profile_id,
            'groupIds': group_ids
        }
        
        parameters = {'/profiles/': 'groups'}
        put_call(self.profile_url, self.header, data, parameters=parameters)
