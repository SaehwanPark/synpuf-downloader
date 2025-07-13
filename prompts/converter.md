Now you need to implement a converter (from csv files to parquets)
Read csv files from {SYNPUF_DIR}/csv_files
Save parquets to {SYNPUF_DIR}/parquets
Parquet name should be the same as csv file name except for sample suffix. For example, `DE1_0_2008_Beneficiary_Summary_File_*.csv` => `DE1_0_2008_Beneficiary_Summary_File.parquet` (this may be directory)

Requirements
1. Use PyArrow backend to natually handle nullable integers
2. Use PyArrow to save partitioned parquets (use the sample number as partition key)
3. For carrier claims, `A` and `B` files have the same column structure -- they are just separated. You must combine them as well.
4. Note that files may be very large. Use the best strategy, method, and practice.
5. Integer columns may be nullable.

Refer to the the attached csv file list.