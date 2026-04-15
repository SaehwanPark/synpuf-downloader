# SynPUF Lookup Reference

## Core Facts

- The dataset has 5 families: beneficiary, inpatient, outpatient, carrier, and PDE.
- Each sample contains 8 CSVs.
- `DESYNPUF_ID` is the common join key.
- Carrier part `A` and `B` should be merged before analysis.
- Claim year is usually derived from `CLM_THRU_DT`.
- Date fields are commonly stored as `YYYYMMDD` integers.

## Common Field Patterns

- Beneficiary summary:
  - demographic and coverage fields
  - chronic condition indicators
  - annual reimbursement totals
- Inpatient/outpatient:
  - claim-level header fields
  - diagnosis and procedure code blocks
  - revenue center / HCPCS blocks
- Carrier:
  - 13 repeated line-item blocks
  - payment, deductible, coinsurance, and processing fields
- PDE:
  - small event table with service date and cost fields

## Answering Checklist

1. State the file family.
2. State the key or grouping rule.
3. State the storage convention for the field.
4. Mention if the field is synthetic, repeated, or derived.
5. If the exact column is not obvious, inspect the codebook or the local Parquet schema.

