---
name: synpuf-orientation
description: Find SynPUF files, decode schemas, and answer data layout questions.
---

# SynPUF Orientation

## Overview

Use this skill when you need to locate a SynPUF artifact, understand how files link together, interpret a column name, or confirm the right sample/year partition before analysis.

## When To Use

- map CSV files to Parquet datasets
- check what a field means or what type it should be
- determine join keys and sample partitioning
- answer questions like "which file contains this variable?" or "how do these records relate?"

## Fast Workflow

1. Identify the family: beneficiary, inpatient, outpatient, carrier, or PDE.
2. Identify the sample and year.
3. Confirm the key: `DESYNPUF_ID` almost always anchors the join.
4. Check whether carrier `A` and `B` need to be combined.
5. Confirm storage conventions before answering: dates are YYYYMMDD integers, code fields often stay as strings, and claims are partitioned by sample.

## Rules You Can Rely On

- `DESYNPUF_ID` is the beneficiary-level join key across families.
- Carrier `A` and `B` are one logical dataset and should be concatenated first.
- Claim year is usually driven by `CLM_THRU_DT`, not by the file name.
- Do not assume digit-like codes are numeric measures.
- Preserve identifiers, codes, and provider numbers as strings unless the data source explicitly says otherwise.
- If `docs/agent-codebook.md` exists in the workspace, use it as the local lookup reference for the exact field inventory.

## What A Good Answer Looks Like

- names the exact file or field
- states the join key or partition key
- includes a short caveat if the field is synthetic, repeated, or time-varying
- avoids unnecessary theory when the user only needs a lookup

## Resources

- [lookup reference](references/lookup.md)

