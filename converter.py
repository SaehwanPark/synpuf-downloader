#!/usr/bin/env python3
"""
SynPUF CSV to Parquet Converter

Converts CMS SynPUF CSV files to partitioned Parquet format using PyArrow.
Handles large files efficiently and combines carrier claims A/B files.
"""

import argparse
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pyarrow as pa
import pyarrow.csv as pv
import pyarrow.dataset as ds
import pyarrow.parquet as pq
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()


class SynPUFConverter:
    """Converts SynPUF CSV files to partitioned Parquet format."""
    
    def __init__(self, synpuf_dir: str, log_level: str = 'INFO'):
        """Initialize the converter.
        
        Args:
            synpuf_dir: Base SynPUF directory
            log_level: Logging level
        """
        self.synpuf_dir = Path(synpuf_dir)
        self.csv_dir = self.synpuf_dir / "csv_files"
        self.parquet_dir = self.synpuf_dir / "parquets"
        self.log_dir = self.synpuf_dir / "logs"
        
        # Create directories
        self.parquet_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging(log_level)
        
        # File patterns for grouping
        self.file_patterns = {
            'beneficiary_2008': r'DE1_0_2008_Beneficiary_Summary_File_Sample_(\d+)\.csv',
            'beneficiary_2009': r'DE1_0_2009_Beneficiary_Summary_File_Sample_(\d+)\.csv',
            'beneficiary_2010': r'DE1_0_2010_Beneficiary_Summary_File_Sample_(\d+)\.csv',
            'carrier_a': r'DE1_0_2008_to_2010_Carrier_Claims_Sample_(\d+)A\.csv',
            'carrier_b': r'DE1_0_2008_to_2010_Carrier_Claims_Sample_(\d+)B\.csv',
            'inpatient': r'DE1_0_2008_to_2010_Inpatient_Claims_Sample_(\d+)\.csv',
            'outpatient': r'DE1_0_2008_to_2010_Outpatient_Claims_Sample_(\d+)\.csv',
            'prescription': r'DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_(\d+)\.csv'
        }
        
        # Columns that should always be string type (IDs, codes, diagnoses)
        self.string_columns = {
            'desynpuf_id', 'bene_id', 'clm_id', 'clm_line_num', 'prf_physn_npi',
            'prf_physn_upin', 'carr_clm_pmt_dnl_cd', 'carr_clm_hcpcs_cd',
            'carr_clm_hcpcs_1_mdfr_cd', 'carr_clm_hcpcs_2_mdfr_cd', 
            'prv_inst_oscar_num', 'clm_fac_type_cd', 'clm_srv_clsfctn_type_cd',
            'clm_freq_cd', 'icd_dgns_cd1', 'icd_dgns_cd2', 'icd_dgns_cd3',
            'icd_dgns_cd4', 'icd_dgns_cd5', 'icd_dgns_cd6', 'icd_dgns_cd7',
            'icd_dgns_cd8', 'icd_dgns_cd9', 'icd_dgns_cd10', 'icd_prcdr_cd1',
            'icd_prcdr_cd2', 'icd_prcdr_cd3', 'icd_prcdr_cd4', 'icd_prcdr_cd5',
            'icd_prcdr_cd6', 'hcpcs_cd', 'rev_cntr_ide_ndc_upc_num', 'prdsrv_id',
            'plan_cntrct_rec_id', 'pbp_id', 'ptnt_rsdnc_cd', 'gnn_cd', 'daw_prod_cd',
            'carr_num', 'clm_carr_pmt_dnl_cd', 'carr_clm_entry_cd', 'line_nch_pmt_cd',
            'line_bene_pmt_cd', 'line_prvdr_pmt_cd', 'line_bene_ptb_ddctbl_cd',
            'line_bene_prmry_pyr_cd', 'line_coinsrnc_cd', 'line_alowd_chrg_cd',
            'line_prcsg_ind_cd', 'line_pmt_80_100_cd', 'line_nch_alwbl_cd',
            'hcpcs_1st_mdfr_cd', 'hcpcs_2nd_mdfr_cd', 'betos_cd', 'prov_spclty',
            # Add more medical codes as needed
        }
        
        self.logger.info(f"Initialized SynPUF converter for {self.synpuf_dir}")
        
        # Print clean status to console
        print(f"📁 Output directory: {self.synpuf_dir}")
        print(f"📝 Log file: {self.log_file}")
    
    def _setup_logging(self, log_level: str):
        """Configure logging with both console and file output."""
        self.logger = logging.getLogger(__name__)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"synpuf_convert_{timestamp}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info(f"Logging to file: {log_file}")
        self.log_file = log_file
    
    def _get_csv_files(self) -> Dict[str, List[Tuple[Path, int]]]:
        """Get all CSV files grouped by type.
        
        Returns:
            Dictionary mapping file type to list of (filepath, sample_number) tuples
        """
        csv_files = {}
        
        # Initialize groups
        for file_type in self.file_patterns:
            csv_files[file_type] = []
        
        # Scan CSV directory
        for csv_file in self.csv_dir.glob("*.csv"):
            for file_type, pattern in self.file_patterns.items():
                match = re.match(pattern, csv_file.name)
                if match:
                    sample_num = int(match.group(1))
                    csv_files[file_type].append((csv_file, sample_num))
                    break
        
        # Sort by sample number
        for file_type in csv_files:
            csv_files[file_type].sort(key=lambda x: x[1])
        
        # Log summary to file
        for file_type, files in csv_files.items():
            self.logger.info(f"Found {len(files)} {file_type} files")
        
        # Print clean summary to console  
        total_files = sum(len(files) for files in csv_files.values())
        print(f"📊 Found {total_files} CSV files across {len([f for f in csv_files.values() if f])} file types")
        
        return csv_files
    
    def _infer_schema_with_string_columns(self, csv_file: Path, sample_size: int = 10000) -> pa.Schema:
        """Infer schema from CSV with string column enforcement.
        
        Args:
            csv_file: Path to CSV file
            sample_size: Number of rows to sample for schema inference
            
        Returns:
            PyArrow schema with proper types
        """
        # Configure CSV reading options for PyArrow 20.0.0
        convert_options = pv.ConvertOptions(
            strings_can_be_null=True,
            include_columns=None,
            include_missing_columns=True,
            auto_dict_encode=False  # Disable automatic dictionary encoding for flexibility
        )
        
        # First pass: get column names
        with open(csv_file, 'r', encoding='utf-8') as f:
            header_line = f.readline().strip()
            column_names = [col.strip().strip('"') for col in header_line.split(',')]
        
        # Read options optimized for large files
        read_options = pv.ReadOptions(
            block_size=2*1024*1024,  # 2MB blocks for schema inference
            skip_rows=0,
            column_names=column_names,
            autogenerate_column_names=False,
            encoding='utf8'
        )
        
        parse_options = pv.ParseOptions(
            delimiter=',',
            quote_char='"',
            escape_char='\\',
            newlines_in_values=False
        )
        
        # Read sample data for schema inference
        try:
            table_sample = pv.read_csv(
                csv_file,
                convert_options=convert_options,
                read_options=read_options,
                parse_options=parse_options
            )
        except Exception as e:
            self.logger.error(f"Error reading CSV sample from {csv_file}: {e}")
            raise
        
        # Build schema with proper types
        fields = []
        for i, column_name in enumerate(column_names):
            column_name_lower = column_name.lower()
            
            # Force string type for medical ID/code columns
            if any(string_col in column_name_lower for string_col in self.string_columns):
                field_type = pa.string()
                self.logger.debug(f"Column '{column_name}' forced to string type")
            else:
                # Use inferred type but ensure it's nullable and optimized
                if i < len(table_sample.schema):
                    inferred_type = table_sample.schema.field(i).type
                    
                    if pa.types.is_integer(inferred_type):
                        # Use int64 for all integers to avoid overflow issues
                        field_type = pa.int64()
                    elif pa.types.is_floating(inferred_type):
                        # Use float64 for all floating point numbers
                        field_type = pa.float64()
                    elif pa.types.is_boolean(inferred_type):
                        field_type = pa.bool_()
                    elif pa.types.is_date(inferred_type):
                        field_type = pa.date32()
                    elif pa.types.is_timestamp(inferred_type):
                        # Preserve timestamp precision
                        field_type = inferred_type
                    else:
                        # Default to string for safety
                        field_type = pa.string()
                else:
                    # Fallback to string if column not found in sample
                    field_type = pa.string()
            
            fields.append(pa.field(column_name, field_type, nullable=True))
        
        schema = pa.schema(fields)
        self.logger.debug(f"Inferred schema for {csv_file.name}: {len(fields)} columns")
        return schema
    
    def _read_csv_efficiently(self, csv_file: Path, schema: pa.Schema) -> pa.Table:
        """Read CSV file efficiently using PyArrow 20.0.0.
        
        Args:
            csv_file: Path to CSV file
            schema: PyArrow schema to use
            
        Returns:
            PyArrow table
        """
        convert_options = pv.ConvertOptions(
            column_types=schema,
            strings_can_be_null=True,
            include_missing_columns=True,
            auto_dict_encode=False,  # Disable automatic dictionary encoding
            null_values=['', 'NULL', 'null', 'NA', 'na', 'N/A'],  # Common null representations
            true_values=['true', 'True', 'TRUE', '1', 'yes', 'Yes', 'YES'],
            false_values=['false', 'False', 'FALSE', '0', 'no', 'No', 'NO']
        )
        
        read_options = pv.ReadOptions(
            block_size=64*1024*1024,  # 64MB blocks for better throughput on large files
            skip_rows=0,
            autogenerate_column_names=False,
            encoding='utf8'
        )
        
        parse_options = pv.ParseOptions(
            delimiter=',',
            quote_char='"',
            escape_char='\\',
            newlines_in_values=False,
            ignore_empty_lines=True
        )
        
        file_size_mb = csv_file.stat().st_size / 1024 / 1024
        # Log detailed info to file only
        self.logger.info(f"Reading {csv_file.name} ({file_size_mb:.1f} MB)")
        
        try:
            table = pv.read_csv(
                csv_file,
                convert_options=convert_options,
                read_options=read_options,
                parse_options=parse_options
            )
            
            # Log to file only
            self.logger.info(f"Loaded {len(table):,} rows, {len(table.columns)} columns")
            return table
            
        except Exception as e:
            self.logger.error(f"Error reading CSV {csv_file}: {e}")
            raise
    
    def _combine_carrier_claims(self, carrier_files: Dict[str, List[Tuple[Path, int]]]) -> pa.Table:
        """Combine carrier claims A and B files.
        
        Args:
            carrier_files: Dictionary with 'carrier_a' and 'carrier_b' file lists
            
        Returns:
            Combined PyArrow table with sample partition column
        """
        # Log to file
        self.logger.info("Combining carrier claims A and B files")
        
        # Clean console output
        print(f"\n🔄 Combining carrier claims A and B files...")
        
        combined_tables = []
        
        # Group A and B files by sample number
        a_files = {sample: path for path, sample in carrier_files['carrier_a']}
        b_files = {sample: path for path, sample in carrier_files['carrier_b']}
        
        all_samples = sorted(set(a_files.keys()) | set(b_files.keys()))
        
        # Infer schema from first available file (without sample column)
        first_file = None
        for sample in all_samples:
            if sample in a_files:
                first_file = a_files[sample]
                break
            elif sample in b_files:
                first_file = b_files[sample]
                break
        
        if not first_file:
            raise ValueError("No carrier claims files found")
        
        base_schema = self._infer_schema_with_string_columns(first_file)
        
        with tqdm(total=len(all_samples), desc="Processing carrier claims", 
                 leave=False, dynamic_ncols=True) as pbar:
            for sample in all_samples:
                sample_tables = []
                
                # Process A file if exists
                if sample in a_files:
                    table_a = self._read_csv_efficiently(a_files[sample], base_schema)
                    # Add sample column
                    table_a = table_a.append_column('sample', pa.array([sample] * len(table_a)))
                    sample_tables.append(table_a)
                
                # Process B file if exists
                if sample in b_files:
                    table_b = self._read_csv_efficiently(b_files[sample], base_schema)
                    # Add sample column
                    table_b = table_b.append_column('sample', pa.array([sample] * len(table_b)))
                    sample_tables.append(table_b)
                
                if sample_tables:
                    # Combine A and B for this sample
                    sample_combined = pa.concat_tables(sample_tables)
                    combined_tables.append(sample_combined)
                
                pbar.update(1)
        
        if not combined_tables:
            raise ValueError("No carrier claims data to combine")
        
        # Combine all samples
        final_table = pa.concat_tables(combined_tables)
        
        # Log to file
        self.logger.info(f"Combined carrier claims: {len(final_table)} total rows")
        
        # Clean console output
        print(f"✅ Combined carrier claims: {len(final_table):,} rows")
        
        return final_table
    
    def _convert_file_group(self, file_type: str, files: List[Tuple[Path, int]], 
                          output_name: str) -> bool:
        """Convert a group of CSV files to partitioned Parquet.
        
        Args:
            file_type: Type of files (e.g., 'beneficiary_2008')
            files: List of (filepath, sample_number) tuples
            output_name: Output parquet directory name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not files:
                self.logger.warning(f"No files found for {file_type}")
                return True
            
            # Log to file
            self.logger.info(f"Converting {file_type} files to {output_name}")
            
            # Clean console output
            print(f"\n🔄 Converting {len(files)} {file_type} files...")
            
            # Infer schema from first file (without sample column)
            first_file = files[0][0]
            base_schema = self._infer_schema_with_string_columns(first_file)
            
            # Process all files
            all_tables = []
            
            with tqdm(total=len(files), desc=f"Processing {file_type}", 
                     leave=False, dynamic_ncols=True) as pbar:
                for csv_file, sample_num in files:
                    # Read CSV with base schema
                    table = self._read_csv_efficiently(csv_file, base_schema)
                    
                    # Add sample partition column
                    table = table.append_column('sample', pa.array([sample_num] * len(table)))
                    
                    all_tables.append(table)
                    pbar.update(1)
            
            # Combine all tables
            combined_table = pa.concat_tables(all_tables)
            
            # Write partitioned parquet using PyArrow 20.0.0 API
            output_path = self.parquet_dir / output_name
            
            # Create parquet file format with options
            parquet_format = ds.ParquetFileFormat()
            file_options = parquet_format.make_write_options(
                compression='snappy',
                use_dictionary=True,
                write_statistics=True
            )
            
            ds.write_dataset(
                data=combined_table,
                base_dir=output_path,
                format=parquet_format,
                partitioning=['sample'],
                file_options=file_options,
                existing_data_behavior='overwrite_or_ignore',
                max_open_files=1000,
                max_rows_per_file=1000000  # 1M rows per file for manageable file sizes
            )
            
            # Log detailed info to file
            self.logger.info(f"Successfully wrote {output_name} with {len(combined_table)} rows")
            
            # Clean console output
            print(f"✅ Completed {file_type}: {len(combined_table):,} rows")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error converting {file_type}: {e}")
            print(f"❌ Failed {file_type}: {e}")
            return False
    
    def convert_all(self) -> bool:
        """Convert all CSV files to Parquet format.
        
        Returns:
            True if all conversions successful, False otherwise
        """
        if not self.csv_dir.exists():
            self.logger.error(f"CSV directory not found: {self.csv_dir}")
            return False
        
        # Get all CSV files
        csv_files = self._get_csv_files()
        
        all_successful = True
        
        # Convert individual file types
        conversions = [
            ('beneficiary_2008', 'DE1_0_2008_Beneficiary_Summary_File.parquet'),
            ('beneficiary_2009', 'DE1_0_2009_Beneficiary_Summary_File.parquet'),
            ('beneficiary_2010', 'DE1_0_2010_Beneficiary_Summary_File.parquet'),
            ('inpatient', 'DE1_0_2008_to_2010_Inpatient_Claims.parquet'),
            ('outpatient', 'DE1_0_2008_to_2010_Outpatient_Claims.parquet'),
            ('prescription', 'DE1_0_2008_to_2010_Prescription_Drug_Events.parquet'),
        ]
        
        for file_type, output_name in conversions:
            if file_type in csv_files:
                success = self._convert_file_group(file_type, csv_files[file_type], output_name)
                if not success:
                    all_successful = False
        
        # Handle carrier claims specially (combine A and B)
        if 'carrier_a' in csv_files or 'carrier_b' in csv_files:
            try:
                carrier_files = {
                    'carrier_a': csv_files.get('carrier_a', []),
                    'carrier_b': csv_files.get('carrier_b', [])
                }
                
                combined_table = self._combine_carrier_claims(carrier_files)
                
                # Write partitioned parquet using PyArrow 20.0.0 API
                output_path = self.parquet_dir / 'DE1_0_2008_to_2010_Carrier_Claims.parquet'
                
                # Create parquet file format with options
                parquet_format = ds.ParquetFileFormat()
                file_options = parquet_format.make_write_options(
                    compression='snappy',
                    use_dictionary=True,
                    write_statistics=True
                )
                
                ds.write_dataset(
                    data=combined_table,
                    base_dir=output_path,
                    format=parquet_format,
                    partitioning=['sample'],
                    file_options=file_options,
                    existing_data_behavior='overwrite_or_ignore',
                    max_open_files=1000,
                    max_rows_per_file=2000000  # 2M rows per file for carrier claims (larger files)
                )
                
                # Log to file
                self.logger.info(f"Successfully wrote carrier claims with {len(combined_table)} rows")
                
            except Exception as e:
                self.logger.error(f"Error combining carrier claims: {e}")
                print(f"❌ Failed carrier claims: {e}")
                all_successful = False
        
        return all_successful
    
    def generate_summary(self) -> str:
        """Generate a summary of the conversion results.
        
        Returns:
            Formatted summary string
        """
        if not self.parquet_dir.exists():
            return "\n📂 No parquet files found."
        
        summary_lines = [
            "\n" + "="*50,
            "📊 CONVERSION SUMMARY",
            "="*50
        ]
        
        parquet_dirs = list(self.parquet_dir.glob("*.parquet"))
        
        if not parquet_dirs:
            summary_lines.append("📂 No parquet datasets found.")
        else:
            for parquet_dir in sorted(parquet_dirs):
                try:
                    # Use modern PyArrow 20.0.0 dataset API
                    dataset = ds.dataset(parquet_dir, format='parquet')
                    num_files = len(dataset.files)
                    
                    # Try to get row count and basic statistics
                    try:
                        # Get metadata without reading full data for large datasets
                        schema = dataset.schema
                        col_count = len(schema)
                        
                        # Calculate total size on disk
                        size_mb = sum(f.stat().st_size for f in Path(parquet_dir).rglob("*.parquet")) / 1024 / 1024
                        
                        # For small datasets, get row count; for large ones, estimate
                        if size_mb < 100:  # Less than 100MB, safe to read
                            table = dataset.to_table()
                            row_count = len(table)
                        else:
                            # Estimate row count from first partition
                            try:
                                first_partition = dataset.to_table(limit=1000)
                                if len(first_partition) > 0:
                                    # Rough estimation based on file size
                                    avg_row_size = sum(f.stat().st_size for f in Path(parquet_dir).rglob("*.parquet")) / 1000
                                    estimated_rows = int(size_mb * 1024 * 1024 / max(avg_row_size, 1))
                                    row_count = f"~{estimated_rows:,} (estimated)"
                                else:
                                    row_count = "0"
                            except Exception:
                                row_count = "Unknown"
                        
                        summary_lines.extend([
                            f"📄 {parquet_dir.name}:",
                            f"   Partitions: {num_files}",
                            f"   Rows: {row_count if isinstance(row_count, str) else f'{row_count:,}'}",
                            f"   Columns: {col_count}",
                            f"   Size: {size_mb:.1f} MB",
                            ""
                        ])
                    except Exception as e:
                        summary_lines.extend([
                            f"📄 {parquet_dir.name}:",
                            f"   Partitions: {num_files}",
                            f"   ⚠️  Unable to read statistics: {e}",
                            ""
                        ])
                        
                except Exception as e:
                    summary_lines.extend([
                        f"📄 {parquet_dir.name}:",
                        f"   ❌ Error: {e}",
                        ""
                    ])
        
        summary_lines.extend([
            "="*50,
            f"📝 Log file: {self.log_file}",
            "="*50
        ])
        
        return "\n".join(summary_lines)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Convert SynPUF CSV files to partitioned Parquet format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Convert all CSV files using SYNPUF_DIR
  %(prog)s --input-dir /path/to/synpuf  # Override input directory
  %(prog)s --log-level DEBUG        # Enable debug logging
  
Output Structure:
  {SYNPUF_DIR}/parquets/
  ├── DE1_0_2008_Beneficiary_Summary_File.parquet/
  │   ├── sample=1/
  │   ├── sample=2/
  │   └── ...
  ├── DE1_0_2008_to_2010_Carrier_Claims.parquet/ (combined A+B)
  └── ...
        """
    )
    
    parser.add_argument(
        '--input-dir',
        help='SynPUF directory (overrides SYNPUF_DIR environment variable)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Determine input directory
    synpuf_dir = args.input_dir or os.getenv('SYNPUF_DIR')
    if not synpuf_dir:
        parser.error("Input directory must be specified via --input-dir or SYNPUF_DIR environment variable")
    
    # Initialize converter and start processing
    converter = SynPUFConverter(synpuf_dir, args.log_level)
    
    print(f"\n🚀 SynPUF CSV to Parquet Converter")
    print("-" * 50)
    
    success = converter.convert_all()
    
    # Generate and display summary
    print(converter.generate_summary())
    
    if success:
        print("\n✅ All conversions completed successfully!")
        return 0
    else:
        print("\n❌ Some conversions failed. Check the log file for details.")
        return 1


if __name__ == "__main__":
    exit(main())