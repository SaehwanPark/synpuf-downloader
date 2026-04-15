# SynPUF Agent Codebook

This document is a compact, agent-friendly lookup for the CMS Linkable 2008-2010 Medicare DE-SynPUF release and for the Parquet output currently generated in this repository.

Use it when you need to:
- identify the right file family or sample
- check a field name, meaning, or storage type
- confirm join keys and year logic
- avoid common analysis mistakes with synthetic claims data

## Stable Facts

- DE-SynPUF contains 20 samples, numbered `1..20`.
- Each sample contains 8 CSV files:
  - 3 beneficiary summary files, one per year
  - 1 inpatient claims file
  - 1 outpatient claims file
  - 1 prescription drug events file
  - 2 carrier claims files, parts `A` and `B`
- `DESYNPUF_ID` is the universal beneficiary join key.
- For claims files, claim year is determined by `CLM_THRU_DT`.
- Carrier part `A` and `B` files are one logical dataset and should be concatenated before analysis.
- The Parquet output in this repo is partitioned by `sample`.
- The current Parquet column names preserve the converter's exact emitted spellings, including some CMS-style abbreviations.

## On-Disk Layout

Current output root:

```text
${SYNPUF_DIR}/
  zip_files/
  csv_files/
  parquets/
  logs/
```

Observed Parquet layout:

```text
${SYNPUF_DIR}/parquets/
  DE1_0_2008_Beneficiary_Summary_File.parquet/
    1/part-0.parquet
    ...
    20/part-0.parquet
  DE1_0_2008_to_2010_Carrier_Claims.parquet/
    1/part-0.parquet
    ...
    20/part-0.parquet
```

Notes:
- the dataset name is the top-level directory name
- the sample number is the partition directory name
- a sample may contain multiple `part-*.parquet` files when the dataset is large

## Canonical Dataset Map

| Family | Record unit | Files per sample | Current Parquet name | Join key | Year logic | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Beneficiary summary | Beneficiary | 3 | `DE1_0_20xx_Beneficiary_Summary_File.parquet` | `DESYNPUF_ID` | Snapshot year in filename | Annual beneficiary attributes and annual reimbursement totals |
| Inpatient claims | Claim | 1 | `DE1_0_2008_to_2010_Inpatient_Claims.parquet` | `DESYNPUF_ID` | `CLM_THRU_DT` year | 81 variables |
| Outpatient claims | Claim | 1 | `DE1_0_2008_to_2010_Outpatient_Claims.parquet` | `DESYNPUF_ID` | `CLM_THRU_DT` year | 76 variables |
| Carrier claims | Claim | 2 parts (`A`, `B`) | `DE1_0_2008_to_2010_Carrier_Claims.parquet` | `DESYNPUF_ID` | `CLM_THRU_DT` year | 142 variables after combining both parts |
| PDE | Claim/event | 1 | `DE1_0_2008_to_2010_Prescription_Drug_Events.parquet` | `DESYNPUF_ID` | `SRVC_DT` year if needed | 8 variables |

## Record Counts From The Manuals

| Family | 2008 | 2009 | 2010 |
| --- | --- | --- | --- |
| Beneficiary summary | 2,326,856 | 2,291,320 | 2,255,098 |
| Inpatient claims | 547,800 | 504,941 | 280,081 |
| Outpatient claims | 5,673,808 | 6,519,340 | 3,633,839 |
| Carrier claims | 34,276,324 | 37,304,993 | 23,282,135 |
| PDE | 39,927,827 | 43,379,293 | 27,778,849 |

## Type And Storage Rules

Current Parquet output generally follows these conventions:

| Semantic class | Stored type | Examples |
| --- | --- | --- |
| Beneficiary IDs and claim IDs | `string` | `DESYNPUF_ID`, `CLM_ID`, `PDE_ID` |
| Most dates | `int64` | `BENE_BIRTH_DT`, `CLM_FROM_DT`, `CLM_THRU_DT`, `SRVC_DT` |
| Month counts and small counters | `int64` | `BENE_HI_CVRAGE_TOT_MONS`, `SEGMENT`, `DAYS_SUPLY_NUM` |
| Monetary amounts | `double` | `MEDREIMB_IP`, `CLM_PMT_AMT`, `PTNT_PAY_AMT` |
| State, race, sex, and other coded labels | usually `string` when code-like, `int64` when synthetic numeric flags | `BENE_RACE_CD`, `BENE_ESRD_IND`, `SP_STATE_CODE`, `SP_ALZHDMTA` |

Important:
- many CMS code fields are stored as strings even when they look numeric
- dates are still YYYYMMDD integers; parse them only when needed
- monetary variables can be zero, missing, or negative in some claims contexts

## Beneficiary Summary Reference

One record per synthetic beneficiary snapshot year.

| Field | Meaning | Stored type | Notes |
| --- | --- | --- | --- |
| `DESYNPUF_ID` | Beneficiary code | `string` | Primary join key |
| `BENE_BIRTH_DT` | Date of birth | `int64` | YYYYMMDD |
| `BENE_DEATH_DT` | Date of death | `int64` | Nullable; YYYYMMDD |
| `BENE_SEX_IDENT_CD` | Sex | `string` | Code values such as `1`, `2` |
| `BENE_RACE_CD` | Race | `string` | Code values such as `1`, `2`, `3`, `5` |
| `BENE_ESRD_IND` | ESRD indicator | `string` | Code values such as `0`, `Y` |
| `SP_STATE_CODE` | State of residence | `int64` | SSA state code |
| `BENE_COUNTY_CD` | County of residence | `string` | SSA county code; pair with state |
| `BENE_HI_CVRAGE_TOT_MONS` | Part A coverage months | `int64` | 0-12 |
| `BENE_SMI_CVRAGE_TOT_MONS` | Part B coverage months | `int64` | 0-12 |
| `BENE_HMO_CVRAGE_TOT_MONS` | HMO coverage months | `int64` | 0-12 |
| `PLAN_CVRG_MOS_NUM` | Part D plan coverage months | `int64` | 0-12 |
| `SP_ALZHDMTA` | Alzheimer or related disorders | `int64` | Chronic condition flag |
| `SP_CHF` | Heart failure | `int64` | Chronic condition flag |
| `SP_CHRNKIDN` | Chronic kidney disease | `int64` | Chronic condition flag |
| `SP_CNCR` | Cancer | `int64` | Chronic condition flag |
| `SP_COPD` | Chronic obstructive pulmonary disease | `int64` | Chronic condition flag |
| `SP_DEPRESSN` | Depression | `int64` | Chronic condition flag |
| `SP_DIABETES` | Diabetes | `int64` | Chronic condition flag |
| `SP_ISCHMCHT` | Ischemic heart disease | `int64` | Chronic condition flag |
| `SP_OSTEOPRS` | Osteoporosis | `int64` | Chronic condition flag |
| `SP_RA_OA` | Rheumatoid arthritis or osteoarthritis | `int64` | Chronic condition flag |
| `SP_STRKETIA` | Stroke / transient ischemic attack | `int64` | Chronic condition flag |
| `MEDREIMB_IP` | Inpatient annual Medicare reimbursement | `double` | Derived annual amount |
| `BENRES_IP` | Inpatient annual beneficiary responsibility | `double` | Derived annual amount |
| `PPPYMT_IP` | Inpatient annual primary payer reimbursement | `double` | Derived annual amount |
| `MEDREIMB_OP` | Outpatient annual Medicare reimbursement | `double` | Derived annual amount |
| `BENRES_OP` | Outpatient annual beneficiary responsibility | `double` | Derived annual amount |
| `PPPYMT_OP` | Outpatient annual primary payer reimbursement | `double` | Derived annual amount |
| `MEDREIMB_CAR` | Carrier annual Medicare reimbursement | `double` | Derived annual amount |
| `BENRES_CAR` | Carrier annual beneficiary responsibility | `double` | Derived annual amount |
| `PPPYMT_CAR` | Carrier annual primary payer reimbursement | `double` | Derived annual amount |

## Inpatient Claims Reference

One record per inpatient claim.

Core fields:
- `DESYNPUF_ID`
- `CLM_ID`
- `SEGMENT`
- `CLM_FROM_DT`
- `CLM_THRU_DT`
- `PRVDR_NUM`
- `CLM_PMT_AMT`
- `NCH_PRMRY_PYR_CLM_PD_AMT`
- `AT_PHYSN_NPI`
- `OP_PHYSN_NPI`
- `OT_PHYSN_NPI`
- `CLM_ADMSN_DT`
- `ADMTNG_ICD9_DGNS_CD`
- `CLM_PASS_THRU_PER_DIEM_AMT`
- `NCH_BENE_IP_DDCTBL_AMT`
- `NCH_BENE_PTA_COINSRNC_LBLTY_AM`
- `NCH_BENE_BLOOD_DDCTBL_LBLTY_AM`
- `CLM_UTLZTN_DAY_CNT`
- `NCH_BENE_DSCHRG_DT`
- `CLM_DRG_CD`

Repeated blocks:
- `ICD9_DGNS_CD_1..10`
- `ICD9_PRCDR_CD_1..6`
- `HCPCS_CD_1..45`

Type guidance:
- identifiers and code fields are mostly `string`
- date fields are `int64`
- amounts are `double`
- utilization day count is `int64`

## Outpatient Claims Reference

One record per outpatient claim.

Core fields:
- `DESYNPUF_ID`
- `CLM_ID`
- `SEGMENT`
- `CLM_FROM_DT`
- `CLM_THRU_DT`
- `PRVDR_NUM`
- `CLM_PMT_AMT`
- `NCH_PRMRY_PYR_CLM_PD_AMT`
- `AT_PHYSN_NPI`
- `OP_PHYSN_NPI`
- `OT_PHYSN_NPI`
- `NCH_BENE_BLOOD_DDCTBL_LBLTY_AM`
- `NCH_BENE_PTB_DDCTBL_AMT`
- `NCH_BENE_PTB_COINSRNC_AMT`
- `ADMTNG_ICD9_DGNS_CD`

Repeated blocks:
- `ICD9_DGNS_CD_1..10`
- `ICD9_PRCDR_CD_1..6`
- `HCPCS_CD_1..45`

Type guidance:
- identifiers and code fields are mostly `string`
- date fields are `int64`
- amounts are `double`
- utilization fields are `int64`

## Carrier Claims Reference

One record per carrier claim with 13 line items.

Core fields:
- `DESYNPUF_ID`
- `CLM_ID`
- `CLM_FROM_DT`
- `CLM_THRU_DT`

Repeated 13-line blocks:
- `ICD9_DGNS_CD_1..8`
- `PRF_PHYSN_NPI_1..13`
- `TAX_NUM_1..13`
- `HCPCS_CD_1..13`
- `LINE_NCH_PMT_AMT_1..13`
- `LINE_BENE_PTB_DDCTBL_AMT_1..13`
- `LINE_BENE_PRMRY_PYR_PD_AMT_1..13`
- `LINE_COINSRNC_AMT_1..13`
- `LINE_ALOWD_CHRG_AMT_1..13`
- `LINE_PRCSG_IND_CD_1..13`
- `LINE_ICD9_DGNS_CD_1..13`

Type guidance:
- claim and provider IDs are mostly `string`
- tax numbers are stored as `int64` in the current Parquet output
- line amounts are `double`
- processing indicators and diagnosis/procedure codes are `string`

Practical note:
- treat each row as a 13-line carrier claim bundle
- do not unpivot unless you need line-level analysis

## PDE Reference

One record per prescription drug event.

| Field | Meaning | Stored type | Notes |
| --- | --- | --- | --- |
| `DESYNPUF_ID` | Beneficiary code | `string` | Join key |
| `PDE_ID` | Part D event number | `string` | Event identifier |
| `SRVC_DT` | Prescription service date | `int64` | YYYYMMDD |
| `PROD_SRVC_ID` | Product service ID | `string` | Usually a code-like identifier |
| `QTY_DSPNSD_NUM` | Quantity dispensed | `double` | Can be fractional |
| `DAYS_SUPLY_NUM` | Days supply | `int64` | Usually numeric count |
| `PTNT_PAY_AMT` | Patient pay amount | `double` | Monetary amount |
| `TOT_RX_CST_AMT` | Gross drug cost | `double` | Monetary amount |

## Linking And Analysis Rules

### Recommended join order

1. Pick the beneficiary snapshot year you need.
2. Join claims to beneficiaries with `DESYNPUF_ID`.
3. For carrier data, first combine parts `A` and `B`.
4. Use `CLM_THRU_DT` to assign inpatient, outpatient, and carrier claim year when year-specific grouping matters.
5. Use `SRVC_DT` for PDE year logic when needed.

### Common analysis tasks

- Beneficiary profiling:
  - use the yearly beneficiary file as the base table
  - add claim-derived utilization features with beneficiary-level aggregation
- Utilization analysis:
  - group claim rows by beneficiary and claim year
  - count claims, distinct service dates, and distinct providers only after confirming the unit of analysis
- Spending analysis:
  - sum reimbursement and responsibility amounts by beneficiary or cohort window
  - keep negative values unless you have a documented reason to exclude them
- Chronic condition work:
  - use the beneficiary summary chronic flags when you want the published synthetic indicators
  - do not assume they can be perfectly reconstructed from raw claims

### Common gotchas

- Many coded fields look numeric but should still be treated as categorical labels.
- The synthetic files are not suitable for population-level causal inference.
- Regression coefficients and univariate estimates can be biased by the synthetic construction process.
- Split train/validation/test by beneficiary, not by claim row.
- Some beneficiaries have no later-year claims because of death or attrition.
- Provider identifiers in carrier and claim files are synthetic and should not be interpreted as real provider IDs.

## Quick Lookup Prompts

- "Which file has this field?" -> check the family sections above and then the PDF codebook if the field is not a repeated-block name.
- "How do I link these files?" -> use `DESYNPUF_ID`; combine carrier A/B first.
- "Which year should I group by?" -> use `CLM_THRU_DT` for claims and the file year for beneficiary snapshots.
- "Is this value numeric or categorical?" -> inspect the semantic class, not the apparent text digits.
- "Can I infer population-level effects?" -> no; keep conclusions descriptive or clearly framed as model behavior on synthetic data.
