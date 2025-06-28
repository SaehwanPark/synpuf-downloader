#!/usr/bin/env python3
"""
Configuration file for DE-SynPUF 2008-2010 dataset processing
Contains exact URLs, schema definitions, and optimization settings
"""

from typing import Dict, List, Any
import pandas as pd

class DESynPUFConfig:
    """Configuration class for DE-SynPUF dataset processing"""
    
    # Exact download URLs for each sample (1-20)
    BASE_URL = "https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/Downloads"
    
    # File naming patterns for each data type
    FILE_PATTERNS = {
        'beneficiary_2008': 'DE1_0_2008_Beneficiary_Summary_File_Sample_{sample}.zip',
        'beneficiary_2009': 'DE1_0_2009_Beneficiary_Summary_File_Sample_{sample}.zip',
        'beneficiary_2010': 'DE1_0_2010_Beneficiary_Summary_File_Sample_{sample}.zip',
        'inpatient': 'DE1_0_2008_to_2010_Inpatient_Claims_Sample_{sample}.zip',
        'outpatient': 'DE1_0_2008_to_2010_Outpatient_Claims_Sample_{sample}.zip',
        'carrier_1': 'DE1_0_2008_to_2010_Carrier_Claims_Sample_{sample}A.zip',
        'carrier_2': 'DE1_0_2008_to_2010_Carrier_Claims_Sample_{sample}B.zip',
        'prescription': 'DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_{sample}.zip'
    }
    
    # Expected schema for each data type (for validation and optimization)
    SCHEMAS = {
        'beneficiary': {
            'DESYNPUF_ID': 'object',
            'BENE_BIRTH_DT': 'object',
            'BENE_DEATH_DT': 'object',
            'BENE_SEX_IDENT_CD': 'uint8',
            'BENE_RACE_CD': 'uint8',
            'BENE_ESRD_IND': 'object',
            'SP_STATE_CODE': 'uint8',
            'BENE_COUNTY_CD': 'uint16',
            'BENE_HI_CVRAGE_TOT_MONS': 'uint8',
            'BENE_SMI_CVRAGE_TOT_MONS': 'uint8',
            'BENE_HMO_CVRAGE_TOT_MONS': 'uint8',
            'PLAN_CVRG_MOS_NUM': 'uint8',
            'SP_ALZHDMTA': 'uint8',
            'SP_CHF': 'uint8',
            'SP_CHRNKIDN': 'uint8',
            'SP_CNCR': 'uint8',
            'SP_COPD': 'uint8',
            'SP_DEPRESSN': 'uint8',
            'SP_DIABETES': 'uint8',
            'SP_ISCHMCHT': 'uint8',
            'SP_OSTEOPRS': 'uint8',
            'SP_RA_OA': 'uint8',
            'SP_STRKETIA': 'uint8',
            'MEDREIMB_IP': 'float32',
            'BENRES_IP': 'float32',
            'PPPYMT_IP': 'float32',
            'MEDREIMB_OP': 'float32',
            'BENRES_OP': 'float32',
            'PPPYMT_OP': 'float32',
            'MEDREIMB_CAR': 'float32',
            'BENRES_CAR': 'float32',
            'PPPYMT_CAR': 'float32'
        },
        
        'inpatient': {
            'DESYNPUF_ID': 'object',
            'CLM_ID': 'object',
            'SEGMENT': 'uint8',
            'CLM_FROM_DT': 'object',
            'CLM_THRU_DT': 'object',
            'PRVDR_NUM': 'object',
            'CLM_PMT_AMT': 'float32',
            'NCH_PRMRY_PYR_CLM_PD_AMT': 'float32',
            'AT_PHYSN_NPI': 'object',
            'OP_PHYSN_NPI': 'object',
            'OT_PHYSN_NPI': 'object',
            'CLM_ADMSN_DT': 'object',
            'ADMTNG_ICD9_DGNS_CD': 'object',
            'CLM_PASS_THRU_PER_DIEM_AMT': 'float32',
            'NCH_BENE_IP_DDCTBL_AMT': 'float32',
            'NCH_BENE_PTA_COINSRNC_LBLTY_AM': 'float32',
            'NCH_BENE_BLOOD_DDCTBL_LBLTY_AM': 'float32',
            'CLM_UTLZTN_DAY_CNT': 'uint16',
            'NCH_BENE_DSCHRG_DT': 'object',
            'CLM_DRG_CD': 'object'
        },
        
        'outpatient': {
            'DESYNPUF_ID': 'object',
            'CLM_ID': 'object',
            'SEGMENT': 'uint8',
            'CLM_FROM_DT': 'object',
            'CLM_THRU_DT': 'object',
            'PRVDR_NUM': 'object',
            'CLM_PMT_AMT': 'float32',
            'NCH_PRMRY_PYR_CLM_PD_AMT': 'float32',
            'AT_PHYSN_NPI': 'object',
            'OP_PHYSN_NPI': 'object',
            'OT_PHYSN_NPI': 'object',
            'NCH_BENE_BLOOD_DDCTBL_LBLTY_AM': 'float32',
            'ICD9_DGNS_CD_1': 'object',
            'ICD9_DGNS_CD_2': 'object',
            'ICD9_DGNS_CD_3': 'object',
            'ICD9_DGNS_CD_4': 'object',
            'ICD9_DGNS_CD_5': 'object',
            'ICD9_DGNS_CD_6': 'object',
            'ICD9_DGNS_CD_7': 'object',
            'ICD9_DGNS_CD_8': 'object',
            'ICD9_DGNS_CD_9': 'object',
            'ICD9_DGNS_CD_10': 'object',
            'ICD9_PRCDR_CD_1': 'object',
            'ICD9_PRCDR_CD_2': 'object',
            'ICD9_PRCDR_CD_3': 'object',
            'ICD9_PRCDR_CD_4': 'object',
            'ICD9_PRCDR_CD_5': 'object',
            'ICD9_PRCDR_CD_6': 'object',
            'NCH_BENE_PTB_DDCTBL_AMT': 'float32',
            'NCH_BENE_PTB_COINSRNC_AMT': 'float32',
            'ADMTNG_ICD9_DGNS_CD': 'object',
            'HCPCS_CD_1': 'object',
            'HCPCS_CD_2': 'object',
            'HCPCS_CD_3': 'object',
            'HCPCS_CD_4': 'object',
            'HCPCS_CD_5': 'object',
            'HCPCS_CD_6': 'object',
            'HCPCS_CD_7': 'object',
            'HCPCS_CD_8': 'object',
            'HCPCS_CD_9': 'object',
            'HCPCS_CD_10': 'object',
            'HCPCS_CD_11': 'object',
            'HCPCS_CD_12': 'object',
            'HCPCS_CD_13': 'object',
            'HCPCS_CD_14': 'object',
            'HCPCS_CD_15': 'object',
            'HCPCS_CD_16': 'object',
            'HCPCS_CD_17': 'object',
            'HCPCS_CD_18': 'object',
            'HCPCS_CD_19': 'object',
            'HCPCS_CD_20': 'object',
            'HCPCS_CD_21': 'object',
            'HCPCS_CD_22': 'object',
            'HCPCS_CD_23': 'object',
            'HCPCS_CD_24': 'object',
            'HCPCS_CD_25': 'object',
            'HCPCS_CD_26': 'object',
            'HCPCS_CD_27': 'object',
            'HCPCS_CD_28': 'object',
            'HCPCS_CD_29': 'object',
            'HCPCS_CD_30': 'object',
            'HCPCS_CD_31': 'object',
            'HCPCS_CD_32': 'object',
            'HCPCS_CD_33': 'object',
            'HCPCS_CD_34': 'object',
            'HCPCS_CD_35': 'object',
            'HCPCS_CD_36': 'object',
            'HCPCS_CD_37': 'object',
            'HCPCS_CD_38': 'object',
            'HCPCS_CD_39': 'object',
            'HCPCS_CD_40': 'object',
            'HCPCS_CD_41': 'object',
            'HCPCS_CD_42': 'object',
            'HCPCS_CD_43': 'object',
            'HCPCS_CD_44': 'object',
            'HCPCS_CD_45': 'object'
        },
        
        'carrier': {
            'DESYNPUF_ID': 'object',
            'CLM_ID': 'object',
            'CLM_FROM_DT': 'object',
            'CLM_THRU_DT': 'object',
            'ICD9_DGNS_CD_1': 'object',
            'ICD9_DGNS_CD_2': 'object',
            'ICD9_DGNS_CD_3': 'object',
            'ICD9_DGNS_CD_4': 'object',
            'ICD9_DGNS_CD_5': 'object',
            'ICD9_DGNS_CD_6': 'object',
            'ICD9_DGNS_CD_7': 'object',
            'ICD9_DGNS_CD_8': 'object',
            'PRF_PHYSN_NPI_1': 'object',
            'PRF_PHYSN_NPI_2': 'object',
            'PRF_PHYSN_NPI_3': 'object',
            'PRF_PHYSN_NPI_4': 'object',
            'PRF_PHYSN_NPI_5': 'object',
            'PRF_PHYSN_NPI_6': 'object',
            'PRF_PHYSN_NPI_7': 'object',
            'PRF_PHYSN_NPI_8': 'object',
            'PRF_PHYSN_NPI_9': 'object',
            'PRF_PHYSN_NPI_10': 'object',
            'PRF_PHYSN_NPI_11': 'object',
            'PRF_PHYSN_NPI_12': 'object',
            'PRF_PHYSN_NPI_13': 'object',
            'TAX_NUM_1': 'object',
            'TAX_NUM_2': 'object',
            'TAX_NUM_3': 'object',
            'TAX_NUM_4': 'object',
            'TAX_NUM_5': 'object',
            'TAX_NUM_6': 'object',
            'TAX_NUM_7': 'object',
            'TAX_NUM_8': 'object',
            'TAX_NUM_9': 'object',
            'TAX_NUM_10': 'object',
            'TAX_NUM_11': 'object',
            'TAX_NUM_12': 'object',
            'TAX_NUM_13': 'object',
            'HCPCS_CD_1': 'object',
            'HCPCS_CD_2': 'object',
            'HCPCS_CD_3': 'object',
            'HCPCS_CD_4': 'object',
            'HCPCS_CD_5': 'object',
            'HCPCS_CD_6': 'object',
            'HCPCS_CD_7': 'object',
            'HCPCS_CD_8': 'object',
            'HCPCS_CD_9': 'object',
            'HCPCS_CD_10': 'object',
            'HCPCS_CD_11': 'object',
            'HCPCS_CD_12': 'object',
            'HCPCS_CD_13': 'object',
            'LINE_NCH_PMT_AMT_1': 'float32',
            'LINE_NCH_PMT_AMT_2': 'float32',
            'LINE_NCH_PMT_AMT_3': 'float32',
            'LINE_NCH_PMT_AMT_4': 'float32',
            'LINE_NCH_PMT_AMT_5': 'float32',
            'LINE_NCH_PMT_AMT_6': 'float32',
            'LINE_NCH_PMT_AMT_7': 'float32',
            'LINE_NCH_PMT_AMT_8': 'float32',
            'LINE_NCH_PMT_AMT_9': 'float32',
            'LINE_NCH_PMT_AMT_10': 'float32',
            'LINE_NCH_PMT_AMT_11': 'float32',
            'LINE_NCH_PMT_AMT_12': 'float32',
            'LINE_NCH_PMT_AMT_13': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_1': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_2': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_3': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_4': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_5': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_6': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_7': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_8': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_9': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_10': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_11': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_12': 'float32',
            'LINE_BENE_PTB_DDCTBL_AMT_13': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_1': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_2': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_3': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_4': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_5': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_6': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_7': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_8': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_9': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_10': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_11': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_12': 'float32',
            'LINE_BENE_PRMRY_PYR_PD_AMT_13': 'float32',
            'LINE_COINSRNC_AMT_1': 'float32',
            'LINE_COINSRNC_AMT_2': 'float32',
            'LINE_COINSRNC_AMT_3': 'float32',
            'LINE_COINSRNC_AMT_4': 'float32',
            'LINE_COINSRNC_AMT_5': 'float32',
            'LINE_COINSRNC_AMT_6': 'float32',
            'LINE_COINSRNC_AMT_7': 'float32',
            'LINE_COINSRNC_AMT_8': 'float32',
            'LINE_COINSRNC_AMT_9': 'float32',
            'LINE_COINSRNC_AMT_10': 'float32',
            'LINE_COINSRNC_AMT_11': 'float32',
            'LINE_COINSRNC_AMT_12': 'float32',
            'LINE_COINSRNC_AMT_13': 'float32',
            'LINE_ALOWD_CHRG_AMT_1': 'float32',
            'LINE_ALOWD_CHRG_AMT_2': 'float32',
            'LINE_ALOWD_CHRG_AMT_3': 'float32',
            'LINE_ALOWD_CHRG_AMT_4': 'float32',
            'LINE_ALOWD_CHRG_AMT_5': 'float32',
            'LINE_ALOWD_CHRG_AMT_6': 'float32',
            'LINE_ALOWD_CHRG_AMT_7': 'float32',
            'LINE_ALOWD_CHRG_AMT_8': 'float32',
            'LINE_ALOWD_CHRG_AMT_9': 'float32',
            'LINE_ALOWD_CHRG_AMT_10': 'float32',
            'LINE_ALOWD_CHRG_AMT_11': 'float32',
            'LINE_ALOWD_CHRG_AMT_12': 'float32',
            'LINE_ALOWD_CHRG_AMT_13': 'float32',
            'LINE_PRCSG_IND_CD_1': 'object',
            'LINE_PRCSG_IND_CD_2': 'object',
            'LINE_PRCSG_IND_CD_3': 'object',
            'LINE_PRCSG_IND_CD_4': 'object',
            'LINE_PRCSG_IND_CD_5': 'object',
            'LINE_PRCSG_IND_CD_6': 'object',
            'LINE_PRCSG_IND_CD_7': 'object',
            'LINE_PRCSG_IND_CD_8': 'object',
            'LINE_PRCSG_IND_CD_9': 'object',
            'LINE_PRCSG_IND_CD_10': 'object',
            'LINE_PRCSG_IND_CD_11': 'object',
            'LINE_PRCSG_IND_CD_12': 'object',
            'LINE_PRCSG_IND_CD_13': 'object',
            'LINE_ICD9_DGNS_CD_1': 'object',
            'LINE_ICD9_DGNS_CD_2': 'object',
            'LINE_ICD9_DGNS_CD_3': 'object',
            'LINE_ICD9_DGNS_CD_4': 'object',
            'LINE_ICD9_DGNS_CD_5': 'object',
            'LINE_ICD9_DGNS_CD_6': 'object',
            'LINE_ICD9_DGNS_CD_7': 'object',
            'LINE_ICD9_DGNS_CD_8': 'object',
            'LINE_ICD9_DGNS_CD_9': 'object',
            'LINE_ICD9_DGNS_CD_10': 'object',
            'LINE_ICD9_DGNS_CD_11': 'object',
            'LINE_ICD9_DGNS_CD_12': 'object',
            'LINE_ICD9_DGNS_CD_13': 'object'
        },
        
        'prescription': {
            'DESYNPUF_ID': 'object',
            'PDE_ID': 'object',
            'SRVC_DT': 'object',
            'PROD_SRVC_ID': 'object',
            'QTY_DSPNSD_NUM': 'float32',
            'DAYS_SUPLY_NUM': 'uint16',
            'PTNT_PAY_AMT': 'float32',
            'TOT_RX_CST_AMT': 'float32'
        }
    }
    
    # Data type optimizations for memory efficiency
    DTYPE_OPTIMIZATIONS = {
        # Common patterns for automatic dtype optimization
        'id_patterns': ['_ID', '_CD', '_NUM'],
        'date_patterns': ['_DT'],
        'amount_patterns': ['_AMT', '_CST'],
        'count_patterns': ['_CNT', '_MONS', '_DAY'],
        'indicator_patterns': ['_IND', '_CD']
    }
    
    # Parquet write optimization settings
    PARQUET_SETTINGS = {
        'compression': 'snappy',  # Good balance of speed and compression
        'row_group_size': 100_000,  # Optimize for 100k rows per row group
        'write_batch_size': 10_000,
        'use_threads': True,
        'max_partitions': 1000,
        'basename_template': "part-{i}.snappy.parquet"
    }
    
    # Download settings
    DOWNLOAD_SETTINGS = {
        'max_concurrent_downloads': 5,
        'chunk_size': 8192,
        'timeout_seconds': 3600,  # 1 hour timeout
        'retry_attempts': 3,
        'retry_delay': 5  # seconds
    }
    
    @classmethod
    def get_download_urls(cls, samples: List[int]) -> Dict[str, List[str]]:
        """Generate download URLs for specified samples"""
        urls = {key: [] for key in cls.FILE_PATTERNS.keys()}
        
        for sample in samples:
            for file_type, pattern in cls.FILE_PATTERNS.items():
                filename = pattern.format(sample=sample)
                url = f"{cls.BASE_URL}/{filename}"
                urls[file_type].append(url)
        
        return urls
    
    @classmethod
    def get_optimized_dtypes(cls, data_type: str) -> Dict[str, str]:
        """Get optimized data types for a specific dataset"""
        if data_type in cls.SCHEMAS:
            return cls.SCHEMAS[data_type].copy()
        else:
            return {}
    
    @classmethod
    def validate_partition_strategy(cls, df: pd.DataFrame) -> bool:
        """Validate that DESYNPUF_ID exists for partitioning"""
        if 'DESYNPUF_ID' not in df.columns:
            return False
        
        # Check if IDs are properly formatted
        sample_ids = df['DESYNPUF_ID'].dropna().head(1000)
        if sample_ids.empty:
            return False
        
        # Should be alphanumeric strings
        return all(isinstance(id_val, str) and len(id_val) >= 2 for id_val in sample_ids)


# Enhanced pipeline class with configuration
class EnhancedDESynPUFPipeline:
    """Enhanced pipeline class using configuration settings"""
    
    def __init__(self, config: DESynPUFConfig = None, **kwargs):
        self.config = config or DESynPUFConfig()
        
        # Override default settings with kwargs
        self.raw_data_dir = Path(kwargs.get('raw_data_dir', 'raw_data'))
        self.output_dir = Path(kwargs.get('output_dir', 'parquet_data'))
        
        # Use config settings
        download_settings = self.config.DOWNLOAD_SETTINGS
        self.max_concurrent_downloads = kwargs.get('max_concurrent_downloads', 
                                                  download_settings['max_concurrent_downloads'])
        self.chunk_size = kwargs.get('chunk_size', download_settings['chunk_size'])
        self.timeout_seconds = kwargs.get('timeout_seconds', download_settings['timeout_seconds'])
        
        # Create directories
        self.raw_data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def get_optimized_read_kwargs(self, data_type: str) -> Dict[str, Any]:
        """Get optimized pandas read_csv kwargs for specific data type"""
        base_kwargs = {
            'low_memory': False,
            'na_values': ['', 'NULL', 'null', 'NaN'],
            'keep_default_na': True
        }
        
        # Add dtype optimization if available
        dtypes = self.config.get_optimized_dtypes(data_type)
        if dtypes:
            base_kwargs['dtype'] = dtypes
        
        return base_kwargs
    
    def get_parquet_write_kwargs(self) -> Dict[str, Any]:
        """Get optimized parquet write kwargs"""
        return self.config.PARQUET_SETTINGS.copy()


# Utility functions for working with partitioned data
def analyze_partition_distribution(parquet_path: str) -> Dict[str, Any]:
    """Analyze partition distribution in a partitioned dataset"""
    import pyarrow.parquet as pq
    from collections import Counter
    
    dataset = pq.ParquetDataset(parquet_path)
    
    # Extract partition information
    partition_info = []
    total_rows = 0
    
    for piece in dataset.pieces:
        metadata = piece.get_metadata()
        rows = metadata.num_rows
        total_rows += rows
        
        # Extract partition key from path
        path_parts = str(piece.path).split('/')
        partition_key = None
        for part in path_parts:
            if 'partition_id=' in part:
                partition_key = part.split('=')[1]
                break
        
        partition_info.append({
            'partition_key': partition_key,
            'rows': rows,
            'file_size_mb': metadata.serialized_size / (1024 * 1024)
        })
    
    # Calculate statistics
    partition_counts = Counter(info['partition_key'] for info in partition_info)
    row_distribution = {key: sum(info['rows'] for info in partition_info 
                                if info['partition_key'] == key) 
                       for key in partition_counts.keys()}
    
    return {
        'total_partitions': len(partition_counts),
        'total_rows': total_rows,
        'partition_distribution': dict(partition_counts),
        'row_distribution': row_distribution,
        'avg_rows_per_partition': total_rows / len(partition_counts) if partition_counts else 0,
        'partition_info': partition_info
    }


def create_sample_query_examples():
    """Create example queries for working with the partitioned data"""
    examples = {
        'load_specific_partitions': '''
# Load data from specific partitions (last 2 digits of DESYNPUF_ID)
beneficiary_subset = read_partitioned_data('beneficiary', partition_ids=['00', '01', '05'])
        ''',
        
        'filter_by_conditions': '''
# Filter beneficiary data for diabetes patients
import pyarrow.parquet as pq
import pyarrow.compute as pc

dataset = pq.ParquetDataset('parquet_data/beneficiary')
diabetes_filter = pc.equal(pc.field('SP_DIABETES'), 1)
diabetes_patients = dataset.read(filter=diabetes_filter).to_pandas()
        ''',
        
        'join_across_datasets': '''
# Join beneficiary and inpatient data
beneficiary_df = pd.read_parquet('parquet_data/beneficiary')
inpatient_df = pd.read_parquet('parquet_data/inpatient')

# Join on DESYNPUF_ID
joined_data = beneficiary_df.merge(
    inpatient_df, 
    on='DESYNPUF_ID', 
    how='inner'
)
        ''',
        
        'memory_efficient_processing': '''
# Process large datasets in chunks using PyArrow
import pyarrow.parquet as pq

dataset = pq.ParquetDataset('parquet_data/carrier')
total_payments = 0
patient_count = 0

# Process in batches to manage memory
for batch in dataset.to_batches(batch_size=10000):
    df_batch = batch.to_pandas()
    
    # Your processing logic here
    total_payments += df_batch['LINE_NCH_PMT_AMT_1'].sum()
    patient_count += df_batch['DESYNPUF_ID'].nunique()
        '''
    }
    
    return examples


# Example usage configurations
EXAMPLE_CONFIGS = {
    'small_test': {
        'samples': [1, 2],  # Just first 2 samples for testing
        'data_types': ['beneficiary', 'inpatient']  # Subset of data types
    },
    
    'medium_dataset': {
        'samples': list(range(1, 11)),  # First 10 samples (2.5% of Medicare population)
        'data_types': ['beneficiary', 'inpatient', 'outpatient', 'prescription']
    },
    
    'full_dataset': {
        'samples': list(range(1, 21)),  # All 20 samples (5% of Medicare population)
        'data_types': ['beneficiary', 'inpatient', 'outpatient', 'carrier', 'prescription']
    }
}

if __name__ == "__main__":
    # Example usage
    config = DESynPUFConfig()
    
    # Get URLs for first 3 samples
    urls = config.get_download_urls([1, 2, 3])
    print("Example URLs:")
    for data_type, url_list in urls.items():
        print(f"{data_type}: {len(url_list)} files")
        if url_list:
            print(f"  Example: {url_list[0]}")
    
    # Show schema info
    print(f"\nAvailable schemas: {list(config.SCHEMAS.keys())}")
    print(f"Beneficiary schema has {len(config.SCHEMAS['beneficiary'])} columns")
    
    # Show example queries
    examples = create_sample_query_examples()
    print(f"\nAvailable query examples: {list(examples.keys())}")