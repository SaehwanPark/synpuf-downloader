from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path

import pyarrow as pa

from synpuf_downloader.domain.models import (
  CarrierPart,
  ColumnRule,
  ColumnSemantic,
  ConversionJob,
  ConversionResult,
  ConversionStatus,
  ConversionSummary,
  CsvArtifact,
  DatasetKind,
  SampleId,
)

DATASET_ORDER = (
  DatasetKind.BENEFICIARY_2008,
  DatasetKind.BENEFICIARY_2009,
  DatasetKind.BENEFICIARY_2010,
  DatasetKind.INPATIENT_CLAIMS,
  DatasetKind.OUTPATIENT_CLAIMS,
  DatasetKind.PRESCRIPTION_DRUG_EVENTS,
  DatasetKind.CARRIER_CLAIMS,
)

CSV_PATTERNS = (
  (
    re.compile(r'^DE1_0_2008_Beneficiary_Summary_File_Sample_(\d+)\.csv$'),
    DatasetKind.BENEFICIARY_2008,
    None,
  ),
  (
    re.compile(r'^DE1_0_2009_Beneficiary_Summary_File_Sample_(\d+)\.csv$'),
    DatasetKind.BENEFICIARY_2009,
    None,
  ),
  (
    re.compile(r'^DE1_0_2010_Beneficiary_Summary_File_Sample_(\d+)\.csv$'),
    DatasetKind.BENEFICIARY_2010,
    None,
  ),
  (
    re.compile(r'^DE1_0_2008_to_2010_Carrier_Claims_Sample_(\d+)(A|B)\.csv$'),
    DatasetKind.CARRIER_CLAIMS,
    'carrier',
  ),
  (
    re.compile(r'^DE1_0_2008_to_2010_Inpatient_Claims_Sample_(\d+)\.csv$'),
    DatasetKind.INPATIENT_CLAIMS,
    None,
  ),
  (
    re.compile(r'^DE1_0_2008_to_2010_Outpatient_Claims_Sample_(\d+)\.csv$'),
    DatasetKind.OUTPATIENT_CLAIMS,
    None,
  ),
  (
    re.compile(r'^DE1_0_2008_to_2010_Prescription_Drug_Events_Sample_(\d+)\.csv$'),
    DatasetKind.PRESCRIPTION_DRUG_EVENTS,
    None,
  ),
)

STRING_COLUMNS = frozenset(
  {
    'desynpuf_id',
    'bene_id',
    'clm_id',
    'clm_line_num',
    'prf_physn_npi',
    'prf_physn_upin',
    'carr_clm_pmt_dnl_cd',
    'carr_clm_hcpcs_cd',
    'carr_clm_hcpcs_1_mdfr_cd',
    'carr_clm_hcpcs_2_mdfr_cd',
    'prv_inst_oscar_num',
    'clm_fac_type_cd',
    'clm_srv_clsfctn_type_cd',
    'clm_freq_cd',
    'icd_dgns_cd1',
    'icd_dgns_cd2',
    'icd_dgns_cd3',
    'icd_dgns_cd4',
    'icd_dgns_cd5',
    'icd_dgns_cd6',
    'icd_dgns_cd7',
    'icd_dgns_cd8',
    'icd_dgns_cd9',
    'icd_dgns_cd10',
    'icd_prcdr_cd1',
    'icd_prcdr_cd2',
    'icd_prcdr_cd3',
    'icd_prcdr_cd4',
    'icd_prcdr_cd5',
    'icd_prcdr_cd6',
    'hcpcs_cd',
    'rev_cntr_ide_ndc_upc_num',
    'prdsrv_id',
    'plan_cntrct_rec_id',
    'pbp_id',
    'ptnt_rsdnc_cd',
    'gnn_cd',
    'daw_prod_cd',
    'carr_num',
    'clm_carr_pmt_dnl_cd',
    'carr_clm_entry_cd',
    'line_nch_pmt_cd',
    'line_bene_pmt_cd',
    'line_prvdr_pmt_cd',
    'line_bene_ptb_ddctbl_cd',
    'line_bene_prmry_pyr_cd',
    'line_coinsrnc_cd',
    'line_alowd_chrg_cd',
    'line_prcsg_ind_cd',
    'line_pmt_80_100_cd',
    'line_nch_alwbl_cd',
    'hcpcs_1st_mdfr_cd',
    'hcpcs_2nd_mdfr_cd',
    'betos_cd',
    'prov_spclty',
  }
)

STRING_TOKENS = ('_id', '_cd', 'npi', 'upin', 'hcpcs', 'icd_', 'ndc', 'oscar', 'betos')


def group_csv_artifacts(paths: tuple[Path, ...]) -> Mapping[DatasetKind, tuple[CsvArtifact, ...]]:
  parsed = tuple(
    artifact for artifact in (_parse_csv_artifact(path) for path in paths) if artifact is not None
  )
  return {
    dataset_kind: tuple(
      sorted(
        (artifact for artifact in parsed if artifact.dataset_kind == dataset_kind),
        key=_artifact_order_key,
      )
    )
    for dataset_kind in DATASET_ORDER
    if any(artifact.dataset_kind == dataset_kind for artifact in parsed)
  }


def derive_column_rules(
  header: tuple[str, ...],
  inferred_schema: pa.Schema,
) -> tuple[ColumnRule, ...]:
  return tuple(
    _column_rule(column_name, inferred_schema.field(column_name).type) for column_name in header
  )


def build_arrow_schema(rules: tuple[ColumnRule, ...]) -> pa.Schema:
  return pa.schema([pa.field(rule.name, rule.arrow_type, nullable=rule.nullable) for rule in rules])


def build_conversion_jobs(
  grouped: Mapping[DatasetKind, tuple[CsvArtifact, ...]],
) -> tuple[ConversionJob, ...]:
  return tuple(
    ConversionJob(
      dataset_kind=dataset_kind,
      output_name=dataset_output_name(dataset_kind),
      artifacts=grouped.get(dataset_kind, ()),
      max_rows_per_file=2_000_000 if dataset_kind == DatasetKind.CARRIER_CLAIMS else 1_000_000,
    )
    for dataset_kind in DATASET_ORDER
    if grouped.get(dataset_kind)
  )


def summarize_conversions(results: tuple[ConversionResult, ...]) -> ConversionSummary:
  return ConversionSummary(
    successful_datasets=sum(result.status == ConversionStatus.WRITTEN for result in results),
    failed_datasets=sum(result.status == ConversionStatus.FAILED for result in results),
    skipped_datasets=sum(result.status == ConversionStatus.SKIPPED for result in results),
    results=results,
  )


def dataset_output_name(dataset_kind: DatasetKind) -> str:
  return {
    DatasetKind.BENEFICIARY_2008: 'DE1_0_2008_Beneficiary_Summary_File.parquet',
    DatasetKind.BENEFICIARY_2009: 'DE1_0_2009_Beneficiary_Summary_File.parquet',
    DatasetKind.BENEFICIARY_2010: 'DE1_0_2010_Beneficiary_Summary_File.parquet',
    DatasetKind.CARRIER_CLAIMS: 'DE1_0_2008_to_2010_Carrier_Claims.parquet',
    DatasetKind.INPATIENT_CLAIMS: 'DE1_0_2008_to_2010_Inpatient_Claims.parquet',
    DatasetKind.OUTPATIENT_CLAIMS: 'DE1_0_2008_to_2010_Outpatient_Claims.parquet',
    DatasetKind.PRESCRIPTION_DRUG_EVENTS: 'DE1_0_2008_to_2010_Prescription_Drug_Events.parquet',
  }[dataset_kind]


def _parse_csv_artifact(path: Path) -> CsvArtifact | None:
  for pattern, dataset_kind, carrier_marker in CSV_PATTERNS:
    match = pattern.match(path.name)
    if match is None:
      continue
    sample_id = SampleId(int(match.group(1)))
    carrier_part = CarrierPart(match.group(2)) if carrier_marker == 'carrier' else None
    return CsvArtifact(
      path=path,
      sample_id=sample_id,
      dataset_kind=dataset_kind,
      carrier_part=carrier_part,
    )
  return None


def _column_rule(column_name: str, inferred_type: pa.DataType) -> ColumnRule:
  normalized_name = column_name.lower()
  if _is_string_column(normalized_name):
    return ColumnRule(
      name=column_name,
      semantic=ColumnSemantic.STRING_CODE,
      arrow_type=pa.string(),
    )
  if pa.types.is_integer(inferred_type):
    return ColumnRule(name=column_name, semantic=ColumnSemantic.INTEGER, arrow_type=pa.int64())
  if pa.types.is_floating(inferred_type):
    return ColumnRule(name=column_name, semantic=ColumnSemantic.FLOAT, arrow_type=pa.float64())
  if pa.types.is_boolean(inferred_type):
    return ColumnRule(name=column_name, semantic=ColumnSemantic.BOOLEAN, arrow_type=pa.bool_())
  if pa.types.is_date(inferred_type):
    return ColumnRule(name=column_name, semantic=ColumnSemantic.DATE, arrow_type=pa.date32())
  if pa.types.is_timestamp(inferred_type):
    return ColumnRule(
      name=column_name,
      semantic=ColumnSemantic.TIMESTAMP,
      arrow_type=inferred_type,
    )
  return ColumnRule(name=column_name, semantic=ColumnSemantic.TEXT, arrow_type=pa.string())


def _is_string_column(normalized_name: str) -> bool:
  return normalized_name in STRING_COLUMNS or any(
    token in normalized_name for token in STRING_TOKENS
  )


def _artifact_order_key(artifact: CsvArtifact) -> tuple[int, str]:
  part_value = artifact.carrier_part.value if artifact.carrier_part is not None else ''
  return (artifact.sample_id.value, part_value)
