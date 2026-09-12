# Architecture Notes

The implementation separates ingestion, validation, KPI calculation, reporting, and optional narrative generation.

`metrics.py` contains pure transformations that are independently testable. `pipeline.py` coordinates file input and output. `insights.py` provides an offline deterministic summary and an optional API-backed summary that receives aggregated metrics only. `cli.py` is the command-line entry point.

The reporting layer keeps dimensional rows separate from overall rows. This avoids double counting when a BI tool aggregates a table. Ratios are calculated from aggregated numerators and denominators rather than by averaging row-level percentages.

