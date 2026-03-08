"""Databricks batch ingestion placeholder for INTELLI-CREDIT.

This script is designed to be adapted into a Databricks job that ingests
structured company data and writes curated records for downstream scoring.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IngestionRecord:
    company_id: str
    source: str
    payload: dict


def normalize_record(record: IngestionRecord) -> dict:
    return {
        "company_id": record.company_id,
        "source": record.source,
        "payload": record.payload,
    }


def run_ingestion(records: list[IngestionRecord]) -> list[dict]:
    return [normalize_record(record) for record in records]


if __name__ == "__main__":
    sample = IngestionRecord(company_id="demo", source="manual", payload={"revenue": 100.0})
    print(run_ingestion([sample]))
