"""
Simplified US Census Bureau API Integration
Basic demographic and geographic data without geopandas dependency
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplifiedUSCensusAPI:
    """Simplified interface for US Census Bureau APIs without geopandas"""
    
    def __init__(self, output_dir: str = "raw_data/us_census"):
        self.base_url = "https://api.census.gov/data"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Rate limiting - Census API allows reasonable requests
        self.request_delay = 0.1  # 100ms between requests
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, params: Dict) -> Optional[Dict]:
        """Make rate-limited request with error handling"""
        self._rate_limit()
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {url} - {e}")
            return None
    
    def get_states_basic(self, year: int = 2022) -> List[Dict]:
        """Get all US states with basic demographic data"""
        logger.info(f"Fetching US states data for {year}")
        
        url = f"{self.base_url}/{year}/acs/acs5"
        params = {
            'get': 'NAME,B01001_001E',  # Name and Total Population
            'for': 'state:*'
        }
        
        data = self._make_request(url, params)
        if not data:
            logger.warning("No states data received, trying backup approach")
            return self._get_states_backup()
        
        # Process response (first row is headers)
        if len(data) < 2:
            return self._get_states_backup()
        
        headers = data[0]
        states = []
        
        for row in data[1:]:
            if len(row) >= len(headers):
                state_data = dict(zip(headers, row))
                
                # Get state metadata
                fips_code = state_data.get('state', '')
                state_meta = self._get_state_metadata(fips_code)
                
                standardized = {
                    'fips_code': fips_code,
                    'name': state_data.get('NAME', ''),
                    'population': self._safe_int(state_data.get('B01001_001E')),
                    'state_code': state_meta.get('code', ''),
                    'capital': state_meta.get('capital', ''),
                    'data_year': year,
                    'last_updated': datetime.now().isoformat()
                }
                
                states.append(standardized)
        
        # Save to file
        output_file = self.output_dir / f"us_states_{year}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(states, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(states)} states to {output_file}")
        return states
    
    def _get_states_backup(self) -> List[Dict]:
        """Backup state data if API fails"""
        logger.info("Using backup state data")
        
        backup_states = [
            {'fips_code': '01', 'name': 'Alabama', 'state_code': 'AL', 'capital': 'Montgomery'},
            {'fips_code': '02', 'name': 'Alaska', 'state_code': 'AK', 'capital': 'Juneau'},
            {'fips_code': '04', 'name': 'Arizona', 'state_code': 'AZ', 'capital': 'Phoenix'},
            {'fips_code': '05', 'name': 'Arkansas', 'state_code': 'AR', 'capital': 'Little Rock'},
            {'fips_code': '06', 'name': 'California', 'state_code': 'CA', 'capital': 'Sacramento'},
            {'fips_code': '08', 'name': 'Colorado', 'state_code': 'CO', 'capital': 'Denver'},
            {'fips_code': '09', 'name': 'Connecticut', 'state_code': 'CT', 'capital': 'Hartford'},
            {'fips_code': '10', 'name': 'Delaware', 'state_code': 'DE', 'capital': 'Dover'},
            {'fips_code': '11', 'name': 'District of Columbia', 'state_code': 'DC', 'capital': 'Washington'},
            {'fips_code': '12', 'name': 'Florida', 'state_code': 'FL', 'capital': 'Tallahassee'},
            {'fips_code': '13', 'name': 'Georgia', 'state_code': 'GA', 'capital': 'Atlanta'},
            {'fips_code': '15', 'name': 'Hawaii', 'state_code': 'HI', 'capital': 'Honolulu'},
            {'fips_code': '16', 'name': 'Idaho', 'state_code': 'ID', 'capital': 'Boise'},
            {'fips_code': '17', 'name': 'Illinois', 'state_code': 'IL', 'capital': 'Springfield'},
            {'fips_code': '18', 'name': 'Indiana', 'state_code': 'IN', 'capital': 'Indianapolis'},
            {'fips_code': '19', 'name': 'Iowa', 'state_code': 'IA', 'capital': 'Des Moines'},
            {'fips_code': '20', 'name': 'Kansas', 'state_code': 'KS', 'capital': 'Topeka'},
            {'fips_code': '21', 'name': 'Kentucky', 'state_code': 'KY', 'capital': 'Frankfort'},
            {'fips_code': '22', 'name': 'Louisiana', 'state_code': 'LA', 'capital': 'Baton Rouge'},
            {'fips_code': '23', 'name': 'Maine', 'state_code': 'ME', 'capital': 'Augusta'},
            {'fips_code': '24', 'name': 'Maryland', 'state_code': 'MD', 'capital': 'Annapolis'},
            {'fips_code': '25', 'name': 'Massachusetts', 'state_code': 'MA', 'capital': 'Boston'},
            {'fips_code': '26', 'name': 'Michigan', 'state_code': 'MI', 'capital': 'Lansing'},
            {'fips_code': '27', 'name': 'Minnesota', 'state_code': 'MN', 'capital': 'Saint Paul'},
            {'fips_code': '28', 'name': 'Mississippi', 'state_code': 'MS', 'capital': 'Jackson'},
            {'fips_code': '29', 'name': 'Missouri', 'state_code': 'MO', 'capital': 'Jefferson City'},
            {'fips_code': '30', 'name': 'Montana', 'state_code': 'MT', 'capital': 'Helena'},
            {'fips_code': '31', 'name': 'Nebraska', 'state_code': 'NE', 'capital': 'Lincoln'},
            {'fips_code': '32', 'name': 'Nevada', 'state_code': 'NV', 'capital': 'Carson City'},
            {'fips_code': '33', 'name': 'New Hampshire', 'state_code': 'NH', 'capital': 'Concord'},
            {'fips_code': '34', 'name': 'New Jersey', 'state_code': 'NJ', 'capital': 'Trenton'},
            {'fips_code': '35', 'name': 'New Mexico', 'state_code': 'NM', 'capital': 'Santa Fe'},
            {'fips_code': '36', 'name': 'New York', 'state_code': 'NY', 'capital': 'Albany'},
            {'fips_code': '37', 'name': 'North Carolina', 'state_code': 'NC', 'capital': 'Raleigh'},
            {'fips_code': '38', 'name': 'North Dakota', 'state_code': 'ND', 'capital': 'Bismarck'},
            {'fips_code': '39', 'name': 'Ohio', 'state_code': 'OH', 'capital': 'Columbus'},
            {'fips_code': '40', 'name': 'Oklahoma', 'state_code': 'OK', 'capital': 'Oklahoma City'},
            {'fips_code': '41', 'name': 'Oregon', 'state_code': 'OR', 'capital': 'Salem'},
            {'fips_code': '42', 'name': 'Pennsylvania', 'state_code': 'PA', 'capital': 'Harrisburg'},
            {'fips_code': '44', 'name': 'Rhode Island', 'state_code': 'RI', 'capital': 'Providence'},
            {'fips_code': '45', 'name': 'South Carolina', 'state_code': 'SC', 'capital': 'Columbia'},
            {'fips_code': '46', 'name': 'South Dakota', 'state_code': 'SD', 'capital': 'Pierre'},
            {'fips_code': '47', 'name': 'Tennessee', 'state_code': 'TN', 'capital': 'Nashville'},
            {'fips_code': '48', 'name': 'Texas', 'state_code': 'TX', 'capital': 'Austin'},
            {'fips_code': '49', 'name': 'Utah', 'state_code': 'UT', 'capital': 'Salt Lake City'},
            {'fips_code': '50', 'name': 'Vermont', 'state_code': 'VT', 'capital': 'Montpelier'},
            {'fips_code': '51', 'name': 'Virginia', 'state_code': 'VA', 'capital': 'Richmond'},
            {'fips_code': '53', 'name': 'Washington', 'state_code': 'WA', 'capital': 'Olympia'},
            {'fips_code': '54', 'name': 'West Virginia', 'state_code': 'WV', 'capital': 'Charleston'},
            {'fips_code': '55', 'name': 'Wisconsin', 'state_code': 'WI', 'capital': 'Madison'},
            {'fips_code': '56', 'name': 'Wyoming', 'state_code': 'WY', 'capital': 'Cheyenne'}
        ]
        
        for state in backup_states:
            state['population'] = None
            state['data_year'] = 2024
            state['last_updated'] = datetime.now().isoformat()
            state['data_source'] = 'backup_data'
        
        # Save backup data
        output_file = self.output_dir / "us_states_backup.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(backup_states, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(backup_states)} backup states to {output_file}")
        return backup_states
    
    def _get_state_metadata(self, state_fips: str) -> Dict:
        """Get additional state metadata"""
        STATE_METADATA = {
            '01': {'code': 'AL', 'name': 'Alabama', 'capital': 'Montgomery'},
            '02': {'code': 'AK', 'name': 'Alaska', 'capital': 'Juneau'},
            '04': {'code': 'AZ', 'name': 'Arizona', 'capital': 'Phoenix'},
            '05': {'code': 'AR', 'name': 'Arkansas', 'capital': 'Little Rock'},
            '06': {'code': 'CA', 'name': 'California', 'capital': 'Sacramento'},
            '08': {'code': 'CO', 'name': 'Colorado', 'capital': 'Denver'},
            '09': {'code': 'CT', 'name': 'Connecticut', 'capital': 'Hartford'},
            '10': {'code': 'DE', 'name': 'Delaware', 'capital': 'Dover'},
            '11': {'code': 'DC', 'name': 'District of Columbia', 'capital': 'Washington'},
            '12': {'code': 'FL', 'name': 'Florida', 'capital': 'Tallahassee'},
            '13': {'code': 'GA', 'name': 'Georgia', 'capital': 'Atlanta'},
            '15': {'code': 'HI', 'name': 'Hawaii', 'capital': 'Honolulu'},
            '16': {'code': 'ID', 'name': 'Idaho', 'capital': 'Boise'},
            '17': {'code': 'IL', 'name': 'Illinois', 'capital': 'Springfield'},
            '18': {'code': 'IN', 'name': 'Indiana', 'capital': 'Indianapolis'},
            '19': {'code': 'IA', 'name': 'Iowa', 'capital': 'Des Moines'},
            '20': {'code': 'KS', 'name': 'Kansas', 'capital': 'Topeka'},
            '21': {'code': 'KY', 'name': 'Kentucky', 'capital': 'Frankfort'},
            '22': {'code': 'LA', 'name': 'Louisiana', 'capital': 'Baton Rouge'},
            '23': {'code': 'ME', 'name': 'Maine', 'capital': 'Augusta'},
            '24': {'code': 'MD', 'name': 'Maryland', 'capital': 'Annapolis'},
            '25': {'code': 'MA', 'name': 'Massachusetts', 'capital': 'Boston'},
            '26': {'code': 'MI', 'name': 'Michigan', 'capital': 'Lansing'},
            '27': {'code': 'MN', 'name': 'Minnesota', 'capital': 'Saint Paul'},
            '28': {'code': 'MS', 'name': 'Mississippi', 'capital': 'Jackson'},
            '29': {'code': 'MO', 'name': 'Missouri', 'capital': 'Jefferson City'},
            '30': {'code': 'MT', 'name': 'Montana', 'capital': 'Helena'},
            '31': {'code': 'NE', 'name': 'Nebraska', 'capital': 'Lincoln'},
            '32': {'code': 'NV', 'name': 'Nevada', 'capital': 'Carson City'},
            '33': {'code': 'NH', 'name': 'New Hampshire', 'capital': 'Concord'},
            '34': {'code': 'NJ', 'name': 'New Jersey', 'capital': 'Trenton'},
            '35': {'code': 'NM', 'name': 'New Mexico', 'capital': 'Santa Fe'},
            '36': {'code': 'NY', 'name': 'New York', 'capital': 'Albany'},
            '37': {'code': 'NC', 'name': 'North Carolina', 'capital': 'Raleigh'},
            '38': {'code': 'ND', 'name': 'North Dakota', 'capital': 'Bismarck'},
            '39': {'code': 'OH', 'name': 'Ohio', 'capital': 'Columbus'},
            '40': {'code': 'OK', 'name': 'Oklahoma', 'capital': 'Oklahoma City'},
            '41': {'code': 'OR', 'name': 'Oregon', 'capital': 'Salem'},
            '42': {'code': 'PA', 'name': 'Pennsylvania', 'capital': 'Harrisburg'},
            '44': {'code': 'RI', 'name': 'Rhode Island', 'capital': 'Providence'},
            '45': {'code': 'SC', 'name': 'South Carolina', 'capital': 'Columbia'},
            '46': {'code': 'SD', 'name': 'South Dakota', 'capital': 'Pierre'},
            '47': {'code': 'TN', 'name': 'Tennessee', 'capital': 'Nashville'},
            '48': {'code': 'TX', 'name': 'Texas', 'capital': 'Austin'},
            '49': {'code': 'UT', 'name': 'Utah', 'capital': 'Salt Lake City'},
            '50': {'code': 'VT', 'name': 'Vermont', 'capital': 'Montpelier'},
            '51': {'code': 'VA', 'name': 'Virginia', 'capital': 'Richmond'},
            '53': {'code': 'WA', 'name': 'Washington', 'capital': 'Olympia'},
            '54': {'code': 'WV', 'name': 'West Virginia', 'capital': 'Charleston'},
            '55': {'code': 'WI', 'name': 'Wisconsin', 'capital': 'Madison'},
            '56': {'code': 'WY', 'name': 'Wyoming', 'capital': 'Cheyenne'}
        }
        
        return STATE_METADATA.get(state_fips, {})
    
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert string to int, handling null values"""
        if value is None or value == '' or value == '-':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def get_counties_basic(self, year: int = 2022) -> List[Dict]:
        """Get all US counties with basic demographic data"""
        logger.info(f"Fetching US counties data for {year}")
        
        url = f"{self.base_url}/{year}/acs/acs5"
        params = {
            'get': 'NAME,B01001_001E',  # Name and Total Population
            'for': 'county:*'
        }
        
        data = self._make_request(url, params)
        if not data:
            logger.warning("No counties data received, using backup approach")
            return self._get_counties_backup()
        
        # Process response (first row is headers)
        if len(data) < 2:
            return self._get_counties_backup()
        
        headers = data[0]
        counties = []
        
        for row in data[1:]:
            if len(row) >= len(headers):
                county_data = dict(zip(headers, row))
                
                # Get combined FIPS code and state info
                state_fips = county_data.get('state', '')
                county_fips = county_data.get('county', '')
                combined_fips = state_fips + county_fips
                
                # Get state metadata for context
                state_meta = self._get_state_metadata(state_fips)
                
                standardized = {
                    'fips_code': combined_fips,
                    'state_fips': state_fips,
                    'county_fips': county_fips,
                    'name': county_data.get('NAME', ''),
                    'population': self._safe_int(county_data.get('B01001_001E')),
                    'state_name': state_meta.get('name', ''),
                    'state_code': state_meta.get('code', ''),
                    'data_year': year,
                    'last_updated': datetime.now().isoformat()
                }
                
                counties.append(standardized)
        
        # Save to file
        output_file = self.output_dir / f"us_counties_{year}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(counties, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(counties)} counties to {output_file}")
        return counties
    
    def _get_counties_backup(self) -> List[Dict]:
        """Backup county data if API fails"""
        logger.info("Using backup county data")
        
        # Sample counties from major states for backup
        backup_counties = [
            {'fips_code': '06001', 'state_fips': '06', 'county_fips': '001', 'name': 'Alameda County, California', 'state_name': 'California', 'state_code': 'CA'},
            {'fips_code': '06037', 'state_fips': '06', 'county_fips': '037', 'name': 'Los Angeles County, California', 'state_name': 'California', 'state_code': 'CA'},
            {'fips_code': '06075', 'state_fips': '06', 'county_fips': '075', 'name': 'San Francisco County, California', 'state_name': 'California', 'state_code': 'CA'},
            {'fips_code': '12086', 'state_fips': '12', 'county_fips': '086', 'name': 'Miami-Dade County, Florida', 'state_name': 'Florida', 'state_code': 'FL'},
            {'fips_code': '36061', 'state_fips': '36', 'county_fips': '061', 'name': 'New York County, New York', 'state_name': 'New York', 'state_code': 'NY'},
            {'fips_code': '48201', 'state_fips': '48', 'county_fips': '201', 'name': 'Harris County, Texas', 'state_name': 'Texas', 'state_code': 'TX'},
            {'fips_code': '17031', 'state_fips': '17', 'county_fips': '031', 'name': 'Cook County, Illinois', 'state_name': 'Illinois', 'state_code': 'IL'},
            {'fips_code': '04013', 'state_fips': '04', 'county_fips': '013', 'name': 'Maricopa County, Arizona', 'state_name': 'Arizona', 'state_code': 'AZ'},
        ]
        
        for county in backup_counties:
            county['population'] = None
            county['data_year'] = 2024
            county['last_updated'] = datetime.now().isoformat()
            county['data_source'] = 'backup_data'
        
        # Save backup data
        output_file = self.output_dir / "us_counties_backup.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(backup_counties, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(backup_counties)} backup counties to {output_file}")
        return backup_counties

    def download_basic_us_data(self) -> Dict[str, str]:
        """Download basic US data without complex dependencies"""
        logger.info("Starting basic US data download")
        
        results = {}
        
        try:
            # Get all states
            states = self.get_states_basic()
            results['states'] = f"{len(states)} states downloaded"
            
            # Get all counties
            counties = self.get_counties_basic()
            results['counties'] = f"{len(counties)} counties downloaded"
            
            logger.info("Basic US data download completed successfully")
            
        except Exception as e:
            logger.error(f"Error during basic US data download: {e}")
            results['error'] = str(e)
        
        return results


def main():
    """Main execution function"""
    logger.info("Starting simplified US Census data acquisition")
    
    # Initialize Census API
    census_api = SimplifiedUSCensusAPI()
    
    # Download basic US data
    results = census_api.download_basic_us_data()
    
    # Print results
    print("\n" + "="*50)
    print("SIMPLIFIED US CENSUS DATA RESULTS")
    print("="*50)
    for key, value in results.items():
        print(f"{key.upper()}: {value}")
    print("="*50)
    
    logger.info("Simplified US Census data acquisition completed")


if __name__ == "__main__":
    main()