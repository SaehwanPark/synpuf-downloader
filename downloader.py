#!/usr/bin/env python3
"""
CLI SynPUF Downloader

Downloads and unpacks CMS SynPUF (Synthetic Public Use Files) data.
Supports all 20 samples with progress tracking and proper error handling.
"""

import argparse
import logging
from datetime import datetime
import os
import zipfile
from pathlib import Path
from typing import List, Tuple, Dict, NamedTuple
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()


class FailureRecord(NamedTuple):
    """Record of a failed operation."""
    sample_num: int
    filename: str
    operation: str  # 'download' or 'extract'
    error: str


class SynPUFDownloader:
    """Downloads and extracts CMS SynPUF data files."""
    
    def __init__(self, output_dir: str, log_level: str = 'INFO'):
        """Initialize the downloader.
        
        Args:
            output_dir: Base directory for downloads
            log_level: Logging level
        """
        self.output_dir = Path(output_dir)
        self.zip_dir = self.output_dir / "zip_files"
        self.csv_dir = self.output_dir / "csv_files"
        self.log_dir = self.output_dir / "logs"
        
        # Create directories
        self.zip_dir.mkdir(parents=True, exist_ok=True)
        self.csv_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Track failures for detailed reporting
        self.failures: List[FailureRecord] = []
        self.download_stats = {
            'total_files': 0,
            'successful_downloads': 0,
            'successful_extractions': 0,
            'failed_downloads': 0,
            'failed_extractions': 0,
            'skipped_files': 0
        }
        
        # Setup logging
        self._setup_logging(log_level)
        
        self.logger.info(f"Initialized SynPUF downloader with output dir: {self.output_dir}")
    
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
        
        # File handler - create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"synpuf_download_{timestamp}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        self.logger.info(f"Logging to file: {log_file}")
        self.log_file = log_file
    
    def _get_file_urls(self, sample_num: int) -> List[Tuple[str, str]]:
        """Generate URLs for a specific sample.
        
        Args:
            sample_num: Sample number (1-20)
            
        Returns:
            List of (url, filename) tuples
        """
        urls = []
        
        # Base URL patterns based on analysis of actual URLs
        base_cms = "https://www.cms.gov/"
        
        # Standard patterns that work for most samples
        standard_beneficiary_path = "research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/"
        carrier_prescription_base = "http://downloads.cms.gov/files/"
        
        # Special case URL patterns
        special_patterns = {
            1: {
                'beneficiary_2010': "sites/default/files/2020-09/"
            },
            20: {
                'beneficiary_2008': "research-statistics-data-and-systems/statistics-trends-and-reports/synpufs/downloads/",
                'inpatient': "research-statistics-data-and-systems/statistics-trends-and-reports/synpufs/downloads/"
            }
        }
        
        # Special filename patterns (CMS inconsistencies)
        special_filenames = {
            11: {
                'carrier_a': "DE1_0_2008_to_2010_Carrier_Claims_Sample_11A.csv.zip"
            }
        }
        
        # Generate beneficiary summary file URLs
        for year in [2008, 2009, 2010]:
            # Check for special patterns first
            special_key = f'beneficiary_{year}'
            if sample_num in special_patterns and special_key in special_patterns[sample_num]:
                path = special_patterns[sample_num][special_key]
            else:
                path = standard_beneficiary_path
            
            # Filename patterns differ for sample 1, year 2010
            if sample_num == 1 and year == 2010:
                filename = f"DE1_0_{year}_Beneficiary_Summary_File_Sample_{sample_num}.zip"
            else:
                filename = f"de1_0_{year}_beneficiary_summary_file_sample_{sample_num}.zip"
            
            url = base_cms + path + filename
            urls.append((url, filename))
        
        # Carrier Claims (A and B parts) - consistent across all samples
        for part in ['A', 'B']:
            # Check for special filename patterns
            special_key = f'carrier_{part.lower()}'
            if sample_num in special_filenames and special_key in special_filenames[sample_num]:
                filename = special_filenames[sample_num][special_key]
            else:
                filename = f"DE1_0_2008_to_2010_Carrier_Claims_Sample_{sample_num}{part}.zip"
            
            url = carrier_prescription_base + filename
            urls.append((url, filename))
        
        # Inpatient Claims - check for special pattern (sample 20)
        if sample_num == 20:
            inpatient_path = special_patterns[20]['inpatient']
        else:
            inpatient_path = standard_beneficiary_path
            
        filename = f"de1_0_2008_to_2010_inpatient_claims_sample_{sample_num}.zip"
        url = base_cms + inpatient_path + filename
        urls.append((url, filename))
        
        # Outpatient Claims - uses standard pattern for all samples
        filename = f"de1_0_2008_to_2010_outpatient_claims_sample_{sample_num}.zip"
        url = base_cms + standard_beneficiary_path + filename
        urls.append((url, filename))
        
        # Prescription Drug Events - consistent across all samples
        filename = f"DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_{sample_num}.zip"
        url = carrier_prescription_base + filename
        urls.append((url, filename))
        
        self.logger.debug(f"Generated {len(urls)} URLs for sample {sample_num}")
        if sample_num in special_filenames:
            self.logger.debug(f"Applied special filename patterns for sample {sample_num}: {special_filenames[sample_num]}")
        return urls
    
    def validate_urls(self, sample_num: int) -> Dict[str, bool]:
        """Validate URLs for a specific sample without downloading.
        
        Args:
            sample_num: Sample number to validate
            
        Returns:
            Dictionary mapping filename to availability status
        """
        self.logger.info(f"Validating URLs for sample {sample_num}")
        
        urls = self._get_file_urls(sample_num)
        results = {}
        
        for url, filename in urls:
            try:
                response = requests.head(url, allow_redirects=True, timeout=10)
                is_available = response.status_code == 200
                results[filename] = is_available
                
                if is_available:
                    size = response.headers.get('content-length', 'unknown')
                    self.logger.info(f"✅ {filename} - Available (size: {size} bytes)")
                else:
                    self.logger.warning(f"❌ {filename} - Status {response.status_code}")
                    
            except Exception as e:
                results[filename] = False
                self.logger.error(f"❌ {filename} - Error: {e}")
        
        available_count = sum(results.values())
        total_count = len(results)
        self.logger.info(f"Sample {sample_num} URL validation: {available_count}/{total_count} files available")
        
        return results
    
    def _download_file(self, url: str, filepath: Path, sample_num: int) -> bool:
        """Download a single file with progress bar.
        
        Args:
            url: URL to download
            filepath: Local filepath to save to
            sample_num: Sample number for failure tracking
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Downloading {url}")
            
            response = requests.get(url, stream=True, allow_redirects=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as file, tqdm(
                desc=filepath.name,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                miniters=1
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        size = file.write(chunk)
                        progress_bar.update(size)
            
            self.logger.info(f"Successfully downloaded {filepath.name}")
            self.download_stats['successful_downloads'] += 1
            return True
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to download {url}: {e}"
            self.logger.error(error_msg)
            self.failures.append(FailureRecord(sample_num, filepath.name, 'download', str(e)))
            self.download_stats['failed_downloads'] += 1
            # Clean up partial download
            if filepath.exists():
                filepath.unlink()
            return False
        except Exception as e:
            error_msg = f"Unexpected error downloading {url}: {e}"
            self.logger.error(error_msg)
            self.failures.append(FailureRecord(sample_num, filepath.name, 'download', str(e)))
            self.download_stats['failed_downloads'] += 1
            if filepath.exists():
                filepath.unlink()
            return False
    
    def _extract_zip(self, zip_path: Path, sample_num: int) -> bool:
        """Extract a zip file to the CSV directory.
        
        Args:
            zip_path: Path to zip file
            sample_num: Sample number for failure tracking
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Extracting {zip_path.name}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of files to extract
                file_list = zip_ref.namelist()
                
                # Extract with progress bar
                with tqdm(total=len(file_list), desc=f"Extracting {zip_path.name}") as progress_bar:
                    for file_name in file_list:
                        zip_ref.extract(file_name, self.csv_dir)
                        progress_bar.update(1)
            
            self.logger.info(f"Successfully extracted {zip_path.name}")
            self.download_stats['successful_extractions'] += 1
            return True
            
        except zipfile.BadZipFile as e:
            error_msg = f"Invalid zip file: {zip_path}"
            self.logger.error(error_msg)
            self.failures.append(FailureRecord(sample_num, zip_path.name, 'extract', 'Invalid zip file'))
            self.download_stats['failed_extractions'] += 1
            return False
        except Exception as e:
            error_msg = f"Error extracting {zip_path}: {e}"
            self.logger.error(error_msg)
            self.failures.append(FailureRecord(sample_num, zip_path.name, 'extract', str(e)))
            self.download_stats['failed_extractions'] += 1
            return False
    
    def download_sample(self, sample_num: int, skip_existing: bool = True) -> bool:
        """Download and extract all files for a specific sample.
        
        Args:
            sample_num: Sample number (1-20)
            skip_existing: Skip files that already exist
            
        Returns:
            True if all files processed successfully, False otherwise
        """
        self.logger.info(f"Processing Sample {sample_num}")
        
        urls = self._get_file_urls(sample_num)
        self.download_stats['total_files'] += len(urls)
        success_count = 0
        
        for url, filename in urls:
            zip_path = self.zip_dir / filename
            
            # Skip if file already exists and skip_existing is True
            if skip_existing and zip_path.exists():
                self.logger.info(f"Skipping existing file: {filename}")
                self.download_stats['skipped_files'] += 1
                success_count += 1
                continue
            
            # Download the file
            if self._download_file(url, zip_path, sample_num):
                # Extract the file
                if self._extract_zip(zip_path, sample_num):
                    success_count += 1
                else:
                    self.logger.error(f"Failed to extract {filename}")
            else:
                self.logger.error(f"Failed to download {filename}")
        
        success_rate = success_count / len(urls)
        self.logger.info(f"Sample {sample_num} completed: {success_count}/{len(urls)} files processed successfully ({success_rate:.1%})")
        
        return success_count == len(urls)
    
    def download_samples(self, sample_numbers: List[int], skip_existing: bool = True) -> bool:
        """Download and extract files for multiple samples.
        
        Args:
            sample_numbers: List of sample numbers to process
            skip_existing: Skip files that already exist
            
        Returns:
            True if all samples processed successfully, False otherwise
        """
        all_successful = True
        
        for sample_num in sample_numbers:
            if not (1 <= sample_num <= 20):
                self.logger.error(f"Invalid sample number: {sample_num}. Must be between 1-20.")
                all_successful = False
                continue
            
            success = self.download_sample(sample_num, skip_existing)
            if not success:
                all_successful = False
        
        return all_successful
    
    def generate_failure_report(self) -> str:
        """Generate a detailed failure report.
        
        Returns:
            Formatted failure report string
        """
        if not self.failures:
            return "✅ No failures occurred!"
        
        report_lines = [
            "\n" + "="*60,
            "DETAILED FAILURE REPORT",
            "="*60,
            f"Total failures: {len(self.failures)}",
            ""
        ]
        
        # Group failures by type
        download_failures = [f for f in self.failures if f.operation == 'download']
        extract_failures = [f for f in self.failures if f.operation == 'extract']
        
        if download_failures:
            report_lines.extend([
                f"DOWNLOAD FAILURES ({len(download_failures)}):",
                "-" * 30
            ])
            for failure in download_failures:
                report_lines.append(f"  Sample {failure.sample_num}: {failure.filename}")
                report_lines.append(f"    Error: {failure.error}")
                report_lines.append("")
        
        if extract_failures:
            report_lines.extend([
                f"EXTRACTION FAILURES ({len(extract_failures)}):",
                "-" * 30
            ])
            for failure in extract_failures:
                report_lines.append(f"  Sample {failure.sample_num}: {failure.filename}")
                report_lines.append(f"    Error: {failure.error}")
                report_lines.append("")
        
        # Group by sample number for easier troubleshooting
        sample_failures = {}
        for failure in self.failures:
            if failure.sample_num not in sample_failures:
                sample_failures[failure.sample_num] = []
            sample_failures[failure.sample_num].append(failure)
        
        if len(sample_failures) > 1:
            report_lines.extend([
                "FAILURES BY SAMPLE:",
                "-" * 20
            ])
            for sample_num in sorted(sample_failures.keys()):
                failures = sample_failures[sample_num]
                report_lines.append(f"  Sample {sample_num} ({len(failures)} failures):")
                for failure in failures:
                    report_lines.append(f"    - {failure.operation.title()}: {failure.filename}")
                report_lines.append("")
        
        report_lines.extend([
            "="*60,
            f"Log file location: {self.log_file}",
            "="*60
        ])
        
        return "\n".join(report_lines)
    
    def generate_summary_report(self) -> str:
        """Generate a summary statistics report.
        
        Returns:
            Formatted summary report string
        """
        stats = self.download_stats
        total_attempted = stats['total_files'] - stats['skipped_files']
        
        report_lines = [
            "\n" + "="*50,
            "DOWNLOAD SUMMARY",
            "="*50,
            f"Total files expected:      {stats['total_files']}",
            f"Files skipped (existing):  {stats['skipped_files']}",
            f"Files attempted:           {total_attempted}",
            f"Successful downloads:      {stats['successful_downloads']}",
            f"Failed downloads:          {stats['failed_downloads']}",
            f"Successful extractions:    {stats['successful_extractions']}",
            f"Failed extractions:        {stats['failed_extractions']}",
            ""
        ]
        
        if total_attempted > 0:
            download_rate = (stats['successful_downloads'] / total_attempted) * 100
            extract_rate = (stats['successful_extractions'] / total_attempted) * 100
            report_lines.extend([
                f"Download success rate:     {download_rate:.1f}%",
                f"Extraction success rate:   {extract_rate:.1f}%"
            ])
        
        report_lines.append("="*50)
        return "\n".join(report_lines)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Download and extract CMS SynPUF data files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --samples 1 2 3          # Download samples 1, 2, and 3
  %(prog)s --all                    # Download all 20 samples
  %(prog)s --samples 5 --force      # Re-download sample 5 even if it exists
  
Environment Variables:
  SYNPUF_DIR    Output directory for downloaded files (required)
        """
    )
    
    parser.add_argument(
        '--samples',
        type=int,
        nargs='+',
        metavar='N',
        help='Sample numbers to download (1-20)'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Download all 20 samples'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate URLs without downloading (useful for testing)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-download files even if they already exist'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory (overrides SYNPUF_DIR environment variable)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    logging.basicConfig(level=getattr(logging, args.log_level))
    
    # Determine output directory
    output_dir = args.output_dir or os.getenv('SYNPUF_DIR')
    if not output_dir:
        parser.error("Output directory must be specified via --output-dir or SYNPUF_DIR environment variable")
    
    # Determine which samples to download
    if args.all:
        sample_numbers = list(range(1, 21))
    elif args.samples:
        sample_numbers = args.samples
    else:
        parser.error("Must specify either --samples or --all")
    
    # Validate sample numbers
    invalid_samples = [s for s in sample_numbers if not (1 <= s <= 20)]
    if invalid_samples:
        parser.error(f"Invalid sample numbers: {invalid_samples}. Must be between 1-20.")
    
    # Initialize downloader and start processing
    downloader = SynPUFDownloader(output_dir, args.log_level)
    
    print(f"SynPUF Downloader")
    print(f"Output directory: {output_dir}")
    print(f"Log file: {downloader.log_file}")
    print(f"Samples to process: {sample_numbers}")
    
    if args.validate:
        print("Mode: URL Validation")
        print("-" * 50)
        
        all_valid = True
        for sample_num in sample_numbers:
            results = downloader.validate_urls(sample_num)
            if not all(results.values()):
                all_valid = False
        
        if all_valid:
            print("\n✅ All URLs are valid and accessible!")
            return 0
        else:
            print("\n❌ Some URLs are not accessible. Check logs for details.")
            return 1
    else:
        print(f"Skip existing files: {not args.force}")
        print("-" * 50)
        
        success = downloader.download_samples(
            sample_numbers, 
            skip_existing=not args.force
        )
        
        # Generate and display summary report
        print(downloader.generate_summary_report())
        
        if success:
            print("\n✅ All samples processed successfully!")
            return 0
        else:
            # Display detailed failure report
            print(downloader.generate_failure_report())
            print("\n❌ Some samples failed to process. Check the detailed report above and log file for more information.")
            return 1


if __name__ == "__main__":
    exit(main())