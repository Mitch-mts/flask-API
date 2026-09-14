"""
In-memory upload jobs and selectable cleaning operations.

Flow used by Data Studio:
1. create_from_upload / create_from_existing stores a pandas DataFrame
2. process() applies the user-selected cleaning steps in a background thread
3. write_workbook() saves an .xlsx so the dashboard can open the sheet
4. get_record() returns one row at a time for the inspect pager
5. run_explore() calls ServiceFunctions helpers on that sheet
"""

import math
import os
import re
import threading
import uuid
from copy import deepcopy
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px

from ServiceFunctions import get_data

ALLOWED_EXTENSIONS = {".csv", ".xls", ".xlsx"}
MAX_PREVIEW_ROWS = 20

AVAILABLE_FEATURES = [
    {
        "id": "normalize_column_names",
        "label": "Normalize column names",
        "description": "Lowercase names and replace spaces or hyphens with underscores.",
        "needs_columns": False,
    },
    {
        "id": "strip_whitespace",
        "label": "Trim text whitespace",
        "description": "Strip leading and trailing spaces and treat blank cells as missing.",
        "needs_columns": False,
    },
    {
        "id": "infer_numeric_types",
        "label": "Convert number-like text to numbers",
        "description": "Turn columns that are mostly numeric text into real numbers so charts and outliers work.",
        "needs_columns": False,
    },
    {
        "id": "drop_unnamed_columns",
        "label": "Drop unnamed columns",
        "description": "Remove leftover Excel index columns such as Unnamed: 0.",
        "needs_columns": False,
    },
    {
        "id": "drop_duplicates",
        "label": "Remove duplicate rows",
        "description": "Keep the first copy of any fully duplicated row.",
        "needs_columns": False,
    },
    {
        "id": "drop_empty_rows",
        "label": "Drop completely empty rows",
        "description": "Remove rows where every cell is blank.",
        "needs_columns": False,
    },
    {
        "id": "drop_missing_rows",
        "label": "Drop rows with any missing value",
        "description": "Remove a row if any column is empty.",
        "needs_columns": False,
    },
    {
        "id": "fill_missing",
        "label": "Fill missing values",
        "description": "Fill blanks using mean or median for numbers and mode for text.",
        "needs_columns": False,
        "options": ["auto", "mean", "median", "mode", "ffill"],
    },
    {
        "id": "remove_outliers_iqr",
        "label": "Remove numeric outliers (IQR)",
        "description": "Drop rows outside 1.5 × IQR on selected numeric columns (or all numeric columns).",
        "needs_columns": True,
    },
    {
        "id": "drop_columns",
        "label": "Drop selected columns",
        "description": "Remove columns you do not want in the export.",
        "needs_columns": True,
    },
    {
        "id": "sort_by",
        "label": "Sort by column",
        "description": "Sort the cleaned table by one or more columns.",
        "needs_columns": True,
    },
]

FEATURE_LABELS = {feature["id"]: feature["label"] for feature in AVAILABLE_FEATURES}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def allowed_file(filename):
    _, ext = os.path.splitext((filename or "").lower())
    return ext in ALLOWED_EXTENSIONS


def new_job_id():
    return uuid.uuid4().hex


def _json_value(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _safe_records(frame, limit=None):
    subset = frame if limit is None else frame.head(limit)
    records = subset.to_dict("records")
    return [
        {str(key): _json_value(value) for key, value in row.items()}
        for row in records
    ]


def _column_profile(frame):
    profile = []
    for column in frame.columns:
        series = frame[column]
        missing = int(series.isna().sum())
        dtype = str(series.dtype)
        profile.append({
            "name": str(column),
            "dtype": dtype,
            "missing": missing,
            "missing_pct": round((missing / len(frame) * 100), 2) if len(frame) else 0,
            "unique": int(series.nunique(dropna=True)),
            "numeric": pd.api.types.is_numeric_dtype(series),
        })
    return profile


def summarize_frame(frame, label="current"):
    return {
        "label": label,
        "rows": int(len(frame)),
        "columns": int(frame.shape[1]),
        "column_names": [str(column) for column in frame.columns],
        "profile": _column_profile(frame),
        "preview": _safe_records(frame, MAX_PREVIEW_ROWS),
        "dtypes": {str(column): str(dtype) for column, dtype in frame.dtypes.items()},
    }


def _normalize_column_names(frame):
    renamed = {}
    used = set()
    for column in frame.columns:
        name = str(column).strip().lower()
        name = re.sub(r"[^\w]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("_") or "column"
        candidate = name
        index = 2
        while candidate in used:
            candidate = f"{name}_{index}"
            index += 1
        used.add(candidate)
        renamed[column] = candidate
    return frame.rename(columns=renamed)


def _strip_whitespace(frame):
    cleaned = frame.copy()
    for column in cleaned.select_dtypes(include=["object", "string"]).columns:
        cleaned[column] = cleaned[column].apply(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        cleaned[column] = cleaned[column].replace("", pd.NA)
    return cleaned


def _infer_numeric_types(frame):
    cleaned = frame.copy()
    for column in cleaned.columns:
        if pd.api.types.is_numeric_dtype(cleaned[column]):
            continue
        converted = pd.to_numeric(cleaned[column], errors="coerce")
        original_non_null = cleaned[column].notna().sum()
        converted_non_null = converted.notna().sum()
        if original_non_null and converted_non_null / original_non_null >= 0.8:
            cleaned[column] = converted
    return cleaned


def _drop_unnamed_columns(frame):
    keep = [
        column for column in frame.columns
        if not re.match(r"(?i)^unnamed", str(column).strip())
    ]
    return frame.loc[:, keep]


def _fill_missing(frame, strategy="auto"):
    filled = frame.copy()
    strategy = (strategy or "auto").lower()

    if strategy == "ffill":
        return filled.ffill()

    for column in filled.columns:
        series = filled[column]
        if not series.isna().any():
            continue
        if strategy == "mode" or (strategy == "auto" and not pd.api.types.is_numeric_dtype(series)):
            mode = series.mode(dropna=True)
            if not mode.empty:
                filled[column] = series.fillna(mode.iloc[0])
            continue
        if pd.api.types.is_numeric_dtype(series):
            if strategy == "median" or strategy == "auto":
                filled[column] = series.fillna(series.median())
            elif strategy == "mean":
                filled[column] = series.fillna(series.mean())
    return filled


def _remove_outliers_iqr(frame, columns=None):
    cleaned = frame.copy()
    target_columns = columns or [
        column for column in cleaned.columns if pd.api.types.is_numeric_dtype(cleaned[column])
    ]
    mask = pd.Series(True, index=cleaned.index)
    for column in target_columns:
        if column not in cleaned.columns or not pd.api.types.is_numeric_dtype(cleaned[column]):
            continue
        q1 = cleaned[column].quantile(0.25)
        q3 = cleaned[column].quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask &= cleaned[column].isna() | ((cleaned[column] >= lower) & (cleaned[column] <= upper))
    return cleaned.loc[mask].reset_index(drop=True)


def apply_operations(frame, operations):
    """Apply user-selected cleaning steps in the given order."""
    cleaned = frame.copy()
    applied = []

    for operation in operations or []:
        name = operation.get("id") or operation.get("name")
        columns = operation.get("columns") or []
        if isinstance(columns, str):
            columns = [columns]

        before_rows, before_cols = cleaned.shape

        if name == "normalize_column_names":
            cleaned = _normalize_column_names(cleaned)
        elif name == "strip_whitespace":
            cleaned = _strip_whitespace(cleaned)
        elif name == "infer_numeric_types":
            cleaned = _infer_numeric_types(cleaned)
        elif name == "drop_unnamed_columns":
            cleaned = _drop_unnamed_columns(cleaned)
        elif name == "drop_duplicates":
            cleaned = cleaned.drop_duplicates().reset_index(drop=True)
        elif name == "drop_empty_rows":
            cleaned = cleaned.dropna(how="all").reset_index(drop=True)
        elif name == "drop_missing_rows":
            cleaned = cleaned.dropna(how="any").reset_index(drop=True)
        elif name == "fill_missing":
            cleaned = _fill_missing(cleaned, operation.get("strategy", "auto"))
        elif name == "remove_outliers_iqr":
            cleaned = _remove_outliers_iqr(cleaned, columns or None)
        elif name == "drop_columns":
            existing = [column for column in columns if column in cleaned.columns]
            if existing:
                cleaned = cleaned.drop(columns=existing)
        elif name == "sort_by":
            existing = [column for column in columns if column in cleaned.columns]
            if existing:
                cleaned = cleaned.sort_values(
                    by=existing,
                    ascending=operation.get("ascending", True),
                ).reset_index(drop=True)
        else:
            raise ValueError(f"Unknown processing feature: {name}")

        applied.append({
            "id": name,
            "label": FEATURE_LABELS.get(name, name),
            "rows_before": int(before_rows),
            "rows_after": int(cleaned.shape[0]),
            "columns_before": int(before_cols),
            "columns_after": int(cleaned.shape[1]),
        })

    return cleaned, applied


def build_chart(frame, chart_type, x=None, y=None):
    if frame is None or frame.empty:
        raise ValueError("No data available to chart.")

    chart_type = (chart_type or "").lower()
    columns = list(frame.columns)
    x = x if x in columns else columns[0]
    numeric_columns = [column for column in columns if pd.api.types.is_numeric_dtype(frame[column])]

    if chart_type == "histogram":
        if x not in numeric_columns and numeric_columns:
            x = numeric_columns[0]
        figure = px.histogram(frame, x=x, title=f"Distribution of {x}")
    elif chart_type == "bar":
        counts = frame[x].astype(str).value_counts().head(25).reset_index()
        counts.columns = [x, "count"]
        figure = px.bar(counts, x=x, y="count", title=f"Top values in {x}")
    elif chart_type == "pie":
        counts = frame[x].astype(str).value_counts().head(12).reset_index()
        counts.columns = [x, "count"]
        figure = px.pie(counts, names=x, values="count", title=f"Share of {x}")
    elif chart_type == "scatter":
        y = y if y in numeric_columns else (numeric_columns[1] if len(numeric_columns) > 1 else None)
        if x not in numeric_columns or y is None:
            raise ValueError("Scatter charts need two numeric columns.")
        figure = px.scatter(frame, x=x, y=y, title=f"{y} vs {x}")
    elif chart_type == "box":
        if x not in numeric_columns and numeric_columns:
            x = numeric_columns[0]
        figure = px.box(frame, y=x, title=f"Box plot of {x}")
    elif chart_type == "line":
        y = y if y in numeric_columns else (numeric_columns[0] if numeric_columns else None)
        if y is None:
            raise ValueError("Line charts need a numeric Y column.")
        figure = px.line(frame.reset_index(), x="index", y=y, title=f"{y} over row order")
    else:
        raise ValueError("Supported charts: histogram, bar, pie, scatter, box, line.")

    figure.update_layout(margin=dict(l=40, r=20, t=60, b=40), paper_bgcolor="white")
    return figure.to_json()


class PipelineStore:
    """Keeps uploaded and cleaned frames in memory for the current process."""

    def __init__(self, upload_dir):
        self.upload_dir = upload_dir
        self._jobs = {}
        self._lock = threading.Lock()
        os.makedirs(upload_dir, exist_ok=True)

    def create_from_upload(self, file_storage):
        filename = file_storage.filename or ""
        if not allowed_file(filename):
            raise ValueError("Please upload a .csv, .xls, or .xlsx file.")

        job_id = new_job_id()
        _, ext = os.path.splitext(filename.lower())
        saved_name = f"{job_id}{ext}"
        path = os.path.join(self.upload_dir, saved_name)
        file_storage.save(path)

        frame = get_data(path)
        return self._store_job(job_id, filename, path, frame)

    def create_from_existing(self, dataset_name, dataset_path):
        job_id = new_job_id()
        frame = get_data(dataset_path)
        return self._store_job(job_id, f"{dataset_name} (built-in)", dataset_path, frame)

    def _store_job(self, job_id, source_name, path, frame):
        now = utc_now()
        job = {
            "id": job_id,
            "source_name": source_name,
            "path": path,
            "original": frame,
            "cleaned": frame.copy(),
            "applied": [],
            "status": "uploaded",
            "error": None,
            "exported": False,
            "created_at": now,
            "updated_at": now,
        }
        with self._lock:
            self._jobs[job_id] = job
        # Write an Excel copy immediately so "Open Excel" works before cleaning.
        try:
            self.write_workbook(job_id, "original")
            self.write_workbook(job_id, "cleaned")
        except Exception:
            pass
        return self.public_job(job_id)

    def get(self, job_id):
        job = self._jobs.get(job_id)
        if job is None:
            raise KeyError("Upload session expired or was not found. Please upload the file again.")
        return job

    def list_jobs(self):
        cards = [self.job_card(job_id) for job_id in self._jobs]
        cards.sort(key=lambda item: item["updated_at"], reverse=True)
        counts = {"uploaded": 0, "processing": 0, "ready": 0, "error": 0}
        for card in cards:
            counts[card["status"]] = counts.get(card["status"], 0) + 1
        return {
            "jobs": cards,
            "counts": {
                "total": len(cards),
                "uploaded": counts["uploaded"],
                "processing": counts["processing"],
                "ready": counts["ready"],
                "error": counts["error"],
            },
        }

    def job_card(self, job_id):
        job = self.get(job_id)
        original = job["original"]
        cleaned = job["cleaned"]
        status = job["status"]
        next_action = "process"
        if status == "processing":
            next_action = "wait"
        elif status == "ready":
            next_action = "export"
        elif status == "error":
            next_action = "retry"
        return {
            "job_id": job_id,
            "source_name": job["source_name"],
            "status": status,
            "error": job.get("error"),
            "exported": bool(job.get("exported")),
            "created_at": job["created_at"],
            "updated_at": job["updated_at"],
            "original_rows": int(len(original)),
            "original_columns": int(original.shape[1]),
            "cleaned_rows": int(len(cleaned)),
            "cleaned_columns": int(cleaned.shape[1]),
            "applied": deepcopy(job["applied"]),
            "next_action": next_action,
        }

    def process(self, job_id, operations):
        job = self.get(job_id)
        if job["status"] == "processing":
            return self.job_card(job_id)
        job["status"] = "processing"
        job["error"] = None
        job["updated_at"] = utc_now()
        thread = threading.Thread(
            target=self._run_process,
            args=(job_id, operations or []),
            daemon=True,
        )
        thread.start()
        return self.job_card(job_id)

    def _run_process(self, job_id, operations):
        # Background worker: apply the user's chosen cleaning steps, then
        # write a cleaned Excel workbook so Explore / ServiceFunctions can open it.
        job = self.get(job_id)
        try:
            cleaned, applied = apply_operations(job["original"].copy(), operations)
            job["cleaned"] = cleaned
            job["applied"] = applied
            job["status"] = "ready"
            job["error"] = None
            self.write_workbook(job_id, "cleaned")
        except Exception as exc:
            job["status"] = "error"
            job["error"] = str(exc)
        job["updated_at"] = utc_now()

    def frame_for(self, job_id, source="cleaned"):
        """Pick the original upload or the cleaned sheet for inspect / paging."""
        job = self.get(job_id)
        if source == "original":
            return job["original"]
        return job["cleaned"]

    def write_workbook(self, job_id, source="cleaned"):
        """
        Save the current DataFrame as a real .xlsx file in uploads/.
        The dashboard 'Open Excel' button downloads this workbook.
        """
        job = self.get(job_id)
        frame = self.frame_for(job_id, source)
        path = os.path.join(self.upload_dir, f"{job_id}_{source}.xlsx")
        frame.to_excel(path, index=False)
        job[f"{source}_xlsx"] = path
        return path

    def workbook_bytes(self, job_id, source="cleaned"):
        """Return the Excel file for download, creating it if needed."""
        path = self.write_workbook(job_id, source)
        job = self.get(job_id)
        base_name = os.path.splitext(job["source_name"])[0]
        safe_name = re.sub(r"[^\w\-]+", "_", base_name).strip("_") or "dataset"
        from io import BytesIO
        with open(path, "rb") as handle:
            buffer = BytesIO(handle.read())
        buffer.seek(0)
        return buffer, f"{safe_name}_{source}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def get_record(self, job_id, source="cleaned", index=0):
        """
        One row at a time for the dashboard pager.
        index is 0-based and is clamped to the valid range.
        """
        frame = self.frame_for(job_id, source)
        total = int(len(frame))
        if total == 0:
            return {
                "index": 0,
                "total": 0,
                "record": {},
                "columns": [str(column) for column in frame.columns],
                "has_prev": False,
                "has_next": False,
                "source": source,
            }
        index = max(0, min(int(index), total - 1))
        row = _safe_records(frame.iloc[[index]])[0]
        return {
            "index": index,
            "total": total,
            "record": row,
            "columns": [str(column) for column in frame.columns],
            "has_prev": index > 0,
            "has_next": index < total - 1,
            "source": source,
        }

    def run_explore(self, job_id, source, method_id, params):
        """Run one ServiceFunctions inspect method against the chosen sheet."""
        from utils.explore import run_service_method
        frame = self.frame_for(job_id, source)
        return run_service_method(frame, method_id, params)

    def mark_exported(self, job_id):
        job = self.get(job_id)
        job["exported"] = True
        job["updated_at"] = utc_now()

    def delete(self, job_id):
        # Remove the job from memory and delete any files we created for it
        # (the original upload plus generated Excel workbooks).
        job = self.get(job_id)
        upload_dir = os.path.abspath(self.upload_dir)
        for key in ("path", "original_xlsx", "cleaned_xlsx"):
            path = job.get(key)
            if path and os.path.abspath(path).startswith(upload_dir) and os.path.isfile(path):
                os.remove(path)
        with self._lock:
            self._jobs.pop(job_id, None)

    def public_job(self, job_id, include_original=True):
        job = self.get(job_id)
        payload = {
            "job_id": job_id,
            "source_name": job["source_name"],
            "status": job["status"],
            "error": job.get("error"),
            "exported": bool(job.get("exported")),
            "created_at": job["created_at"],
            "updated_at": job["updated_at"],
            "applied": deepcopy(job["applied"]),
            "cleaned": summarize_frame(job["cleaned"], "cleaned"),
        }
        if include_original:
            payload["original"] = summarize_frame(job["original"], "original")
        return payload

    def export_bytes(self, job_id, export_format):
        job = self.get(job_id)
        frame = job["cleaned"]
        export_format = (export_format or "csv").lower()
        base_name = os.path.splitext(job["source_name"])[0]
        safe_name = re.sub(r"[^\w\-]+", "_", base_name).strip("_") or "cleaned_data"

        if export_format == "xlsx":
            from io import BytesIO
            buffer = BytesIO()
            frame.to_excel(buffer, index=False)
            buffer.seek(0)
            self.mark_exported(job_id)
            return buffer, f"{safe_name}_cleaned.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        from io import BytesIO
        buffer = BytesIO()
        frame.to_csv(buffer, index=False)
        buffer.seek(0)
        self.mark_exported(job_id)
        return buffer, f"{safe_name}_cleaned.csv", "text/csv"
