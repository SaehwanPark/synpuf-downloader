#!/usr/bin/env python3
"""
Streamlined DE-SynPUF 2008-2010 Data Pipeline
Downloads, extracts, concatenates, and converts to partitioned Parquet files

Dataset structure per sample (1-20):
- 3 Beneficiary files (2008, 2009, 2010)
- 1 Inpatient Claims file (2008-2010)
- 1 Outpatient Claims file (2008-2010)  
- 2 Carrier Claims files (2008-2010)
- 1 Prescription Drug Events file (2008-2010)
"""

import asyncio
import aiohttp
import aiofiles
import zipfile
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
import logging
from typing import List, Dict, Tuple
import time
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DESynPUFPipeline:
    """Streamlined pipeline for DE-SynPUF data processing"""
    
    def __init__(self, 
                 raw_data_dir: str = "raw_data",
                 output_dir: str = "parquet_data",
                 max_concurrent_downloads: int = 5,
                 chunk_size: int = 8192):
        self.raw_data_dir = Path(raw_data_dir)
        self.output_dir = Path(output_dir)
        self.max_concurrent_downloads = max_concurrent_downloads
        self.chunk_size = chunk_size
        
        # Create directories
        self.raw_data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # CMS base URL pattern
        self.base_url = "https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/Downloads"
        
        # File mapping per sample
        self.file_patterns = {
            'beneficiary_2008': 'DE1_0_2008_Beneficiary_Summary_File_Sample_{sample}.zip',
            'beneficiary_2009': 'DE1_0_2009_Beneficiary_Summary_File_Sample_{sample}.zip', 
            'beneficiary_2010': 'DE1_0_2010_Beneficiary_Summary_File_Sample_{sample}.zip',
            'inpatient': 'DE1_0_2008_to_2010_Inpatient_Claims_Sample_{sample}.zip',
            'outpatient': 'DE1_0_2008_to_2010_Outpatient_Claims_Sample_{sample}.zip',
            'carrier_1': 'DE1_0_2008_to_2010_Carrier_Claims_Sample_{sample}A.zip',
            'carrier_2': 'DE1_0_2008_to_2010_Carrier_Claims_Sample_{sample}B.zip',
            'prescription': 'DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_{sample}.zip'
        }
    
    async def download_file(self, session: aiohttp.ClientSession, url: str, filepath: Path) -> bool:
        """Download a single file asynchronously"""
        try:
            if filepath.exists():
                logger.info(f"File already exists: {filepath.name}")
                return True
                
            logger.info(f"Downloading: {filepath.name}")
            async with session.get(url) as response:
                if response.status == 200:
                    async with aiofiles.open(filepath, 'wb') as f:
                        async for chunk in response.content.iter_chunked(self.chunk_size):
                            await f.write(chunk)
                    logger.info(f"Downloaded: {filepath.name}")
                    return True
                else:
                    logger.error(f"Failed to download {url}: Status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return False
    
    async def download_all_samples(self, samples: List[int] = None) -> Dict[str, List[Path]]:
        """Download all files for specified samples"""
        if samples is None:
            samples = list(range(1, 21))  # Samples 1-20
        
        download_tasks = []
        file_paths = {key: [] for key in self.file_patterns.keys()}
        
        connector = aiohttp.TCPConnector(limit=self.max_concurrent_downloads)
        timeout = aiohttp.ClientTimeout(total=3600)  # 1 hour timeout
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for sample in samples:
                for file_type, pattern in self.file_patterns.items():
                    filename = pattern.format(sample=sample)
                    url = f"{self.base_url}/{filename}"
                    filepath = self.raw_data_dir / filename
                    
                    download_tasks.append(self.download_file(session, url, filepath))
                    file_paths[file_type].append(filepath)
            
            # Execute downloads with concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent_downloads)
            
            async def sem_download(task):
                async with semaphore:
                    return await task
            
            results = await asyncio.gather(*[sem_download(task) for task in download_tasks])
            
        successful_downloads = sum(results)
        total_downloads = len(download_tasks)
        logger.info(f"Downloaded {successful_downloads}/{total_downloads} files successfully")
        
        return file_paths
    
    def extract_zip_files(self, file_paths: Dict[str, List[Path]]) -> Dict[str, List[Path]]:
        """Extract all ZIP files and return CSV file paths"""
        csv_paths = {key: [] for key in file_paths.keys()}
        
        for file_type, zip_paths in file_paths.items():
            for zip_path in zip_paths:
                if not zip_path.exists():
                    logger.warning(f"ZIP file not found: {zip_path}")
                    continue
                
                extract_dir = zip_path.parent / zip_path.stem
                extract_dir.mkdir(exist_ok=True)
                
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_dir)
                    
                    # Find CSV files in extracted directory
                    csv_files = list(extract_dir.glob("*.csv"))
                    csv_paths[file_type].extend(csv_files)
                    
                    logger.info(f"Extracted {len(csv_files)} CSV files from {zip_path.name}")
                    
                except Exception as e:
                    logger.error(f"Error extracting {zip_path}: {e}")
        
        return csv_paths
    
    def read_and_concatenate_csvs(self, csv_paths: List[Path], file_type: str) -> pd.DataFrame:
        """Read and concatenate CSV files with optimized data types"""
        dfs = []
        
        # Read first file to get schema
        if not csv_paths:
            logger.warning(f"No CSV files found for {file_type}")
            return pd.DataFrame()
        
        logger.info(f"Processing {len(csv_paths)} files for {file_type}")
        
        # Read first file to determine dtypes
        first_df = pd.read_csv(csv_paths[0], nrows=1000)
        
        # Optimize dtypes for memory efficiency
        dtype_map = {}
        for col in first_df.columns:
            if first_df[col].dtype == 'object':
                # Try to convert to category if reasonable cardinality
                unique_vals = first_df[col].nunique()
                if unique_vals < len(first_df) * 0.5:  # Less than 50% unique
                    dtype_map[col] = 'category'
            elif first_df[col].dtype in ['int64']:
                # Try smaller int types
                if first_df[col].min() >= 0:
                    if first_df[col].max() < 2**16:
                        dtype_map[col] = 'uint16'
                    elif first_df[col].max() < 2**32:
                        dtype_map[col] = 'uint32'
                else:
                    if first_df[col].min() >= -2**15 and first_df[col].max() < 2**15:
                        dtype_map[col] = 'int16'
                    elif first_df[col].min() >= -2**31 and first_df[col].max() < 2**31:
                        dtype_map[col] = 'int32'
        
        # Read all files with optimized dtypes
        for csv_path in csv_paths:
            try:
                df = pd.read_csv(
                    csv_path,
                    dtype=dtype_map,
                    low_memory=False
                )
                dfs.append(df)
                logger.info(f"Read {csv_path.name}: {len(df):,} rows")
            except Exception as e:
                logger.error(f"Error reading {csv_path}: {e}")
        
        if dfs:
            concatenated_df = pd.concat(dfs, ignore_index=True)
            logger.info(f"Concatenated {file_type}: {len(concatenated_df):,} total rows")
            return concatenated_df
        else:
            return pd.DataFrame()
    
    def create_partition_key(self, df: pd.DataFrame) -> pd.Series:
        """Create partition key from last 2 digits of DESYNPUF_ID"""
        if 'DESYNPUF_ID' not in df.columns:
            logger.error("DESYNPUF_ID column not found")
            return pd.Series(['00'] * len(df))
        
        # Extract last 2 characters and pad with zeros if needed
        partition_key = df['DESYNPUF_ID'].astype(str).str[-2:].str.zfill(2)
        return partition_key
    
    def write_to_parquet(self, df: pd.DataFrame, file_type: str) -> None:
        """Write DataFrame to partitioned Parquet files using PyArrow"""
        if df.empty:
            logger.warning(f"Empty DataFrame for {file_type}, skipping")
            return
        
        # Add partition column
        df['partition_id'] = self.create_partition_key(df)
        
        # Convert to PyArrow Table for better performance
        table = pa.Table.from_pandas(df)
        
        # Define output path
        output_path = self.output_dir / file_type
        
        # Write partitioned dataset
        try:
            pq.write_to_dataset(
                table,
                root_path=str(output_path),
                partition_cols=['partition_id'],
                compression='snappy',  # Good balance of speed and compression
                use_threads=True,      # Enable parallel writing
                existing_data_behavior='overwrite_or_ignore',
                # Row group size optimization for large datasets
                row_group_size=100_000,  # Approximately 100k rows per row group
                # Write options
                write_batch_size=10_000,
                max_partitions=1000,
                basename_template="part-{i}.snappy.parquet"
            )
            
            logger.info(f"Written {file_type} to partitioned Parquet: {output_path}")
            
            # Log partition information
            dataset = pq.ParquetDataset(str(output_path))
            logger.info(f"Created {len(dataset.pieces)} partitions for {file_type}")
            
        except Exception as e:
            logger.error(f"Error writing {file_type} to Parquet: {e}")
    
    def merge_beneficiary_files(self, csv_paths: Dict[str, List[Path]]) -> pd.DataFrame:
        """Merge beneficiary files from all years"""
        beneficiary_dfs = []
        
        for year in ['2008', '2009', '2010']:
            year_key = f'beneficiary_{year}'
            if year_key in csv_paths and csv_paths[year_key]:
                year_df = self.read_and_concatenate_csvs(csv_paths[year_key], year_key)
                if not year_df.empty:
                    year_df['BENE_YEAR'] = int(year)
                    beneficiary_dfs.append(year_df)
        
        if beneficiary_dfs:
            return pd.concat(beneficiary_dfs, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def merge_carrier_files(self, csv_paths: Dict[str, List[Path]]) -> pd.DataFrame:
        """Merge carrier files (Part A and Part B)"""
        carrier_dfs = []
        
        for part in ['carrier_1', 'carrier_2']:
            if part in csv_paths and csv_paths[part]:
                part_df = self.read_and_concatenate_csvs(csv_paths[part], part)
                if not part_df.empty:
                    carrier_dfs.append(part_df)
        
        if carrier_dfs:
            return pd.concat(carrier_dfs, ignore_index=True)
        else:
            return pd.DataFrame()
    
    async def run_pipeline(self, samples: List[int] = None) -> None:
        """Execute the complete pipeline"""
        start_time = time.time()
        logger.info("Starting DE-SynPUF data pipeline")
        
        # Step 1: Download files
        logger.info("Step 1: Downloading files...")
        file_paths = await self.download_all_samples(samples)
        
        # Step 2: Extract ZIP files
        logger.info("Step 2: Extracting ZIP files...")
        csv_paths = self.extract_zip_files(file_paths)
        
        # Step 3: Process each data type
        logger.info("Step 3: Processing and converting to Parquet...")
        
        # Process beneficiary data (merge all years)
        logger.info("Processing beneficiary data...")
        beneficiary_df = self.merge_beneficiary_files(csv_paths)
        if not beneficiary_df.empty:
            self.write_to_parquet(beneficiary_df, 'beneficiary')
        
        # Process claims data
        claims_types = ['inpatient', 'outpatient', 'prescription']
        for claim_type in claims_types:
            if claim_type in csv_paths:
                logger.info(f"Processing {claim_type} data...")
                df = self.read_and_concatenate_csvs(csv_paths[claim_type], claim_type)
                if not df.empty:
                    self.write_to_parquet(df, claim_type)
        
        # Process carrier data (merge both parts)
        logger.info("Processing carrier data...")
        carrier_df = self.merge_carrier_files(csv_paths)
        if not carrier_df.empty:
            self.write_to_parquet(carrier_df, 'carrier')
        
        elapsed_time = time.time() - start_time
        logger.info(f"Pipeline completed in {elapsed_time:.2f} seconds")
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self) -> None:
        """Generate a summary report of the processed data"""
        logger.info("Generating summary report...")
        
        summary = {}
        for data_type in ['beneficiary', 'inpatient', 'outpatient', 'carrier', 'prescription']:
            parquet_path = self.output_dir / data_type
            if parquet_path.exists():
                try:
                    dataset = pq.ParquetDataset(str(parquet_path))
                    total_rows = sum(piece.get_metadata().num_rows for piece in dataset.pieces)
                    partitions = len(dataset.pieces)
                    
                    summary[data_type] = {
                        'total_rows': total_rows,
                        'partitions': partitions,
                        'path': str(parquet_path)
                    }
                except Exception as e:
                    logger.error(f"Error reading {data_type} metadata: {e}")
        
        logger.info("=== DE-SynPUF Processing Summary ===")
        for data_type, info in summary.items():
            logger.info(f"{data_type.upper()}:")
            logger.info(f"  Rows: {info['total_rows']:,}")
            logger.info(f"  Partitions: {info['partitions']}")
            logger.info(f"  Path: {info['path']}")


# Example usage and helper functions
def run_full_pipeline():
    """Run the complete pipeline for all samples"""
    pipeline = DESynPUFPipeline()
    asyncio.run(pipeline.run_pipeline())

def run_sample_pipeline(samples: List[int]):
    """Run pipeline for specific samples"""
    pipeline = DESynPUFPipeline()
    asyncio.run(pipeline.run_pipeline(samples))

def read_partitioned_data(data_type: str, partition_ids: List[str] = None) -> pd.DataFrame:
    """
    Read data from partitioned Parquet files
    
    Args:
        data_type: Type of data ('beneficiary', 'inpatient', etc.)
        partition_ids: List of partition IDs to read (e.g., ['00', '01'])
    """
    output_dir = Path("parquet_data")
    parquet_path = output_dir / data_type
    
    if not parquet_path.exists():
        logger.error(f"Parquet data not found for {data_type}")
        return pd.DataFrame()
    
    if partition_ids:
        # Read specific partitions
        dfs = []
        for partition_id in partition_ids:
            partition_path = parquet_path / f"partition_id={partition_id}"
            if partition_path.exists():
                df = pd.read_parquet(partition_path)
                dfs.append(df)
        
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        else:
            return pd.DataFrame()
    else:
        # Read all partitions
        return pd.read_parquet(parquet_path)

if __name__ == "__main__":
    # Example: Run pipeline for samples 1-5
    samples_to_process = list(range(1, 6))  # Samples 1-5
    run_sample_pipeline(samples_to_process)
    
    # Example: Read specific partitions
    # beneficiary_data = read_partitioned_data('beneficiary', ['00', '01', '02'])
    # print(f"Loaded {len(beneficiary_data):,} beneficiary records")