"""Authentication and base API client for VALD services"""

import pandas as pd
from typing import Dict, List, Optional, Literal
from datetime import datetime

from ..utils import token_post_call, post_call, get_call, put_call, delete_call


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
    headers : dict
        Authorization headers with Bearer token and content type
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
        self.headers = None
    
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
        call_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': "vald-api-external"
        }
        
        response = token_post_call(url, data=payload, headers=call_headers)
        if response == '':
            raise Exception("Failed to obtain token")
        
        self.token = response.json().get('access_token')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        return self.token
    
    def convert_date_to_iso8601(self, date_string: str) -> str:
        """
        Convert date of birth from 'dd/mm/yyyy' to ISO 8601 UTC format.
        
        Parameters
        ----------
        date_string : str
            Date in 'dd/mm/yyyy' format
            
        Returns
        -------
        str
            Date in 'YYYY-MM-DDT00:00:00.000Z' ISO 8601 UTC format
            
        Example
        -------
        >>> convert_date_to_iso8601('15/03/1990')
        '1990-03-15T00:00:00.000Z'
        """
        if 'T' in date_string and 'Z' in date_string:
            # Already in ISO 8601 format, return as-is
            return date_string
        
        try:
            # Parse dd/mm/yyyy format
            parsed_date = datetime.strptime(date_string, '%d/%m/%Y')
            # Convert to ISO 8601 UTC format
            return parsed_date.strftime('%Y-%m-%dT00:00:00.000Z')
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_string}. Expected 'dd/mm/yyyy' or ISO 8601 format. Error: {e}")

    def get_all_tenants(self) -> List[Dict]:
        """
        Retrieve all tenants accessible with current credentials.
        (Scenario 1: Retrieve list of all tenants; Tenant URL)

        Returns
        -------
        list
            List of tenant dictionaries
        """
        parameters = {'/tenants': ''}
        response = get_call(self.tenant_url, headers=self.headers, parameters=parameters)
        
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
        response = get_call(self.tenant_url, headers=self.headers, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to retrieve tenant info")
        
        self.tenant_info = response.json()
        return self.tenant_info
    
    def get_tenant_categories(self) -> pd.DataFrame:
        """
        Get all categories for the tenant.
        (Scenario 3: Retrieve list of tenant's categories; Tenant URL)
        
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
        response = get_call(self.tenant_url, headers=self.headers, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to retrieve categories")
        
        self.categories_df = pd.DataFrame(response.json()['categories'])
        return self.categories_df
    
    def create_category(self, categoryName: str, syncId: Optional[str] = f"temp-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S%f')}") -> Dict:
        """
        Create a new category for the tenant.
        (Scenario 4: Create or update a category; Tenant URL)
        
        Parameters
        ----------
        categoryName : str
            Name of the new category
            
        Returns
        -------
        dict
            Created category information
        """
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        
        
        data = {
            'syncId':syncId,
            'tenantId': self.tenant_id,
            'name': categoryName,
        }
        
        call_headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json-patch+json"
        }
        parameters = {
            '/categories': '',
            '/import': '',
        }

        response = post_call(self.tenant_url, data=data, headers=call_headers, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to create category")

    def get_tenant_groups(self) -> pd.DataFrame:
        """
        Get all groups for the tenant.
        (Scenario 3: Retrieve list of tenant's groups; Tenant URL)
        
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
        response = get_call(self.tenant_url, headers=self.headers, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to retrieve groups")
        
        self.groups_df = pd.DataFrame(response.json()['groups'])
        return self.groups_df

    def create_group(self, groupName: str, categoryName: str, syncId: Optional[str] = f"temp-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S%f')}") -> Dict:
        """
        Create a new group for the tenant.
        (Scenario 5: Create or update a group; Tenant URL)
        
        Parameters
        ----------
        groupName : str
            Name of the new group
        categoryId : str
            ID of the category the group belongs to
        syncId : str, optional
            Sync ID for the group (default: None)
            
        Returns
        -------
        dict
            Created group information
        """
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        
        self.get_tenant_categories() # Ensure categories_df up to date
        cat_id = self.categories_df.loc[self.categories_df['name'] == categoryName, 'id'].values[0]
        data = {
            'tenantId': self.tenant_id,
            'syncId':syncId,
            'categoryId': cat_id,
            'name': groupName,
        }
        
        call_headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json-patch+json"
        }
        parameters = {
            '/groups': '',
            '/import': '',
        }

        response = post_call(self.tenant_url, data=data, headers=call_headers, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to create group")
    
    def get_group_profiles(self, groupName: str = None, categoryName: str = 'Team') -> pd.DataFrame:
        """
        Get profiles for a specific group.
        (Scenario 1: Retrieve list of tenant's profiles; Profile URL)
        
        Parameters
        ----------
        groupName : str
            Name of the group (retrieves all if not specified)
        categoryName : str
            Category name (default: 'Team')
            
        Returns
        -------
        pd.DataFrame
            Profiles dataframe
        """
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        
        if groupName is None:
            parameters = {
                '/profiles': '',
                '?TenantId=': self.tenant_id,
            }
        else:
            self.get_tenant_categories() # Ensure categories_df up to date
            self.get_tenant_groups() # Ensure groups_df up to date
            cat_id = self.categories_df.loc[self.categories_df['name'] == categoryName, 'id'].values[0]
            group_id = self.groups_df.loc[
                (self.groups_df['name'] == groupName) & (self.groups_df['categoryId'] == cat_id),
                'id'
            ].values[0]
            
            parameters = {
                '/profiles': '',
                '?TenantId=': self.tenant_id,
                '&GroupId=': group_id,
            }
        
        response = get_call(self.profile_url, headers=self.headers, parameters=parameters)
        
        if response == '' or response.status_code != 200:
            raise Exception(f"Failed to retrieve profiles. Status Code: {getattr(response, 'status_code', 'unknown')}, Response: {getattr(response, 'text', '')}")
        
        # An empty body (e.g. a group with no profiles) is not valid JSON
        if not response.text.strip():
            self.profile_df = pd.DataFrame()
            return self.profile_df
        
        try:
            response_json = response.json()
        except ValueError:
            raise Exception(f"Failed to parse response JSON. Response: {response.text}")
        
        self.profile_df = pd.DataFrame(response_json.get('profiles', []))
        return self.profile_df
    
    def get_profiles(self, profileIds: Optional[List[str]] = [], groupName: Optional[str] = None, categoryName: Optional[str] = 'Team', syncId: Optional[str] = None, externalId: Optional[str] = None) -> pd.DataFrame:
        """
        Get profiles based on profile IDs.
        (Scenario 1: Retrieve list of tenant's profiles; Profile URL)
        
        Parameters
        ----------
        profileIds : list, optional
            List of profile IDs to retrieve (default: [])
        groupName : str, optional
            Name of the group (retrieves all if not specified)
        categoryName : str, optional
            Category name (default: 'Team')
        syncId : str, optional
            Sync ID to filter profiles (default: None)
        externalId : str, optional
            External ID to filter profiles (default: None)
            
        Returns
        -------
        pd.DataFrame
            Profiles dataframe
        """
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
    
        parameters = {
            '/profiles': '',
            '?TenantId=': self.tenant_id,
        }
        if len(profileIds) > 0:
            if len(profileIds) == 1:
                parameters['&ProfileIds='] = profileIds[0]
            else:
                parameters['&ProfileIds='] = '&ProfileIds='.join(profileIds)
        if groupName:
            self.get_tenant_categories() # Ensure categories_df up to date
            self.get_tenant_groups() # Ensure groups_df up to date
            cat_ids = self.categories_df.loc[self.categories_df['name'] == categoryName, 'id'].values
            if len(cat_ids) == 0:
                raise ValueError(f"Category '{categoryName}' not found. Available categories: {self.categories_df['name'].tolist()}")
            cat_id = cat_ids[0]
            
            group_ids = self.groups_df.loc[
                (self.groups_df['name'] == groupName) & (self.groups_df['categoryId'] == cat_id),
                'id'
            ].values
            if len(group_ids) == 0:
                raise ValueError(f"Group '{groupName}' not found in category '{categoryName}'. Available groups: {self.groups_df[self.groups_df['categoryId'] == cat_id]['name'].tolist()}")
            parameters['&GroupId='] = group_ids[0]
        if syncId:
            parameters['&SyncId='] = syncId
        if externalId:
            parameters['&ExternalId='] = externalId
        
        call_headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        response = get_call(self.profile_url, headers=call_headers, parameters=parameters)
        
        if response == '':
            raise Exception("Failed to retrieve profiles")
        try:
            response_json = response.json()
        except ValueError:
            raise Exception("Failed to parse response JSON")
        try:
            self.profile_df = pd.DataFrame(response_json['profiles'])
            return self.profile_df
        except KeyError:
            return response_json
    
    def create_profile(self, givenName: str, familyName: str, dateOfBirth: str, sex: Literal["Male", "Female", "Unknown", "NotApplicable"], email: Optional[str] = None, externalId: Optional[str] = None, syncId: Optional[str] = None, returnProfileId: Optional[bool] = True) -> Dict:
        """
        Create a new profile for the tenant.
        (Scenario 2: Create or update a profile; Profile URL)
        
        Parameters
        ----------
        givenName : str
            Given name of the profile
        familyName : str
            Family name of the profile
        dateOfBirth : str
            Date of birth. Accepted formats:
            - 'dd/mm/yyyy' (e.g., '15/03/1990')
            - ISO 8601 'YYYY-MM-DDT00:00:00.000Z' (e.g., '1990-03-15T00:00:00.000Z')
            
            The function automatically converts 'dd/mm/yyyy' to ISO 8601 UTC format.
        sex : {"Male", "Female", "Unknown", "NotApplicable"}
            Sex of the profile
        email : str, optional
            Email address of the profile (default: None)
        externalId : str, optional
            External ID for the profile (default: None)
        syncId : str, optional
            Sync ID for the profile (default: None)
        returnProfileId : bool, optional
            Whether to return the profile ID after creation (default: True)
            
        Returns
        -------
        dict or pd.DataFrame
            Profile information or dataframe containing the created profile
            
        Raises
        ------
        ValueError
            If dateOfBirth format is invalid or sex value is not accepted
        """
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        if syncId is None:
            syncId = f"temp-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # Convert dateOfBirth to ISO 8601 UTC format if needed
        try:
            iso_dob = self.convert_date_to_iso8601(dateOfBirth)
        except ValueError as e:
            raise ValueError(
                f"Invalid dateOfBirth format: '{dateOfBirth}'. "
                f"Accepted formats: 'dd/mm/yyyy' (e.g., '15/03/1990') or "
                f"ISO 8601 'YYYY-MM-DDT00:00:00.000Z' (e.g., '1990-03-15T00:00:00.000Z'). "
                f"Error: {e}"
            )
        
        data = {
            'tenantId': self.tenant_id,
            'givenName': givenName,
            'familyName': familyName,
            'dateOfBirth': iso_dob,
            'sex':sex,
        }
        if email:
            data['email'] = email
        if externalId:
            data['externalId'] = externalId
        data['syncId'] = syncId
        
        call_headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json-patch+json"
        }
        
        parameters = {
            '/profiles/': 'import',
        }

        response = post_call(self.profile_url, data=data, headers=call_headers, parameters=parameters)
        if response == '':
            raise Exception("Failed to create profile")
        # else:
        #     return syncId
        if returnProfileId:
            # If we created a temporary sync ID, retrieve the profile to get the assigned profile ID
            print("Profile created. Retrieving profile information to get assigned profile ID...")
            temp_sync_id = data['syncId']
            profile_df = self.get_profiles(syncId=temp_sync_id)  # Get all profiles
            if not profile_df.empty:
                return profile_df
            else:
                raise Exception("Profile created but failed to retrieve with temporary sync ID")
        else:
            return response
        
    def add_groups_to_profile(self, profileId: str, groupNames: List[str], categoryNames: List[str] = ['Team']) -> None:
        """
        Add one or more groups to a profile.
        (Scenario 5: Add profile to group/s – POST method; Profile URL)
        - The existing group assignments will be maintained.
        
        Parameters
        ----------
        profileId : str
            Profile ID
        groupNames : list
            List of group names to assign
        categoryNames : list
            List of category names
        """
        if not isinstance(groupNames, list):
            groupNames = [groupNames]
        if not isinstance(categoryNames, list):
            categoryNames = [categoryNames]
        assert len(groupNames) == len(categoryNames), "Length of groupNames and categoryNames must be the same"
     
        if 'tenant_id' not in dir(self):
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        print(f"Tenant ID: {self.tenant_id}")
        self.get_tenant_categories() # Ensure categories_df up to date
        self.get_tenant_groups() # Ensure groups_df up to date
        print(self.groups_df)
        cat_ids = [self.categories_df.loc[self.categories_df['name'] == cat_name, 'id'].values[0] for cat_name in categoryNames]
        group_ids = [
            self.groups_df.loc[
                (self.groups_df['name'] == groupName) & (self.groups_df['categoryId'] == categoryId),
                'id'
            ].values[0]
            for groupName,categoryId in zip(groupNames, cat_ids)
        ]
        print(cat_ids,group_ids)
        data = {
            'tenantId': self.tenant_id,
            'profileId': profileId,
            'groupIds': group_ids
        }
        
        parameters = {'/profiles/': 'groups'}
        post_call(self.profile_url, data=data, headers=self.headers, parameters=parameters)
        
    def overwrite_groups_to_profile(self, profileId: str, groupNames: List[str], categoryNames: List[str] = ['Team']) -> None:
        """
        Overwrite group assignments for a profile.
        (Scenario 6: Replace (add and remove) groups on a profile – PUT method; Profile URL)
        - This endpoint will completely replace any existing group assignments for the profile
        
        Parameters
        ----------
        profileId : str
            Profile ID
        groupNames : list
            List of group names to assign
        categoryNames : list
            List of category names
        """
        if not isinstance(groupNames, list):
            groupNames = [groupNames]
        if not isinstance(categoryNames, list):
            categoryNames = [categoryNames]
        assert len(groupNames) == len(categoryNames), "Length of groupNames and categoryNames must be the same"

        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")

        self.get_tenant_categories() # Ensure categories_df up to date
        self.get_tenant_groups() # Ensure groups_df up to date
        cat_ids = [self.categories_df.loc[self.categories_df['name'] == cat_name, 'id'].values[0] for cat_name in categoryNames]
        group_ids = [
            self.groups_df.loc[
                (self.groups_df['name'] == groupName) & (self.groups_df['categoryId'] == cat_ids[i]),
                'id'
            ].values[0]
            for i, groupName in enumerate(groupNames)
        ]
        
        data = {
            'tenantId': self.tenant_id,
            'profileId': profileId,
            'groupIds': group_ids
        }
        
        parameters = {'/profiles/': 'groups'}
        put_call(self.profile_url, headers=self.headers, data=data, parameters=parameters)

    def overwrite_profiles_to_group(self, groupName: str, profileIds: List[str], categoryName: Optional[str] = 'Team') -> None:
        """
        Overwrite profile assignments for a group.
        (Scenario 6: Replace (add and remove) the profiles in a group; Tenant URL)
        - Profiles that currently exist in the group but have not been included in this list will be removed from the group.
        
        Parameters
        ----------
        groupName : str
            Group name
        profileIds : list
            List of profile IDs to assign
        categoryName : str, optional
            Category name
        """
        if not isinstance(profileIds, list):
            profileIds = [profileIds]
        
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        
        self.get_tenant_categories() # Ensure categories_df up to date
        self.get_tenant_groups() # Ensure groups_df up to date
        cat_ids = self.categories_df.loc[self.categories_df['name'] == categoryName, 'id'].values
        if len(cat_ids) == 0:
            raise ValueError(f"Category '{categoryName}' not found. Available categories: {self.categories_df['name'].tolist()}")
        cat_id = cat_ids[0]
        group_id = self.groups_df.loc[
            (self.groups_df['name'] == groupName) & (self.groups_df['categoryId'] == cat_id),
            'id'
        ].values[0]
        
        data = {
            'tenantId': self.tenant_id,
            'groupId': group_id,
            'profileIds': profileIds
        }
        call_headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json-patch+json"
        }
        
        parameters = {'/groups/': 'profiles'}
        put_call(self.tenant_url, headers=call_headers, data=data, parameters=parameters)
    
    def remove_profiles_from_group(self, groupName: str, profileIds: List[str], categoryName: Optional[str] = 'Team') -> None:
        """
        Remove profiles from a group.
        (Scenario 7: Remove profiles from a group in a tenant)
        If not supplied, all profiles will be removed from the group.

        Parameters
        ----------
        groupName : str
            Group name
        profileIds : list
            List of profile IDs to remove; 
            If empty list provided [], all profiles will be removed from the group
        categoryName : str, optional
            Category name
        """
        if not isinstance(profileIds, list):
            profileIds = [profileIds]
        
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        
        self.get_tenant_categories() # Ensure categories_df up to date
        self.get_tenant_groups() # Ensure groups_df up to date
        cat_ids = self.categories_df.loc[self.categories_df['name'] == categoryName, 'id'].values
        if len(cat_ids) == 0:
            raise ValueError(f"Category '{categoryName}' not found. Available categories: {self.categories_df['name'].tolist()}")
        cat_id = cat_ids[0]
        group_id = self.groups_df.loc[
            (self.groups_df['name'] == groupName) & (self.groups_df['categoryId'] == cat_id),
            'id'
        ].values[0]
        
        data = {
            'tenantId': self.tenant_id,
            'groupId': group_id,
            'profileIds': profileIds
        }
        call_headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json-patch+json"
        }
        
        parameters = {'/groups/': 'profiles'}
        delete_call(self.tenant_url, headers=call_headers, data=data, parameters=parameters)
    
    def remove_groups_from_profile(self, profileId: str, groupNames: List[str], categoryNames: List[str] = ['Team']) -> None:
        """
        Remove groups from a profile.
        (Scenario 7: Remove groups from a profile; Profile URL)

        Parameters
        ----------
        profileId : str
            Profile ID
        groupNames : list
            List of group names to remove
            If empty list provided [], all groups will be removed from the profile
        categoryNames : list, optional
            List of category names
        """
        if not isinstance(groupNames, list):
            groupNames = [groupNames]
        if not isinstance(categoryNames, list):
            categoryNames = [categoryNames]
        assert len(groupNames) == len(categoryNames), "Length of groupNames and categoryNames must be the same"
        
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        if len(groupNames) == 0:
            # If empty list provided, remove all groups by passing an empty list of group IDs
            group_ids = []
        else:
            self.get_tenant_categories() # Ensure categories_df up to date
        self.get_tenant_groups() # Ensure groups_df up to date
        cat_ids = [self.categories_df.loc[self.categories_df['name'] == cat_name, 'id'].values[0] for cat_name in categoryNames]
        group_ids = [
            self.groups_df.loc[
                (self.groups_df['name'] == groupName) & (self.groups_df['categoryId'] == cat_ids[i]),
                'id'
            ].values[0]
            for i, groupName in enumerate(groupNames)
        ]
        
        data = {
            'tenantId': self.tenant_id,
            'profileId': profileId,
            'groupIds': group_ids
        }
        call_headers = {
            "accept": "*/*",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json-patch+json"
        }
        
        parameters = {'/profiles/': 'groups'}
        delete_call(self.profile_url, headers=call_headers, data=data, parameters=parameters)

    def delete_group(self, groupName: str, categoryName: str = 'Team') -> None:
        """
        Delete a group from the tenant.
        (Scenario 8: Delete a group in a tenant)
        - Profile group membership will be updated, but the profiles will not be deleted from the tenant.
        
        Parameters
        ----------
        groupName : str
            Name of the group to delete
        categoryName : str, optional
            Category name
        """
        if self.tenant_id is None:
            raise ValueError("No tenant ID found. Please call get_tenant_info() first.")
        
        self.get_tenant_categories() # Ensure categories_df up to date
        self.get_tenant_groups() # Ensure groups_df up to date
        cat_ids = self.categories_df.loc[self.categories_df['name'] == categoryName, 'id'].values
        if len(cat_ids) == 0:
            raise ValueError(f"Category '{categoryName}' not found. Available categories: {self.categories_df['name'].tolist()}")
        cat_id = cat_ids[0]
        group_id = self.groups_df.loc[
            (self.groups_df['name'] == groupName) & (self.groups_df['categoryId'] == cat_id),
            'id'
        ].values[0]
        
        parameters = {
            '/groups/': group_id,
            '?tenantId=': self.tenant_id,
        }
        delete_call(self.tenant_url, headers=self.headers, parameters=parameters)
    
