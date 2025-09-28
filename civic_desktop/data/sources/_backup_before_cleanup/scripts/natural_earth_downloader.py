"""
Natural Earth Data Downloader
High-quality geographic boundaries and administrative data
"""

import requests
import zipfile
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NaturalEarthDownloader:
    """Download and process Natural Earth geographic data"""
    
    def __init__(self, data_dir: str = "raw_data/natural_earth"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://naciscdn.org/naturalearth"
        
        # Available resolutions
        self.resolutions = ["110m", "50m", "10m"]  # Low, Medium, High resolution
        
        # Available datasets
        self.datasets = {
            # Cultural datasets
            'countries': 'ne_{res}_admin_0_countries.zip',
            'states_provinces': 'ne_{res}_admin_1_states_provinces_lakes.zip',
            'populated_places': 'ne_{res}_populated_places.zip',
            'urban_areas': 'ne_{res}_urban_areas.zip',
            
            # Physical datasets  
            'coastline': 'ne_{res}_coastline.zip',
            'land': 'ne_{res}_land.zip',
            'ocean': 'ne_{res}_ocean.zip',
            'rivers_lakes': 'ne_{res}_rivers_lake_centerlines.zip',
            
            # Administrative boundaries
            'admin_0_boundary_lines': 'ne_{res}_admin_0_boundary_lines_land.zip',
            'admin_1_boundary_lines': 'ne_{res}_admin_1_boundary_lines_land.zip'
        }
    
    def download_dataset(self, dataset: str, resolution: str = "50m") -> Optional[str]:
        """Download a specific Natural Earth dataset"""
        if dataset not in self.datasets:
            logger.error(f"Unknown dataset: {dataset}")
            return None
        
        if resolution not in self.resolutions:
            logger.error(f"Invalid resolution: {resolution}. Use one of {self.resolutions}")
            return None
        
        filename = self.datasets[dataset].format(res=resolution)
        category = "cultural" if dataset in ['countries', 'states_provinces', 'populated_places', 'urban_areas'] else "physical"
        url = f"{self.base_url}/{resolution}/{category}/{filename}"
        
        logger.info(f"Downloading {dataset} at {resolution} resolution...")
        
        return self._download_and_extract(url, filename, dataset)
    
    def _download_and_extract(self, url: str, filename: str, dataset_name: str) -> Optional[str]:
        """Download and extract shapefile"""
        file_path = self.data_dir / filename
        extracted_dir = self.data_dir / dataset_name
        
        try:
            # Check if already extracted
            if extracted_dir.exists() and any(extracted_dir.iterdir()):
                logger.info(f"Dataset {dataset_name} already exists, skipping download")
                return str(extracted_dir)
            
            # Download file if not exists
            if not file_path.exists():
                logger.info(f"Downloading from {url}")
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Simple progress indicator
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                if downloaded % (1024 * 1024) == 0:  # Every MB
                                    logger.info(f"Downloaded {percent:.1f}%")
            
            # Extract zip file
            extracted_dir.mkdir(exist_ok=True)
            logger.info(f"Extracting {filename}")
            
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_dir)
            
            # Clean up zip file to save space
            file_path.unlink()
            logger.info(f"Extraction complete: {extracted_dir}")
            
            return str(extracted_dir)
            
        except Exception as e:
            logger.error(f"Error downloading/extracting {dataset_name}: {e}")
            return None
    
    def download_countries(self, resolution: str = "50m") -> Optional[str]:
        """Download country boundaries shapefile"""
        return self.download_dataset('countries', resolution)
    
    def download_states_provinces(self, resolution: str = "50m") -> Optional[str]:
        """Download state/province boundaries shapefile"""  
        return self.download_dataset('states_provinces', resolution)
    
    def download_populated_places(self, resolution: str = "50m") -> Optional[str]:
        """Download populated places (cities) shapefile"""
        return self.download_dataset('populated_places', resolution)
    
    def download_all_cultural_data(self, resolution: str = "50m") -> Dict[str, Optional[str]]:
        """Download all cultural/administrative datasets"""
        logger.info(f"Downloading all cultural data at {resolution} resolution")
        
        cultural_datasets = ['countries', 'states_provinces', 'populated_places', 'urban_areas']
        results = {}
        
        for dataset in cultural_datasets:
            result = self.download_dataset(dataset, resolution)
            results[dataset] = result
            
            # Small delay between downloads to be respectful
            time.sleep(1)
        
        return results
    
    def process_countries_to_json(self, resolution: str = "50m") -> Optional[str]:
        """Process countries shapefile to JSON format"""
        try:
            import geopandas as gpd
        except ImportError:
            logger.error("geopandas not available. Install with: pip install geopandas")
            return None
        
        # Download if not exists
        countries_dir = self.download_countries(resolution)
        if not countries_dir:
            return None
        
        # Find the shapefile
        countries_path = Path(countries_dir)
        shp_files = list(countries_path.glob("*.shp"))
        
        if not shp_files:
            logger.error(f"No shapefile found in {countries_path}")
            return None
        
        shp_file = shp_files[0]
        logger.info(f"Processing {shp_file}")
        
        try:
            # Read shapefile
            gdf = gpd.read_file(shp_file)
            
            # Convert to standard format
            countries_data = []
            
            for _, row in gdf.iterrows():
                country = {
                    'iso_code_2': row.get('ISO_A2'),
                    'iso_code_3': row.get('ISO_A3'), 
                    'country_name': row.get('NAME'),
                    'official_name': row.get('NAME_LONG'),
                    'continent': row.get('CONTINENT'),
                    'region': row.get('REGION_UN'),
                    'subregion': row.get('SUBREGION'),
                    'population': row.get('POP_EST'),
                    'area_km2': row.get('POP_EST'),
                    'gdp_estimate': row.get('GDP_MD_EST'),
                    'economy': row.get('ECONOMY'),
                    'government_type': row.get('TYPE'),
                    'coordinates': {
                        'latitude': row.get('LAB_Y'),
                        'longitude': row.get('LAB_X')
                    },
                    'geometry': row.geometry.__geo_interface__ if hasattr(row.geometry, '__geo_interface__') else None
                }
                
                countries_data.append(country)
            
            # Save as JSON
            output_file = self.data_dir / f"countries_{resolution}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(countries_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(countries_data)} countries to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error processing countries shapefile: {e}")
            return None
    
    def process_states_to_json(self, resolution: str = "50m") -> Optional[str]:
        """Process states/provinces shapefile to JSON format"""
        try:
            import geopandas as gpd
        except ImportError:
            logger.error("geopandas not available. Install with: pip install geopandas")
            return None
        
        # Download if not exists
        states_dir = self.download_states_provinces(resolution)
        if not states_dir:
            return None
        
        # Find the shapefile
        states_path = Path(states_dir)
        shp_files = list(states_path.glob("*.shp"))
        
        if not shp_files:
            logger.error(f"No shapefile found in {states_path}")
            return None
        
        shp_file = shp_files[0]
        logger.info(f"Processing {shp_file}")
        
        try:
            # Read shapefile
            gdf = gpd.read_file(shp_file)
            
            # Convert to standard format
            states_data = []
            
            for _, row in gdf.iterrows():
                state = {
                    'iso_code': row.get('iso_3166_2'),
                    'country_code': row.get('iso_a2'),
                    'state_name': row.get('name'),
                    'name_local': row.get('name_local'),
                    'type': row.get('type_en'),
                    'region': row.get('region'),
                    'population': row.get('pop_est'),
                    'area_km2': row.get('area_km2'),
                    'coordinates': {
                        'latitude': row.get('latitude'),
                        'longitude': row.get('longitude')
                    },
                    'geometry': row.geometry.__geo_interface__ if hasattr(row.geometry, '__geo_interface__') else None
                }
                
                states_data.append(state)
            
            # Save as JSON
            output_file = self.data_dir / f"states_provinces_{resolution}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(states_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(states_data)} states/provinces to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error processing states shapefile: {e}")
            return None
    
    def generate_summary_report(self) -> Dict[str, any]:
        """Generate a summary report of downloaded data"""
        logger.info("Generating summary report")
        
        summary = {
            'download_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'data_directory': str(self.data_dir),
            'datasets': {}
        }
        
        # Check what's been downloaded
        for dataset_name in self.datasets.keys():
            dataset_dir = self.data_dir / dataset_name
            if dataset_dir.exists():
                files = list(dataset_dir.iterdir())
                summary['datasets'][dataset_name] = {
                    'downloaded': True,
                    'files_count': len(files),
                    'directory_size_mb': sum(f.stat().st_size for f in files if f.is_file()) / (1024 * 1024)
                }
            else:
                summary['datasets'][dataset_name] = {'downloaded': False}
        
        # Save summary
        summary_file = self.data_dir / "download_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary saved to {summary_file}")
        return summary


def main():
    """Main execution function"""
    logger.info("Starting Natural Earth data download")
    
    # Initialize downloader
    downloader = NaturalEarthDownloader()
    
    print("Natural Earth Data Downloader")
    print("=" * 40)
    print("Available datasets:")
    for i, dataset in enumerate(downloader.datasets.keys(), 1):
        print(f"{i}. {dataset}")
    
    print("\nDownloading essential datasets...")
    
    # Download core datasets
    results = {}
    
    # Countries (essential for any civic platform)
    logger.info("Downloading countries...")
    countries_result = downloader.download_countries("50m")
    results['countries'] = countries_result
    
    # States/Provinces (for administrative boundaries)
    logger.info("Downloading states/provinces...")
    states_result = downloader.download_states_provinces("50m")
    results['states_provinces'] = states_result
    
    # Populated places (cities and towns)
    logger.info("Downloading populated places...")
    places_result = downloader.download_populated_places("50m")
    results['populated_places'] = places_result
    
    # Process to JSON format (if geopandas available)
    try:
        import geopandas
        logger.info("Processing countries to JSON...")
        countries_json = downloader.process_countries_to_json("50m")
        results['countries_json'] = countries_json
        
        logger.info("Processing states to JSON...")
        states_json = downloader.process_states_to_json("50m")
        results['states_json'] = states_json
        
    except ImportError:
        logger.warning("geopandas not available - skipping JSON processing")
        logger.info("To enable JSON processing, install: pip install geopandas")
    
    # Generate summary
    summary = downloader.generate_summary_report()
    
    # Print results
    print("\n" + "="*50)
    print("NATURAL EARTH DOWNLOAD RESULTS")
    print("="*50)
    for key, value in results.items():
        status = "SUCCESS" if value else "FAILED"
        print(f"{key.upper()}: {status}")
    
    print(f"\nTotal datasets downloaded: {sum(1 for v in results.values() if v)}")
    print(f"Data directory: {downloader.data_dir}")
    print("="*50)
    
    logger.info("Natural Earth data download completed")


if __name__ == "__main__":
    main()