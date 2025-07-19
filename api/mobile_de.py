"""
Mobile.de API Client
-------------------
Handles API integration with mobile.de's commercial API for car listings.
"""
import requests
import base64
import json
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, parse_qs, unquote
import logging

logger = logging.getLogger(__name__)


class MobileDeAPIClient:
    """
    Client for mobile.de API integration.
    
    This client handles authentication, request formatting, rate limiting,
    and data normalization for mobile.de API responses.
    """
    
    def __init__(self, username: str, password: str, base_url: str = "https://api.mobile.de"):
        """
        Initialize the mobile.de API client.
        
        Args:
            username: API username from mobile.de
            password: API password from mobile.de
            base_url: Base URL for mobile.de API (default: https://api.mobile.de)
        """
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self._setup_authentication()
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        
    def _setup_authentication(self):
        """Setup HTTP Basic Authentication for the session."""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.session.headers.update({
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'VroomSniffer/1.0 (API Client)'
        })
        
    def _rate_limit(self):
        """Enforce rate limiting between API requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
        
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make an authenticated API request to mobile.de.
        
        Args:
            endpoint: API endpoint (e.g., '/vehicles/search')
            params: Query parameters for the request
            
        Returns:
            Dict containing the API response
            
        Raises:
            requests.RequestException: If the API request fails
        """
        self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Log successful request
            logger.info(f"API request successful: {endpoint}")
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {str(e)}")
            raise
            
    def convert_search_url_to_params(self, search_url: str) -> Dict[str, Any]:
        """
        Convert a mobile.de search URL to API parameters.
        
        Args:
            search_url: Full mobile.de search URL
            
        Returns:
            Dict containing API parameters
        """
        parsed_url = urlparse(search_url)
        query_params = parse_qs(parsed_url.query)
        
        # Convert common URL parameters to API parameters
        api_params = {}
        
        # Brand/Make
        if 'makeModelVariant1.makeId' in query_params:
            api_params['makeId'] = query_params['makeModelVariant1.makeId'][0]
        elif 'makeId' in query_params:
            api_params['makeId'] = query_params['makeId'][0]
            
        # Model
        if 'makeModelVariant1.modelId' in query_params:
            api_params['modelId'] = query_params['makeModelVariant1.modelId'][0]
        elif 'modelId' in query_params:
            api_params['modelId'] = query_params['modelId'][0]
            
        # Price range
        if 'minPrice' in query_params:
            api_params['minPrice'] = int(query_params['minPrice'][0])
        if 'maxPrice' in query_params:
            api_params['maxPrice'] = int(query_params['maxPrice'][0])
            
        # Mileage range
        if 'minMileage' in query_params:
            api_params['minMileage'] = int(query_params['minMileage'][0])
        if 'maxMileage' in query_params:
            api_params['maxMileage'] = int(query_params['maxMileage'][0])
            
        # Year range
        if 'minFirstRegistration' in query_params:
            api_params['minFirstRegistration'] = int(query_params['minFirstRegistration'][0])
        if 'maxFirstRegistration' in query_params:
            api_params['maxFirstRegistration'] = int(query_params['maxFirstRegistration'][0])
            
        # Location/Radius
        if 'zipcode' in query_params:
            api_params['zipcode'] = query_params['zipcode'][0]
        if 'radius' in query_params:
            api_params['radius'] = int(query_params['radius'][0])
            
        # Fuel type
        if 'fuelTypeId' in query_params:
            api_params['fuelTypeId'] = query_params['fuelTypeId'][0]
            
        # Transmission
        if 'transmissionId' in query_params:
            api_params['transmissionId'] = query_params['transmissionId'][0]
            
        # Sorting
        if 'sortOption.sortBy' in query_params:
            api_params['sortBy'] = query_params['sortOption.sortBy'][0]
        if 'sortOption.sortOrder' in query_params:
            api_params['sortOrder'] = query_params['sortOption.sortOrder'][0]
            
        # Page size
        if 'pageSize' in query_params:
            api_params['pageSize'] = int(query_params['pageSize'][0])
        else:
            api_params['pageSize'] = 50  # Default page size
            
        logger.info(f"Converted URL to API params: {len(api_params)} parameters")
        return api_params
        
    def search_vehicles(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for vehicles using the mobile.de API.
        
        Args:
            search_params: Dictionary of search parameters
            
        Returns:
            Dict containing search results
        """
        endpoint = "/vehicles/search"
        return self._make_request(endpoint, search_params)
        
    def normalize_api_response(self, api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Normalize mobile.de API response to VroomSniffer format.
        
        Args:
            api_response: Raw API response from mobile.de
            
        Returns:
            List of normalized car listings
        """
        listings = []
        
        # Extract vehicles from API response
        vehicles = api_response.get('vehicles', [])
        if not vehicles:
            # Try alternative response structure
            vehicles = api_response.get('results', [])
            
        for vehicle in vehicles:
            try:
                normalized_listing = {
                    'title': self._extract_title(vehicle),
                    'price': self._extract_price(vehicle),
                    'location': self._extract_location(vehicle),
                    'mileage': self._extract_mileage(vehicle),
                    'year': self._extract_year(vehicle),
                    'fuel_type': self._extract_fuel_type(vehicle),
                    'transmission': self._extract_transmission(vehicle),
                    'url': self._extract_url(vehicle),
                    'image_url': self._extract_image_url(vehicle),
                    'description': self._extract_description(vehicle),
                    'seller_type': self._extract_seller_type(vehicle),
                    'id': self._extract_id(vehicle),
                    'source': 'mobile.de_api',
                    'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                listings.append(normalized_listing)
                
            except Exception as e:
                logger.warning(f"Failed to normalize vehicle listing: {str(e)}")
                continue
                
        logger.info(f"Normalized {len(listings)} listings from API response")
        return listings
        
    def _extract_title(self, vehicle: Dict[str, Any]) -> str:
        """Extract and format the vehicle title."""
        make = vehicle.get('make', {}).get('name', '')
        model = vehicle.get('model', {}).get('name', '')
        variant = vehicle.get('variant', {}).get('name', '')
        
        title_parts = [make, model, variant]
        title = ' '.join(filter(None, title_parts))
        
        return title or vehicle.get('title', 'Unknown Vehicle')
        
    def _extract_price(self, vehicle: Dict[str, Any]) -> str:
        """Extract and format the price."""
        price_info = vehicle.get('price', {})
        
        if isinstance(price_info, dict):
            amount = price_info.get('amount')
            currency = price_info.get('currency', '€')
            
            if amount:
                return f"{amount:,} {currency}"
                
        # Fallback to direct price field
        price = vehicle.get('priceAmount') or vehicle.get('price')
        if price:
            return f"{price:,} €"
            
        return "Price on request"
        
    def _extract_location(self, vehicle: Dict[str, Any]) -> str:
        """Extract location information."""
        location = vehicle.get('location', {})
        
        if isinstance(location, dict):
            city = location.get('city', '')
            postal_code = location.get('postalCode', '')
            
            if city and postal_code:
                return f"{postal_code} {city}"
            elif city:
                return city
            elif postal_code:
                return postal_code
                
        return vehicle.get('location', 'Unknown Location')
        
    def _extract_mileage(self, vehicle: Dict[str, Any]) -> str:
        """Extract mileage information."""
        mileage = vehicle.get('mileage', {})
        
        if isinstance(mileage, dict):
            value = mileage.get('value')
            unit = mileage.get('unit', 'km')
            
            if value:
                return f"{value:,} {unit}"
                
        # Fallback
        mileage_value = vehicle.get('mileageValue') or vehicle.get('mileage')
        if mileage_value:
            return f"{mileage_value:,} km"
            
        return "Unknown mileage"
        
    def _extract_year(self, vehicle: Dict[str, Any]) -> str:
        """Extract year information."""
        year = vehicle.get('firstRegistration', {}).get('year')
        if year:
            return str(year)
            
        # Fallback
        year = vehicle.get('year') or vehicle.get('firstRegistrationYear')
        return str(year) if year else "Unknown year"
        
    def _extract_fuel_type(self, vehicle: Dict[str, Any]) -> str:
        """Extract fuel type."""
        fuel_type = vehicle.get('fuelType', {})
        
        if isinstance(fuel_type, dict):
            return fuel_type.get('name', 'Unknown fuel type')
            
        return vehicle.get('fuelType', 'Unknown fuel type')
        
    def _extract_transmission(self, vehicle: Dict[str, Any]) -> str:
        """Extract transmission type."""
        transmission = vehicle.get('transmission', {})
        
        if isinstance(transmission, dict):
            return transmission.get('name', 'Unknown transmission')
            
        return vehicle.get('transmission', 'Unknown transmission')
        
    def _extract_url(self, vehicle: Dict[str, Any]) -> str:
        """Extract the vehicle detail URL."""
        url = vehicle.get('detailUrl') or vehicle.get('url')
        
        if url and not url.startswith('http'):
            # If it's a relative URL, make it absolute
            url = f"https://www.mobile.de{url}"
            
        return url or "https://www.mobile.de"
        
    def _extract_image_url(self, vehicle: Dict[str, Any]) -> str:
        """Extract the main image URL."""
        images = vehicle.get('images', [])
        
        if images and len(images) > 0:
            first_image = images[0]
            if isinstance(first_image, dict):
                return first_image.get('url', '')
            elif isinstance(first_image, str):
                return first_image
                
        return vehicle.get('imageUrl', '')
        
    def _extract_description(self, vehicle: Dict[str, Any]) -> str:
        """Extract vehicle description."""
        description = vehicle.get('description', '')
        
        # Combine with key features if available
        features = vehicle.get('features', [])
        if features:
            features_text = ', '.join(features[:5])  # Limit to 5 features
            if description:
                description += f" | Features: {features_text}"
            else:
                description = f"Features: {features_text}"
                
        return description
        
    def _extract_seller_type(self, vehicle: Dict[str, Any]) -> str:
        """Extract seller type (dealer, private, etc.)."""
        seller = vehicle.get('seller', {})
        
        if isinstance(seller, dict):
            seller_type = seller.get('type', '')
            if seller_type:
                return seller_type
                
        return vehicle.get('sellerType', 'Unknown seller')
        
    def _extract_id(self, vehicle: Dict[str, Any]) -> str:
        """Extract unique vehicle ID."""
        return str(vehicle.get('id', vehicle.get('vehicleId', '')))
        
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test the API connection and credentials.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Make a simple test request
            response = self._make_request('/vehicles/search', {'pageSize': 1})
            
            if response:
                return True, "API connection successful"
            else:
                return False, "API returned empty response"
                
        except Exception as e:
            return False, f"API connection failed: {str(e)}"


class MobileDeAPIError(Exception):
    """Custom exception for mobile.de API errors."""
    pass
