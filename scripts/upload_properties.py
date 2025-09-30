"""
Script to upload properties from property.json to the FastAPI listing service.
Handles data transformation from the JSON format to the API schema.
"""
import json
import requests
from typing import List, Dict, Any
from datetime import datetime
import sys


class PropertyUploader:
    def __init__(self, api_base_url: str, auth_token: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        self.amenities_cache = {}
        self.safety_features_cache = {}
    
    def load_amenities(self):
        """Fetch and cache amenities from API."""
        response = requests.get(f"{self.api_base_url}/api/v1/amenities")
        response.raise_for_status()
        amenities = response.json()
        self.amenities_cache = {a['name'].lower(): a['id'] for a in amenities}
        print(f"✓ Loaded {len(self.amenities_cache)} amenities")
    
    def load_safety_features(self):
        """Fetch and cache safety features from API."""
        response = requests.get(f"{self.api_base_url}/api/v1/safety-features")
        response.raise_for_status()
        features = response.json()
        self.safety_features_cache = {f['name'].lower(): f['id'] for f in features}
        print(f"✓ Loaded {len(self.safety_features_cache)} safety features")
    
    def map_property_type(self, type_str: str) -> str:
        """Map property type from JSON format to API format."""
        type_mapping = {
            'entire-place': 'entire_place',
            'private-room': 'private_room',
            'shared-room': 'shared_room',
            'entire_place': 'entire_place',
            'private_room': 'private_room',
            'shared_room': 'shared_room'
        }
        return type_mapping.get(type_str.lower(), 'entire_place')
    
    def get_amenity_ids(self, amenity_names: List[str]) -> List[str]:
        """Convert amenity names to IDs."""
        ids = []
        for name in amenity_names:
            amenity_id = self.amenities_cache.get(name.lower())
            if amenity_id:
                ids.append(amenity_id)
            else:
                print(f"  Warning: Amenity '{name}' not found in system")
        return ids
    
    def get_safety_feature_ids(self, feature_names: List[str]) -> List[str]:
        """Convert safety feature names to IDs."""
        ids = []
        for name in feature_names:
            feature_id = self.safety_features_cache.get(name.lower())
            if feature_id:
                ids.append(feature_id)
            else:
                print(f"  Warning: Safety feature '{name}' not found in system")
        return ids
    
    def transform_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform property data from JSON format to API format."""
        
        # Build location
        location_data = property_data.get('location', {})
        coordinates = location_data.get('coordinates', {})
        
        location = {
            "address": location_data.get('address', 'N/A'),
            "city": location_data.get('city', 'Unknown'),
            "state": location_data.get('state', ''),
            "country": location_data.get('country', 'Unknown'),
            "postal_code": location_data.get('postalCode', location_data.get('postal_code', '')),
            "latitude": float(coordinates.get('lat', 0.0)),
            "longitude": float(coordinates.get('lng', 0.0))
        }
        
        # Build images (minimum 3 required)
        images = property_data.get('images', [])
        if len(images) < 3:
            print(f"  Warning: Property '{property_data.get('title')}' has only {len(images)} images, padding to 3")
            # Pad with placeholder if needed
            while len(images) < 3:
                images.append(images[0] if images else 'https://via.placeholder.com/800x600')
        
        formatted_images = []
        for idx, img_url in enumerate(images[:10]):  # Limit to 10 images
            formatted_images.append({
                "image_url": img_url,
                "display_order": idx,
                "is_cover": idx == 0,
                "alt_text": f"Property image {idx + 1}"
            })
        
        # Get amenity and safety feature IDs
        amenity_ids = self.get_amenity_ids(property_data.get('amenities', []))
        safety_ids = self.get_safety_feature_ids(property_data.get('safetyBadges', []))
        
        # Build the API payload
        api_payload = {
            "title": property_data.get('title', 'Untitled Property'),
            "description": property_data.get('description', 'No description provided'),
            "property_type": self.map_property_type(property_data.get('type', 'entire-place')),
            "bedrooms": property_data.get('bedrooms', 1),
            "beds": property_data.get('beds', 1),
            "bathrooms": float(property_data.get('bathrooms', 1)),
            "max_guests": property_data.get('maxGuests', 2),
            "max_adults": property_data.get('maxGuests', 2),
            "max_children": property_data.get('maxChildren', 0),
            "max_infants": property_data.get('maxInfants', 0),
            "pets_allowed": property_data.get('petsAllowed', False),
            "price_per_night": int(float(property_data.get('pricePerNight', 0)) * 100),  # Convert to cents
            "currency": property_data.get('currency', 'USD'),
            "cleaning_fee": int(float(property_data.get('cleaningFee', 0)) * 100),
            "service_fee": int(float(property_data.get('serviceFee', 0)) * 100),
            "weekly_discount": property_data.get('weeklyDiscount', 0),
            "monthly_discount": property_data.get('monthlyDiscount', 0),
            "instant_book": property_data.get('instantBook', False),
            "location": location,
            "amenity_ids": amenity_ids,
            "safety_feature_ids": safety_ids,
            "images": formatted_images,
            "house_rules": property_data.get('rules', []),
            "cancellation_policy": property_data.get('cancellationPolicy', 'Standard cancellation policy'),
            "check_in_policy": property_data.get('checkInPolicy', 'Check-in after 3 PM')
        }
        
        return api_payload
    
    def upload_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a single property to the API."""
        try:
            api_payload = self.transform_property(property_data)
            
            response = requests.post(
                f"{self.api_base_url}/api/v1/properties/",
                json=api_payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✓ Created: {result['title']} (ID: {result['id']})")
                return result
            else:
                print(f"✗ Failed to create '{property_data.get('title')}'")
                print(f"  Status: {response.status_code}")
                print(f"  Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ Error uploading '{property_data.get('title')}': {str(e)}")
            return None
    
    def upload_from_file(self, filename: str):
        """Load and upload properties from JSON file."""
        print(f"\n=== Property Upload Script ===\n")
        
        # Load JSON file
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"✗ File not found: {filename}")
            return
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in {filename}: {str(e)}")
            return
        
        # Handle both single object and array
        if isinstance(data, dict):
            properties = [data]
        elif isinstance(data, list):
            properties = data
        else:
            print("✗ Invalid data format. Expected object or array.")
            return
        
        print(f"Found {len(properties)} properties to upload\n")
        
        # Load amenities and safety features
        try:
            self.load_amenities()
            self.load_safety_features()
        except Exception as e:
            print(f"✗ Failed to load reference data: {str(e)}")
            return
        
        # Upload properties
        print(f"\nUploading properties...\n")
        successful = 0
        failed = 0
        
        for idx, property_data in enumerate(properties, 1):
            print(f"[{idx}/{len(properties)}] Processing '{property_data.get('title', 'Unknown')}'...")
            result = self.upload_property(property_data)
            if result:
                successful += 1
            else:
                failed += 1
        
        # Summary
        print(f"\n=== Upload Complete ===")
        print(f"✓ Successful: {successful}")
        print(f"✗ Failed: {failed}")
        print(f"Total: {len(properties)}")


def main():
    """Main function to run the uploader."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload properties from JSON file to FastAPI service')
    parser.add_argument('filename', help='Path to property.json file')
    parser.add_argument('--api-url', default='http://localhost:8001', help='API base URL')
    parser.add_argument('--token', required=True, help='JWT authentication token')
    
    args = parser.parse_args()
    
    uploader = PropertyUploader(args.api_url, args.token)
    uploader.upload_from_file(args.filename)


if __name__ == '__main__':
    main()