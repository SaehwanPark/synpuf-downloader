Task: Using your best knowledge, you must implement CLI synpuf downloader that downloads zip files then unpack (to csv files). 

Requirements:
1. use environmental variable (you may use `dotenv` package to read from `.env`) `SYNPUF_DIR` for output directory
2. use logging
3. use `tqdm` to let users know the progress
4. See the below for original locations. Be aware the base url has **inconsistnetly different patterns**.
5. You need not create subdirectory per Sample number because filenames indicate which samples they are from.
6. Note that DE-SynPUF is provided across 20 samples (Samples 1 through 20)

---

Expected output directory structure:
Assume `SYNPUF_DIR='/home/saehwan/data/synpuf'`

`synpuf/`
: subdirectories `zip_files`, `csv_files`

`zip_files` will contain raw zip files
`csv_files` will contain unpacked csv files (from zips) -- using the original file constructions (e.g., carrier claims are separated into A and B)

---

## Sample 1 locations

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_1.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2009_beneficiary_summary_file_sample_1.zip
https://www.cms.gov/sites/default/files/2020-09/DE1_0_2010_Beneficiary_Summary_File_Sample_1.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_1A.zip
http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_1B.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_1.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_outpatient_claims_sample_1.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_1.zip

---

## Sample 2

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_2.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2009_beneficiary_summary_file_sample_2.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2010_beneficiary_summary_file_sample_2.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_2A.zip
http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_2B.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_2.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_outpatient_claims_sample_2.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_2.zip

---

## Sample 3

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_3.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2009_beneficiary_summary_file_sample_3.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2010_beneficiary_summary_file_sample_3.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_3A.zip
http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_3B.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_3.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_outpatient_claims_sample_3.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_3.zip

---

## Sample 10

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_10.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2009_beneficiary_summary_file_sample_10.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2010_beneficiary_summary_file_sample_10.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_10A.zip
http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_10B.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_10.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_outpatient_claims_sample_10.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_10.zip

---

## Sample 15

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_15.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2009_beneficiary_summary_file_sample_15.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2010_beneficiary_summary_file_sample_15.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_15A.zip
http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_15B.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_15.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_outpatient_claims_sample_15.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_15.zip

---

## Sample 18

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_18.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2009_beneficiary_summary_file_sample_18.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2010_beneficiary_summary_file_sample_18.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_18A.zip
http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_18B.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_18.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_outpatient_claims_sample_18.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_18.zip

---

## Sample 19

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_19.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2009_beneficiary_summary_file_sample_19.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2010_beneficiary_summary_file_sample_19.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_19A.zip
http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_19B.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_19.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_outpatient_claims_sample_19.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_19.zip

---

## Sample 20

https://www.cms.gov/research-statistics-data-and-systems/statistics-trends-and-reports/synpufs/downloads/de1_0_2008_beneficiary_summary_file_sample_20.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2009_beneficiary_summary_file_sample_20.zip
https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2010_beneficiary_summary_file_sample_20.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_20A.zip
http://downloads.cms.gov/files/DE1_0_2008_to_2010_Carrier_Claims_Sample_20B.zip

https://www.cms.gov/research-statistics-data-and-systems/statistics-trends-and-reports/synpufs/downloads/de1_0_2008_to_2010_inpatient_claims_sample_20.zip

https://www.cms.gov/research-statistics-data-and-systems/downloadable-public-use-files/synpufs/downloads/de1_0_2008_to_2010_outpatient_claims_sample_20.zip

http://downloads.cms.gov/files/DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_20.zip

