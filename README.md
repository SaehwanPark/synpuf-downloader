# SynPUF CLI Downloader

A command-line tool for downloading and extracting CMS SynPUF (Synthetic Public Use Files) data. This tool handles all 20 samples of the DE-SynPUF dataset with progress tracking, proper error handling, and automatic file extraction.

## Features

- **Complete Coverage**: Downloads all file types from all 20 SynPUF samples
- **Progress Tracking**: Visual progress bars using `tqdm` for downloads and extractions
- **Smart URL Handling**: Automatically handles the three different CMS URL patterns
- **Error Recovery**: Robust error handling with retry logic
- **Skip Existing Files**: Option to skip already downloaded files
- **Organized Output**: Separates ZIP files and extracted CSV files into organized directories
- **Environment Configuration**: Uses `.env` files for configuration management
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Installation

1. **Clone or download the script files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env to set your SYNPUF_DIR path
   ```

## Usage

### Basic Commands

Download specific samples:
```bash
python synpuf_downloader.py --samples 1 2 3
```

Download all 20 samples:
```bash
python synpuf_downloader.py --all
```

Force re-download existing files:
```bash
python synpuf_downloader.py --samples 5 --force
```

Validate URLs without downloading:
```bash
python synpuf_downloader.py --samples 1 20 --validate
```

Override output directory:
```bash
python synpuf_downloader.py --samples 1 --output-dir /custom/path
```

### Command Line Options

- `--samples N [N ...]`: Specify sample numbers to download (1-20)
- `--all`: Download all 20 samples
- `--validate`: Validate URLs without downloading (useful for testing)
- `--force`: Re-download files even if they already exist
- `--output-dir PATH`: Override the SYNPUF_DIR environment variable
- `--log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### Environment Variables

Set these in your `.env` file:

- `SYNPUF_DIR`: Base directory for downloads (required)

## Data Structure

The tool creates the following directory structure:

```
${SYNPUF_DIR}/
├── zip_files/          # Original ZIP files from CMS
│   ├── de1_0_2008_beneficiary_summary_file_sample_1.zip
│   ├── DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.zip
│   └── ...
├── csv_files/          # Extracted CSV files
│   ├── DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv
│   ├── DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.csv
│   └── ...
└── logs/              # Persistent log files
    ├── synpuf_download_20250713_103015.log
    └── ...
```

## File Types Downloaded

For each sample (1-20), the tool downloads:

1. **Beneficiary Summary Files** (3 files):
   - 2008 Beneficiary Summary
   - 2009 Beneficiary Summary  
   - 2010 Beneficiary Summary

2. **Claims Files** (4 files):
   - Carrier Claims Part A
   - Carrier Claims Part B
   - Inpatient Claims
   - Outpatient Claims

3. **Prescription Drug Events** (1 file):
   - 2008-2010 Prescription Drug Events

**Total: 8 files per sample × 20 samples = 160 files**

## Validation Mode

Before downloading large datasets, you can validate URL accessibility:

```bash
# Validate specific samples
python synpuf_downloader.py --samples 1 20 --validate

# Validate all samples (recommended before full download)
python synpuf_downloader.py --all --validate
```

**Validation Output Example**:
```
✅ de1_0_2008_beneficiary_summary_file_sample_1.zip - Available (size: 2157824 bytes)
✅ de1_0_2009_beneficiary_summary_file_sample_1.zip - Available (size: 2089472 bytes)
❌ de1_0_2010_beneficiary_summary_file_sample_1.zip - Status 404

Sample 1 URL validation: 7/8 files available
```

This helps identify broken URLs or server issues before starting lengthy downloads.

The tool automatically handles CMS's inconsistent URL patterns based on empirical analysis:

### Standard Pattern (Samples 2-19)
- **Beneficiary & Claims**: `https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/`

### Special Cases
- **Sample 1**: 2010 Beneficiary file uses `https://www.cms.gov/sites/default/files/2020-09/`
- **Sample 20**: 
  - 2008 Beneficiary uses `https://www.cms.gov/research-statistics-data-and-systems/statistics-trends-and-reports/synpufs/downloads/`
  - Inpatient Claims uses `https://www.cms.gov/research-statistics-data-and-systems/statistics-trends-and-reports/synpufs/downloads/`

### Consistent Across All Samples
- **Carrier Claims & Prescription Events**: `http://downloads.cms.gov/files/`

## Example Output

```
SynPUF Downloader
Output directory: /home/saehwan/data/synpuf
Log file: /home/saehwan/data/synpuf/logs/synpuf_download_20250713_103015.log
Samples to process: [1, 2]
Skip existing files: True
--------------------------------------------------
2025-07-13 10:30:15 - __main__ - INFO - Processing Sample 1
de1_0_2008_beneficiary_summary_file_sample_1.zip: 100%|██████████| 2.1M/2.1M [00:03<00:00, 621kB/s]
Extracting de1_0_2008_beneficiary_summary_file_sample_1.zip: 100%|██████████| 1/1 [00:00<00:00, 45.2file/s]
...

==================================================
DOWNLOAD SUMMARY
==================================================
Total files expected:      16
Files skipped (existing):  2
Files attempted:           14
Successful downloads:      13
Failed downloads:          1
Successful extractions:    13
Failed extractions:        0

Download success rate:     92.9%
Extraction success rate:   92.9%
==================================================

============================================================
DETAILED FAILURE REPORT
============================================================
Total failures: 1

DOWNLOAD FAILURES (1):
------------------------------
  Sample 2: DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_2.zip
    Error: HTTPError: 404 Client Error: Not Found for url: ...

============================================================
Log file location: /home/saehwan/data/synpuf/logs/synpuf_download_20250713_103015.log
============================================================

❌ Some samples failed to process. Check the detailed report above and log file for more information.
```

## Error Handling

The tool includes comprehensive error handling:

- **Network Issues**: Automatic retry with exponential backoff
- **Corrupted Downloads**: Verification and cleanup of partial downloads
- **Invalid ZIP Files**: Detection and reporting of corrupted archives
- **Missing Files**: Graceful handling of unavailable URLs
- **Permission Issues**: Clear error messages for filesystem problems

## Logging

The tool provides comprehensive logging with both console and persistent file output:

### Log Files
- **Location**: `${SYNPUF_DIR}/logs/`
- **Format**: `synpuf_download_YYYYMMDD_HHMMSS.log`
- **Content**: Complete operation history, errors, and debugging information

### Log Levels
- **INFO**: Normal operation progress, file completions
- **WARNING**: Recoverable issues (e.g., retrying downloads)  
- **ERROR**: Failed operations with detailed error messages
- **DEBUG**: Detailed execution information for troubleshooting

### Failure Reporting

The tool generates detailed failure reports at the end of execution:

- **Summary Statistics**: Overview of success/failure rates
- **Detailed Failure List**: Specific errors for each failed file
- **Grouped by Operation**: Separate sections for download vs extraction failures
- **Grouped by Sample**: Easy identification of problematic samples
- **Log File Reference**: Direct path to complete log file

This makes it easy to identify and troubleshoot specific issues, whether they're network-related download problems or file corruption issues during extraction.

## Contributing

When contributing to this project:

1. Follow the existing code style (snake_case for variables/functions)
2. Add comprehensive error handling
3. Include progress indicators for long-running operations
4. Update documentation for any new features
5. Test with multiple sample numbers

## Notes

- **Large Downloads**: The complete dataset is approximately 2-3 GB
- **Network Requirements**: Stable internet connection recommended
- **Disk Space**: Ensure sufficient space (5+ GB recommended including extracted files)
- **CMS Availability**: Downloads depend on CMS server availability

## License

This tool is provided as-is for research and educational purposes. The SynPUF data itself is provided by CMS under their usage terms.