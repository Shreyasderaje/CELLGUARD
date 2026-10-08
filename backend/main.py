"""CELLGUARD API foundation."""

from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CELLGUARD API", version="1.0.0")
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "factory_process_data.csv"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Identify the CELLGUARD API service."""
    return {"service": "CELLGUARD API", "message": "API foundation is running"}


@app.get("/api/health")
async def health() -> dict[str, str]:
    """Report that the API process is responding."""
    return {"status": "ok", "service": "CELLGUARD API", "version": "1.0.0"}


@app.get("/api/telemetry/summary")
async def telemetry_summary() -> dict:
    """Calculate command-center telemetry from the factory process CSV."""
    try:
        data = pd.read_csv(DATA_PATH)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Factory telemetry CSV could not be loaded.",
        ) from exc

    required_columns = {
        "machine_id",
        "current",
        "temperature",
        "pressure",
        "defect_status",
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise HTTPException(
            status_code=500,
            detail=f"Factory telemetry CSV is missing required columns: {', '.join(sorted(missing_columns))}.",
        )

    total_inspections = len(data)
    defects = data["defect_status"].eq("Defect")
    defect_count = int(defects.sum())
    defect_rate = (defect_count / total_inspections * 100) if total_inspections else 0.0
    high_risk_batches = int(
        (
            (data["current"] > 210)
            | (data["temperature"] > 100)
            | (data["pressure"] < 3.8)
        ).sum()
    )

    machines = []
    for machine_id, machine_data in data.groupby("machine_id", dropna=True, sort=True):
        machine_defects = machine_data["defect_status"].eq("Defect")
        machine_total = len(machine_data)
        machine_defect_count = int(machine_defects.sum())
        machine_defect_rate = (
            machine_defect_count / machine_total * 100 if machine_total else 0.0
        )
        if machine_defect_rate > 18:
            status = "CRITICAL"
        elif machine_defect_rate > 12:
            status = "WARNING"
        else:
            status = "HEALTHY"
        machines.append(
            {
                "machine_id": str(machine_id),
                "total_batches": machine_total,
                "defect_count": machine_defect_count,
                "defect_rate": round(machine_defect_rate, 2),
                "status": status,
            }
        )

    return {
        "total_inspections": total_inspections,
        "defect_count": defect_count,
        "defect_rate": round(defect_rate, 2),
        "high_risk_batches": high_risk_batches,
        "active_workstations": int(data["machine_id"].nunique(dropna=True)),
        "machines": machines,
        "data_source": "Synthetic factory telemetry",
        "record_count": total_inspections,
    }
