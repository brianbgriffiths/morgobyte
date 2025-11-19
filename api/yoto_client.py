"""
Yoto API Client for authenticating and making requests to the Yoto API.
"""
import requests
from typing import Optional, Dict, Any
import os
from datetime import datetime, timedelta


class YotoAPIClient:
    """Client for interacting with the Yoto API."""
    
    def __init__(self):
        self.base_url = os.getenv('YOTO_API_BASE_URL', 'https://api.yotoplay.com')
        self.client_id = os.getenv('YOTO_CLIENT_ID')
        self.client_secret = os.getenv('YOTO_CLIENT_SECRET')
        self.refresh_token = os.getenv('YOTO_REFRESH_TOKEN')
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
    
    def _is_token_expired(self) -> bool:
        """Check if the current access token is expired."""
        # If we don't have expiry info and have a token, assume it's valid
        # (happens when token is set directly from headers)
        if self.access_token and not self.token_expiry:
            return False
        if not self.access_token or not self.token_expiry:
            return True
        return datetime.now() >= self.token_expiry
    
    def authenticate(self) -> bool:
        """
        Authenticate with the Yoto API using refresh token.
        Returns True if authentication is successful.
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("YOTO_CLIENT_ID and YOTO_CLIENT_SECRET must be set in environment variables")
        
        url = 'https://login.yotoplay.com/oauth/token'
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'audience': 'https://api.yotoplay.com'
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            expires_in = token_data.get('expires_in', 3600)  # Default to 1 hour
            self.token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 min early
            
            return True
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            return False
    
    def _ensure_authenticated(self):
        """Ensure we have a valid access token."""
        print(f"=== _ensure_authenticated called ===")
        print(f"  access_token: {'present' if self.access_token else 'missing'}")
        print(f"  refresh_token: {'present' if self.refresh_token else 'missing'}")
        print(f"  token_expiry: {self.token_expiry}")
        print(f"  is_expired: {self._is_token_expired()}")
        
        # If access token is already set (e.g., from headers), don't try to refresh
        if not self.access_token:
            print("ERROR: No access token available")
            raise Exception("No access token available")
        
        print("Access token is available, proceeding...")
        
        # Only try to refresh if we have all the credentials and token is expired
        if self._is_token_expired() and self.refresh_token and self.client_id and self.client_secret:
            print("Token expired, attempting refresh...")
            if not self.authenticate():
                raise Exception("Failed to authenticate with Yoto API")
        else:
            print("Token not expired or no refresh credentials, skipping refresh")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """
        Make an authenticated request to the Yoto API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments to pass to requests
        
        Returns:
            JSON response as dictionary
        """
        print(f"=== _make_request called ===")
        print(f"  method: {method}")
        print(f"  endpoint: {endpoint}")
        print(f"  kwargs: {kwargs}")
        
        self._ensure_authenticated()
        
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'
        
        print(f"Making {method} request to: {url}")
        print(f"Authorization header: Bearer {self.access_token[:30]}...")
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            print(f"Response status: {response.status_code}")
            
            # If we get a 403 and we have refresh credentials, try to refresh the token and retry
            if response.status_code == 403 and self.refresh_token and self.client_id and self.client_secret:
                print("Got 403, attempting to refresh token and retry...")
                if self.authenticate():
                    print("Token refreshed successfully, retrying request...")
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.request(method, url, headers=headers, **kwargs)
                    print(f"Retry response status: {response.status_code}")
                else:
                    print("Token refresh failed")
            
            response.raise_for_status()
            result = response.json()
            print(f"Response JSON keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
            return result
        except requests.exceptions.RequestException as e:
            print(f"!!! API request failed: {type(e).__name__}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response body: {e.response.text[:500]}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make a GET request to the Yoto API."""
        return self._make_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make a POST request to the Yoto API."""
        return self._make_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make a PUT request to the Yoto API."""
        return self._make_request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make a DELETE request to the Yoto API."""
        return self._make_request('DELETE', endpoint, **kwargs)
    
    # Specific API methods based on Yoto API docs
    def get_family(self) -> Dict[Any, Any]:
        """Get family information."""
        return self.get('/family')
    
    def get_players(self) -> list:
        """Get all devices (players) in the family."""
        try:
            print(f"Fetching devices from /device-v2/devices/mine")
            response = self.get('/device-v2/devices/mine')
            # Response structure: { "devices": [...] }
            devices = response.get('devices', [])
            if not isinstance(devices, list):
                devices = []
            print(f"Successfully fetched {len(devices)} devices")
            return devices
        except Exception as e:
            print(f"Error fetching devices: {e}")
            raise
    
    def get_player(self, player_id: str) -> Dict[Any, Any]:
        """Get specific device (player) information."""
        return self.get(f'/devices/{player_id}')
    
    def get_library(self) -> list:
        """Get user's MYO content library."""
        try:
            print(f"Fetching library from /content/mine")
            response = self.get('/content/mine')
            # Response structure: { "cards": [...] }
            cards = response.get('cards', [])
            if not isinstance(cards, list):
                cards = []
            print(f"Successfully fetched {len(cards)} cards from library")
            return cards
        except Exception as e:
            print(f"Error fetching library: {e}")
            raise
    
    def get_card(self, card_id: str, playable: bool = True) -> dict:
        """Get detailed card information including chapters."""
        try:
            endpoint = f'/content/{card_id}'
            print(f"=== get_card called ===")
            print(f"  card_id: {card_id}")
            print(f"  playable: {playable}")
            print(f"  endpoint: {endpoint}")
            
            params = {}
            if playable:
                params['playable'] = 'true'
                params['signingType'] = 's3'
            
            print(f"  params: {params}")
            print(f"Calling self.get('{endpoint}', params={params})")
            
            response = self.get(endpoint, params=params)
            print(f"Successfully fetched card details for {card_id}")
            return response
        except Exception as e:
            print(f"!!! ERROR in get_card: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
