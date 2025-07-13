# SynPUF Tools

A comprehensive toolkit for downloading and processing CMS SynPUF (Synthetic Public Use Files) data. This includes a downloader for acquiring the raw data and a converter for transforming CSV files to efficient Parquet format.

## Tools Included

1. **`downloader.py`** - Downloads and extracts all 20 SynPUF samples
2. **`converter.py`** - Converts CSV files to partitioned Parquet format

## Features

### Downloader
- **Complete Coverage**: Downloads all file types from all 20 SynPUF samples
- **Progress Tracking**: Visual progress bars using `tqdm` 
- **Smart URL Handling**: Handles CMS's inconsistent URL patterns
- **Error Recovery**: Robust error handling with detailed failure reporting
- **Persistent Logging**: Complete operation logs for debugging

### Converter  
- **Efficient Processing**: Uses PyArrow 20.0.0 for optimal performance with large files
- **Modern API**: Uses the latest Dataset API (no legacy dataset dependencies)
- **Partitioned Output**: Creates sample-partitioned Parquet datasets
- **Data Combining**: Merges Carrier Claims A/B files automatically
- **Type Safety**: Proper handling of nullable integers and string IDs/codes
- **Memory Efficient**: Streams large files (64MB chunks) without loading everything into memory
- **Smart Schema Detection**: Automatically preserves medical codes and IDs as strings

## Requirements

- **Python**: 3.13+
- **PyArrow**: 20.0.0+  
- **Pandas**: 2.3.0+
- **uv**: For package management (recommended)

## Installation

**Using uv (recommended)**:
```bash
uv sync
```

**Using pip**:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file from the template:
```bash
cp .env.example .env
# Edit .env to set your SYNPUF_DIR path
```

## Usage

### Download SynPUF Data

Download specific samples:
```bash
python downloader.py --samples 1 2 3
```

Download all 20 samples:
```bash
python downloader.py --all
```

Validate URLs without downloading:
```bash
python downloader.py --samples 1 20 --validate
```

### Convert to Parquet

Convert all CSV files to Parquet:
```bash
python converter.py
```

With custom directory:
```bash
python converter.py --input-dir /path/to/synpuf
```

### Complete Workflow

```bash
# 1. Download all samples
python downloader.py --all

# 2. Convert to Parquet format
python converter.py

# 3. Verify results
ls -la ${SYNPUF_DIR}/parquets/
```

### Downloader Options

- `--samples N [N ...]`: Specify sample numbers to download (1-20)
- `--all`: Download all 20 samples
- `--validate`: Validate URLs without downloading
- `--force`: Re-download files even if they already exist
- `--output-dir PATH`: Override the SYNPUF_DIR environment variable
- `--log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### Converter Options

- `--input-dir PATH`: SynPUF directory (overrides SYNPUF_DIR)
- `--log-level LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### Environment Variables

Set these in your `.env` file:

- `SYNPUF_DIR`: Base directory for all operations (required)

### Converter Features

#### Clean Console Output
- **Progress Bars**: Clean tqdm progress bars without logging interference
- **Status Updates**: Clear emoji-based status messages 
- **File Logging**: All detailed logs written to timestamped files only
- **Error Display**: Important errors shown on console with details in logs

#### Intelligent Type Handling
- **Nullable Integers**: Proper PyArrow nullable integer types
- **String Preservation**: ID fields, diagnosis codes, procedure codes kept as strings
- **Schema Inference**: Automatic schema detection with manual overrides

### Performance Optimizations
- **Chunked Reading**: 64MB blocks for optimal I/O performance
- **Partitioned Output**: Sample-based partitioning for fast querying
- **Compression**: Snappy compression with dictionary encoding
- **Statistics**: Parquet metadata for query optimization
- **File Size Management**: Configurable max rows per file (1M for beneficiary, 2M for claims)
- **Memory Management**: Configurable max open files (1000 default)

### Data Quality
- **Carrier Claims Combining**: Merges A/B files seamlessly
- **Missing Value Handling**: Proper null value representation
- **Type Safety**: Prevents data type conversion errors

## Example Output

### Downloader
```
SynPUF Downloader
Output directory: /home/saehwan/data/synpuf
Log file: /home/saehwan/data/synpuf/logs/synpuf_download_20250713_103015.log
Samples to process: [1, 2]
Skip existing files: True
--------------------------------------------------
DE1_0_2008_Beneficiary_Summary_File_Sample_1.zip: 100%|██████████| 2.1M/2.1M [00:03<00:00, 621kB/s]

==================================================
DOWNLOAD SUMMARY
==================================================
Total files expected:      16
Successful downloads:      16
Download success rate:     100.0%
==================================================
```

### Converter
```
🚀 SynPUF CSV to Parquet Converter
--------------------------------------------------
📁 Output directory: /home/saehwan/data/synpuf
📝 Log file: /home/saehwan/data/synpuf/logs/synpuf_convert_20250713_145020.log
📊 Found 160 CSV files across 8 file types

🔄 Converting 20 beneficiary_2008 files...
Processing beneficiary_2008: 100%|██████████| 20/20 [00:45<00:00, 2.25s/file]
✅ Completed beneficiary_2008: 2,326,856 rows

🔄 Combining carrier claims A and B files...
Processing carrier claims: 100%|██████████| 20/20 [05:23<00:00, 16.17s/sample]
✅ Combined carrier claims: 9,895,904 rows

==================================================
📊 CONVERSION SUMMARY
==================================================
📄 DE1_0_2008_Beneficiary_Summary_File.parquet:
   Partitions: 20
   Rows: 2,326,856
   Columns: 32
   Size: 45.2 MB

📄 DE1_0_2008_to_2010_Carrier_Claims.parquet:
   Partitions: 40
   Rows: 9,895,904
   Columns: 142
   Size: 1,247.3 MB
==================================================

✅ All conversions completed successfully!
```

## Data Structure

The tools create the following directory structure:

```
${SYNPUF_DIR}/
├── zip_files/          # Original ZIP files from CMS (downloader)
│   ├── de1_0_2008_beneficiary_summary_file_sample_1.zip
│   ├── DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.zip
│   └── ...
├── csv_files/          # Extracted CSV files (downloader)
│   ├── DE1_0_2008_Beneficiary_Summary_File_Sample_1.csv
│   ├── DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.csv
│   └── ...
├── parquets/           # Partitioned Parquet datasets (converter)
│   ├── DE1_0_2008_Beneficiary_Summary_File.parquet/
│   │   ├── sample=1/
│   │   ├── sample=2/
│   │   └── ...
│   ├── DE1_0_2008_to_2010_Carrier_Claims.parquet/ (A+B combined)
│   │   ├── sample=1/
│   │   └── ...
│   └── DE1_0_2008_to_2010_Prescription_Drug_Events.parquet/
└── logs/              # Operation logs
    ├── synpuf_download_20250713_103015.log
    └── synpuf_convert_20250713_145020.log
```

## File Types and Processing

### Downloaded Files (per sample)
1. **Beneficiary Summary Files** (3 files):
   - 2008, 2009, 2010 Beneficiary Summary
2. **Claims Files** (4 files):
   - Carrier Claims Part A & B (combined in Parquet)
   - Inpatient Claims
   - Outpatient Claims
3. **Prescription Drug Events** (1 file)

**Total: 8 files per sample × 20 samples = 160 files**

### Parquet Output Structure
- **Partitioned by Sample**: Each dataset partitioned by sample number (1-20)
- **Carrier Claims Combined**: A and B files merged into single dataset
- **Optimized Types**: Proper nullable integers, string IDs preserved
- **Compressed**: Snappy compression with dictionary encoding

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
- **Sample 11**: Carrier Claims A file has `.csv.zip` extension instead of `.zip`
- **Sample 20**: 
  - 2008 Beneficiary uses `https://www.cms.gov/research-statistics-data-and-systems/statistics-trends-and-reports/synpufs/downloads/`
  - Inpatient Claims uses `https://www.cms.gov/research-statistics-data-and-systems/statistics-trends-and-reports/synpufs/downloads/`

### Consistent Across All Samples
- **Carrier Claims & Prescription Events**: `http://downloads.cms.gov/files/`

## CMS Data Inconsistencies

The tool handles various CMS naming and URL inconsistencies discovered through empirical testing:

- **URL Path Variations**: Different base paths for the same file types across samples
- **Filename Casing**: Mix of uppercase/lowercase in filenames (e.g., `DE1_0` vs `de1_0`)
- **File Extensions**: Sample 11 Carrier A uses `.csv.zip` instead of `.zip`
- **Year-Specific Patterns**: Sample 1's 2010 files use different URL structure

These inconsistencies are automatically handled by the downloader, but may require updates if CMS changes their file organization.

**Adding New Special Cases**: If you discover additional CMS inconsistencies, they can be easily added to the `special_filenames` or `special_patterns` dictionaries in the code.

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