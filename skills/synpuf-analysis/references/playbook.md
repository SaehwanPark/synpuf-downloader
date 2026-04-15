# SynPUF Analysis Playbook

## Study Design Checklist

- Define the outcome first.
- Pick the observation window and any washout period.
- Decide whether the study unit is beneficiary, claim, or beneficiary-year.
- Prevent leakage by excluding future claims and post-index totals from the feature set when they would not be observable at prediction time.
- Use beneficiary-level splitting for validation.

## Feature Ideas

- beneficiary demographics
- coverage months
- chronic condition indicators
- yearly claim counts
- distinct service dates
- provider counts
- diagnosis and procedure counts
- reimbursement and responsibility summaries

## Modeling Guardrails

- Keep labels and features time-aligned.
- Be cautious with data from beneficiaries who die or have partial follow-up.
- Synthetic data can support workflow development and model prototyping, but not real-population inference.
- Report descriptive performance and uncertainty conservatively.

## Useful Output Style

- cohort definition
- feature list
- leakage checks
- validation plan
- caveats

