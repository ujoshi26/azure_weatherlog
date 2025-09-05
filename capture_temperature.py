#!/usr/bin/env python3
"""
Temperature Capture Script
Fetches current temperature for Atlanta and uploads to Azure Blob Storage
"""

import os
import json
import requests
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_atlanta_temperature():
    """Fetch current temperature for Atlanta using OpenWeatherMap API"""
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY environment variable not set")
    
    # Atlanta coordinates
    lat, lon = 33.7490, -84.3880
    
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': api_key,
        'units': 'imperial'  # Fahrenheit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        temperature_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'city': 'Atlanta',
            'state': 'GA',
            'temperature_f': data['main']['temp'],
            'feels_like_f': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'pressure': data['main']['pressure'],
            'visibility': data.get('visibility', 'N/A'),
            'wind_speed': data.get('wind', {}).get('speed', 'N/A'),
            'wind_direction': data.get('wind', {}).get('deg', 'N/A')
        }
        
        logger.info(f"Temperature captured: {temperature_data['temperature_f']}°F")
        return temperature_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather data: {e}")
        raise
    except KeyError as e:
        logger.error(f"Unexpected API response format: {e}")
        raise

def upload_to_azure_blob(temperature_data):
    """Upload temperature data to Azure Blob Storage"""
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    container_name = os.getenv('AZURE_CONTAINER_NAME')
    
    if not connection_string:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable not set")
    if not container_name:
        raise ValueError("AZURE_CONTAINER_NAME environment variable not set")
    
    try:
        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Generate blob name with timestamp
        timestamp = temperature_data['timestamp'].replace(':', '-').replace('.', '-')
        blob_name = f"atlanta-temperature/{timestamp}.json"
        
        # Convert data to JSON
        json_data = json.dumps(temperature_data, indent=2)
        
        # Upload to blob storage
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )
        
        blob_client.upload_blob(
            json_data, 
            overwrite=True,
            content_type='application/json'
        )
        
        logger.info(f"Data uploaded to blob: {blob_name}")
        return blob_name
        
    except Exception as e:
        logger.error(f"Error uploading to Azure Blob Storage: {e}")
        raise

def main():
    """Main function to capture temperature and upload to Azure"""
    try:
        logger.info("Starting Atlanta temperature capture...")
        
        # Get temperature data
        temperature_data = get_atlanta_temperature()
        
        # Upload to Azure Blob Storage
        blob_name = upload_to_azure_blob(temperature_data)
        
        logger.info(f"Successfully completed temperature capture and upload")
        logger.info(f"Temperature: {temperature_data['temperature_f']}°F")
        logger.info(f"Blob: {blob_name}")
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
