"""CELLGUARD API foundation."""

from pathlib import Path
from functools import lru_cache
from base64 import b64encode
from io import BytesIO
from hashlib import sha256
import math
import logging
import os
import sys
from datetime import date, timedelta

import pandas as pd
import yaml
from fastapi import FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field, ValidationError
from ultralytics import YOLO

app = FastAPI(title="CELLGUARD API", version="1.0.0")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.root_cause_inference import predict_root_cause
from src.risk_inference import predict_risk

DATA_PATH = PROJECT_ROOT / "data" / "factory_process_data.csv"
YOLO_MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "runs" / "detect" / "models" / "defect_detector"
    / "cellguard_yolo-3" / "weights" / "best.pt"
)
DATASET_VALID_IMAGES = Path(__file__).resolve().parents[1] / "data" / "raw" / "weld_defect" / "valid" / "images"
DATASET_VALID_LABELS = Path(__file__).resolve().parents[1] / "data" / "raw" / "weld_defect" / "valid" / "labels"
DATASET_ROOT = Path(__file__).resolve().parents[1] / "data" / "raw" / "weld_defect"
DATASET_CONFIG = DATASET_ROOT / "data.yaml"
DATASET_SPLITS = ("train", "valid", "test")
DATASET_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class RootCauseRequest(BaseModel):
    current: float = Field(ge=0, allow_inf_nan=False)
    voltage: float = Field(ge=0, allow_inf_nan=False)
    temperature: float = Field(ge=0, allow_inf_nan=False)
    pressure: float = Field(ge=0, allow_inf_nan=False)
    welding_time: float = Field(ge=0, allow_inf_nan=False)
    speed: float = Field(ge=0, allow_inf_nan=False)


class RiskPredictionRequest(BaseModel):
    current: float = Field(ge=0, allow_inf_nan=False)
    voltage: float = Field(ge=0, allow_inf_nan=False)
    temperature: float = Field(ge=0, allow_inf_nan=False)
    pressure: float = Field(ge=0, allow_inf_nan=False)
    welding_time: float = Field(ge=0, allow_inf_nan=False)
    speed: float = Field(ge=0, allow_inf_nan=False)


@lru_cache(maxsize=1)
def load_yolo_model() -> YOLO:
    """Load the existing trained weld detector once per API process."""
    if not YOLO_MODEL_PATH.is_file():
        raise HTTPException(status_code=503, detail="Trained YOLO model is unavailable.")
    try:
        return YOLO(str(YOLO_MODEL_PATH))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Trained YOLO model could not be loaded.") from exc


@lru_cache(maxsize=1)
def dataset_class_names() -> dict[int, str]:
    """Read class IDs and display names from the dataset's own YAML metadata."""
    try:
        config = yaml.safe_load(DATASET_CONFIG.read_text(encoding="utf-8")) or {}
        names = config.get("names", {})
        if isinstance(names, list):
            return {class_id: str(name) for class_id, name in enumerate(names)}
        if isinstance(names, dict):
            return {int(class_id): str(name) for class_id, name in names.items()}
    except (OSError, TypeError, ValueError, yaml.YAMLError):
        pass
    return {}


@lru_cache(maxsize=1)
def dataset_catalog() -> tuple[dict, ...]:
    """Index dataset images and their class IDs without exposing local paths."""
    class_names = dataset_class_names()
    entries = []
    for split in DATASET_SPLITS:
        split_root = DATASET_ROOT / split
        image_root = split_root / "images"
        label_root = split_root / "labels"
        if not image_root.is_dir():
            continue
        resolved_root = image_root.resolve()
        for image_path in sorted(image_root.iterdir(), key=lambda path: path.name.casefold()):
            if not image_path.is_file() or image_path.suffix.lower() not in DATASET_IMAGE_EXTENSIONS:
                continue
            resolved_image = image_path.resolve()
            if not resolved_image.is_relative_to(resolved_root):
                continue
            label_path = label_root / f"{image_path.stem}.txt"
            class_ids = set()
            if label_path.is_file():
                try:
                    for line in label_path.read_text(encoding="utf-8").splitlines():
                        if not line.strip():
                            continue
                        try:
                            class_id = int(line.split(maxsplit=1)[0])
                        except (ValueError, IndexError):
                            continue
                        if class_id in class_names:
                            class_ids.add(class_id)
                except OSError:
                    pass
            opaque_id = sha256(f"{split}/{image_path.name}".encode("utf-8")).hexdigest()[:16]
            entries.append({
                "image_id": opaque_id,
                "filename": image_path.name,
                "split": split,
                "class_ids": tuple(sorted(class_ids)),
                "class_names": tuple(class_names[class_id] for class_id in sorted(class_ids)),
                "path": resolved_image,
            })
    return tuple(entries)


@lru_cache(maxsize=1)
def curated_dataset_samples() -> dict[int, Path]:
    """Pick one stable validation image per class without copying dataset files."""
    selected: dict[int, Path] = {}
    if not DATASET_VALID_IMAGES.is_dir() or not DATASET_VALID_LABELS.is_dir():
        return selected

    for label_path in sorted(DATASET_VALID_LABELS.glob("*.txt")):
        image_path = next(
            (DATASET_VALID_IMAGES / f"{label_path.stem}{suffix}" for suffix in (".jpg", ".jpeg", ".png")
             if (DATASET_VALID_IMAGES / f"{label_path.stem}{suffix}").is_file()),
            None,
        )
        if image_path is None:
            continue
        try:
            class_ids = {
                int(line.split(maxsplit=1)[0])
                for line in label_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            }
        except (OSError, ValueError, IndexError):
            continue
        for class_id in sorted(class_ids.intersection(dataset_class_names())):
            selected.setdefault(class_id, image_path)
        if len(selected) == len(dataset_class_names()):
            break
    return selected


frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_URLS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        *frontend_origins,
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


@app.post("/api/root-cause/predict")
async def root_cause_prediction(process: RootCauseRequest) -> dict:
    """Run the existing root-cause classifier for a set of process parameters."""
    try:
        return predict_root_cause(process.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Root-cause model file could not be found.") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Root-cause analysis failed.") from exc


@app.post("/api/risk/predict")
async def risk_prediction(request: Request) -> dict:
    """Run the existing defect-risk model for a set of process parameters."""
    try:
        payload = await request.json()
    except (ValueError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=422, detail="Request body must be valid JSON.") from exc
    try:
        process = RiskPredictionRequest.model_validate(payload)
    except ValidationError as exc:
        details = [
            {"loc": ["body", *error["loc"]], "msg": error["msg"], "type": error["type"]}
            for error in exc.errors(include_input=False)
        ]
        raise HTTPException(status_code=422, detail=details) from exc
    try:
        return predict_risk(process.model_dump())
    except Exception as exc:
        logging.getLogger(__name__).exception("Risk prediction failed.")
        raise HTTPException(status_code=500, detail="Risk prediction failed. Please try again.") from exc


@app.get("/api/inspection/samples")
async def inspection_samples() -> dict:
    """Expose one labeled validation image per weld class with compact thumbnails."""
    samples = []
    for class_id, image_path in curated_dataset_samples().items():
        try:
            with Image.open(image_path) as image:
                thumbnail = image.convert("RGB")
                thumbnail.thumbnail((320, 220))
                thumb_bytes = BytesIO()
                thumbnail.save(thumb_bytes, format="JPEG", quality=78, optimize=True)
        except (OSError, UnidentifiedImageError):
            continue
        samples.append({
            "sample_id": class_id,
            "class_name": dataset_class_names()[class_id],
            "filename": image_path.name,
            "image_url": f"/api/inspection/samples/{class_id}",
            "thumbnail": f"data:image/jpeg;base64,{b64encode(thumb_bytes.getvalue()).decode('ascii')}",
        })
    return {"data_source": "Dataset Samples · weld-defect validation set", "samples": samples}


@app.get("/api/inspection/samples/{sample_id}")
async def inspection_sample_image(sample_id: int) -> FileResponse:
    """Stream an allow-listed validation image directly from the existing dataset."""
    image_path = curated_dataset_samples().get(sample_id)
    if image_path is None or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Dataset sample not found.")
    media_type = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
    return FileResponse(image_path, media_type=media_type, filename=image_path.name)


@app.get("/api/inspection/dataset/images")
async def browse_dataset_images(
    class_id: int | None = None,
    search: str = Query(default="", max_length=120),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=20),
) -> dict:
    """Return a paginated dataset index with filters sourced from YOLO labels."""
    class_names = dataset_class_names()
    if class_id is not None and class_id not in class_names:
        allowed = ", ".join(str(value) for value in sorted(class_names)) or "none"
        raise HTTPException(status_code=400, detail=f"Invalid class filter. Available class IDs: {allowed}.")

    entries = dataset_catalog()
    normalized_search = search.strip().casefold()
    matching = [entry for entry in entries if (
        (class_id is None or class_id in entry["class_ids"])
        and normalized_search in entry["filename"].casefold()
    )]
    total_pages = max(1, math.ceil(len(matching) / page_size))
    if page > total_pages:
        page = total_pages
    start = (page - 1) * page_size
    current_entries = matching[start:start + page_size]
    images = [{
        "image_id": entry["image_id"],
        "filename": entry["filename"],
        "split": entry["split"],
        "class_ids": list(entry["class_ids"]),
        "class_names": list(entry["class_names"]),
        "image_url": f"/api/inspection/dataset/images/{entry['image_id']}",
        "thumbnail_url": f"/api/inspection/dataset/images/{entry['image_id']}?thumbnail=true",
    } for entry in current_entries]

    return {
        "total_images": len(entries),
        "matching_count": len(matching),
        "displayed_count": len(images),
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages if matching else 0,
        "class_filters": [{"class_id": key, "class_name": value} for key, value in sorted(class_names.items())],
        "images": images,
    }


@app.get("/api/inspection/dataset/images/{image_id}")
async def dataset_image(image_id: str, thumbnail: bool = False) -> Response:
    """Serve a catalogued dataset image or thumbnail using only its opaque ID."""
    if len(image_id) != 16 or any(char not in "0123456789abcdef" for char in image_id):
        raise HTTPException(status_code=404, detail="Dataset image not found.")
    entry = next((item for item in dataset_catalog() if item["image_id"] == image_id), None)
    if entry is None:
        raise HTTPException(status_code=404, detail="Dataset image not found.")
    image_path = entry["path"]
    image_root = (DATASET_ROOT / entry["split"] / "images").resolve()
    if not image_path.is_file() or not image_path.is_relative_to(image_root):
        raise HTTPException(status_code=404, detail="Dataset image not found.")
    if not thumbnail:
        media_type = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
        return FileResponse(image_path, media_type=media_type, filename=image_path.name)
    try:
        with Image.open(image_path) as image:
            preview = image.convert("RGB")
            preview.thumbnail((360, 240))
            output = BytesIO()
            preview.save(output, format="JPEG", quality=76, optimize=True)
        return Response(content=output.getvalue(), media_type="image/jpeg", headers={"Cache-Control": "public, max-age=3600"})
    except (OSError, UnidentifiedImageError) as exc:
        raise HTTPException(status_code=422, detail="Dataset image could not be decoded.") from exc


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


@app.get("/api/telemetry/history")
async def telemetry_history(
    machine_id: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    """Return time-bucketed historical quality data from the factory CSV."""
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date must be on or before end_date.")

    try:
        data = pd.read_csv(DATA_PATH)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        logging.getLogger(__name__).exception("Factory history CSV could not be loaded.")
        raise HTTPException(status_code=500, detail="Factory history CSV could not be loaded.") from exc

    required_columns = {
        "timestamp", "machine_id", "defect_status", "current", "temperature",
        "pressure", "welding_time",
    }
    missing_columns = required_columns.difference(data.columns)
    if missing_columns:
        raise HTTPException(
            status_code=500,
            detail=f"Factory history CSV is missing required columns: {', '.join(sorted(missing_columns))}.",
        )

    available_machines = sorted(data["machine_id"].dropna().astype(str).unique().tolist())
    if machine_id is not None and machine_id not in available_machines:
        allowed = ", ".join(available_machines) or "none"
        raise HTTPException(
            status_code=422,
            detail=f"Invalid machine_id. Available machines: {allowed}.",
        )

    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    data = data.dropna(subset=["timestamp"])
    if machine_id is not None:
        data = data[data["machine_id"].astype(str) == machine_id]
    if start_date is not None:
        data = data[data["timestamp"] >= pd.Timestamp(start_date)]
    if end_date is not None:
        data = data[data["timestamp"] < pd.Timestamp(end_date + timedelta(days=1))]

    if start_date is not None:
        range_start = pd.Timestamp(start_date)
    elif not data.empty:
        range_start = data["timestamp"].min()
    else:
        range_start = pd.Timestamp("1970-01-01")
    if end_date is not None:
        range_end = pd.Timestamp(end_date + timedelta(days=1))
    elif not data.empty:
        range_end = data["timestamp"].max() + pd.Timedelta(minutes=10)
    else:
        range_end = range_start

    duration = max(pd.Timedelta(0), range_end - range_start)
    if duration <= pd.Timedelta(days=1):
        bucket_interval = "10min"
    elif duration <= pd.Timedelta(days=7):
        bucket_interval = "1h"
    elif duration <= pd.Timedelta(days=45):
        bucket_interval = "6h"
    else:
        bucket_interval = "1D"

    time_series = []
    earliest_timestamp = None
    latest_timestamp = None
    if not data.empty:
        earliest = data["timestamp"].min()
        latest = data["timestamp"].max()
        earliest_timestamp = earliest.isoformat(timespec="seconds")
        latest_timestamp = latest.isoformat(timespec="seconds")

        numeric_columns = ["current", "temperature", "pressure", "welding_time"]
        for column in numeric_columns:
            data[column] = pd.to_numeric(data[column], errors="coerce")
        data["bucket_timestamp"] = data["timestamp"].dt.floor(bucket_interval)
        data["is_defect"] = data["defect_status"].eq("Defect").astype(int)
        grouped = data.groupby("bucket_timestamp", sort=True).agg(
            total_inspected=("defect_status", "size"),
            defect_count=("is_defect", "sum"),
            average_current=("current", "mean"),
            average_temperature=("temperature", "mean"),
            average_pressure=("pressure", "mean"),
            average_welding_time=("welding_time", "mean"),
        )
        bucket_index = pd.date_range(
            start=grouped.index.min(),
            end=grouped.index.max(),
            freq=bucket_interval,
        )
        grouped = grouped.reindex(bucket_index)
        grouped["total_inspected"] = grouped["total_inspected"].fillna(0).astype(int)
        grouped["defect_count"] = grouped["defect_count"].fillna(0).astype(int)
        grouped["defect_rate"] = grouped.apply(
            lambda row: round(row["defect_count"] / row["total_inspected"] * 100, 2)
            if row["total_inspected"] else 0.0,
            axis=1,
        )
        for timestamp, row in grouped.iterrows():
            time_series.append({
                "timestamp": timestamp.isoformat(timespec="seconds"),
                "total_inspected": int(row["total_inspected"]),
                "defect_count": int(row["defect_count"]),
                "defect_rate": float(row["defect_rate"]),
                "average_current": round(float(row["average_current"]), 2) if pd.notna(row["average_current"]) else None,
                "average_temperature": round(float(row["average_temperature"]), 2) if pd.notna(row["average_temperature"]) else None,
                "average_pressure": round(float(row["average_pressure"]), 2) if pd.notna(row["average_pressure"]) else None,
                "average_welding_time": round(float(row["average_welding_time"]), 2) if pd.notna(row["average_welding_time"]) else None,
            })

    return {
        "data_source": "Synthetic demonstration data — not real production history.",
        "machine_id": machine_id,
        "start_date": start_date.isoformat() if start_date else None,
        "end_date": end_date.isoformat() if end_date else None,
        "bucket_interval": bucket_interval,
        "record_count": int(len(data)),
        "earliest_timestamp": earliest_timestamp,
        "latest_timestamp": latest_timestamp,
        "available_machines": available_machines,
        "time_series": time_series,
    }
@app.post("/api/inspection")
async def inspect_image(image: UploadFile = File(...)) -> dict:
    """Run the existing weld detector on an uploaded image."""
    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Upload a JPG or PNG image.")

    try:
        image_bytes = await image.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="The uploaded image is empty.")
        with Image.open(BytesIO(image_bytes)) as source:
            source.load()
            source_image = source.convert("RGB")
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid image.") from exc
    finally:
        await image.close()

    try:
        result = load_yolo_model().predict(source=source_image, conf=0.25, verbose=False)[0]
        annotated = Image.fromarray(result.plot()[:, :, ::-1])
        output = BytesIO()
        annotated.save(output, format="PNG")
        detections = []
        for box in result.boxes:
            class_id = int(box.cls.item())
            detections.append({
                "detected_class": load_yolo_model().names[class_id],
                "confidence": round(float(box.conf.item()), 4),
                "bounding_box": [round(float(value), 1) for value in box.xyxy[0].tolist()],
            })
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Image inspection failed. Please try another image.") from exc

    return {
        "detections": detections,
        "annotated_image": f"data:image/png;base64,{b64encode(output.getvalue()).decode('ascii')}",
        "image_width": source_image.width,
        "image_height": source_image.height,
    }
