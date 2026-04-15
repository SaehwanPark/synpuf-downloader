---
name: synpuf-analysis
description: Build SynPUF cohorts, features, and models for claims research.
---

# SynPUF Analysis

## Overview

Use this skill when you are designing a cohort, building features, doing EDA, or training a model on SynPUF-style Medicare data.

## When To Use

- cohort design and index-date selection
- beneficiary-level aggregations
- claims utilization and spending analysis
- predictive modeling, clustering, or descriptive epidemiology on SynPUF

## Default Analysis Workflow

1. Define the unit of analysis first.
2. Choose the index year or index date.
3. Build a beneficiary table before adding claims features.
4. Aggregate claims by beneficiary and analysis window.
5. Split by beneficiary, not by claim row.
6. Check leakage, censoring, and synthetic-data caveats before modeling.

## Analysis Rules

- Use `DESYNPUF_ID` as the beneficiary grouping key.
- Use `CLM_THRU_DT` when you need claim-year assignment.
- Keep beneficiary snapshots and claim history separate until the feature layer.
- Treat annual reimbursement totals as derived features, especially if they appear in a target-adjacent prediction problem.
- Use the published chronic flags when you want the synthetic indicators as given, rather than re-deriving them unless you explicitly need that exercise.
- Do not present causal or population-level claims as if this were real Medicare data.

## Modeling Guidance

- Prefer beneficiary-level splits for train/validation/test.
- Be careful with temporal leakage from future claims, death dates, or annual totals.
- Use simple descriptive baselines first.
- For very wide claims tables, consider grouped features:
  - counts of claims
  - counts of distinct service dates
  - counts of distinct diagnosis or procedure codes
  - utilization and spending summaries by year
  - chronic condition flags
- If the question is about explainability, keep the feature set interpretable and compact.

## Resources

- [analysis playbook](references/playbook.md)

