"""
Dashboard explorer: run ServiceFunctions inspect methods on a job's data.

The UI calls these by method id. Each entry maps to a ServiceFunctions helper
so you can open a sheet and inspect shape, head/tail, unique values, counts,
grouping, sorting, combined columns, or a column median.
"""

import math

import numpy as np
import pandas as pd

from ServiceFunctions import ServiceFunctions

# Catalog shown in the Explore dropdown. `needs` tells the UI which inputs to show.
EXPLORE_METHODS = [
    {
        "id": "shape",
        "label": "Shape (rows × columns)",
        "service_method": "frame_shape",
        "needs": [],
        "description": "Calls ServiceFunctions.frame_shape — same idea as get_data_set_shape.",
    },
    {
        "id": "columns",
        "label": "Column names and types",
        "service_method": "frame_columns",
        "needs": [],
        "description": "Calls ServiceFunctions.frame_columns — same idea as get_column_info.",
    },
    {
        "id": "head",
        "label": "First N rows",
        "service_method": "frame_head",
        "needs": ["n"],
        "description": "Calls ServiceFunctions.frame_head — same idea as get_head_data_info.",
    },
    {
        "id": "tail",
        "label": "Last N rows",
        "service_method": "frame_tail",
        "needs": ["n"],
        "description": "Calls ServiceFunctions.frame_tail — same idea as get_tail_data_info.",
    },
    {
        "id": "unique_values",
        "label": "Unique values in a column",
        "service_method": "frame_unique_values",
        "needs": ["column"],
        "description": "Calls ServiceFunctions.frame_unique_values.",
    },
    {
        "id": "value_counts",
        "label": "Value counts for a column",
        "service_method": "frame_value_counts",
        "needs": ["column"],
        "description": "Calls ServiceFunctions.frame_value_counts.",
    },
    {
        "id": "group_count",
        "label": "Group by one column and count",
        "service_method": "frame_group_count",
        "needs": ["column"],
        "description": "Calls ServiceFunctions.frame_group_count.",
    },
    {
        "id": "group_count_two",
        "label": "Group by two columns and count",
        "service_method": "frame_group_count_two",
        "needs": ["column", "column2"],
        "description": "Calls ServiceFunctions.frame_group_count_two.",
    },
    {
        "id": "sort",
        "label": "Sort by a column",
        "service_method": "frame_sort",
        "needs": ["column", "ascending"],
        "description": "Calls ServiceFunctions.frame_sort — same idea as ordering_data.",
    },
    {
        "id": "combine_columns",
        "label": "Combine two columns",
        "service_method": "frame_combine_columns",
        "needs": ["column", "column2"],
        "description": "Calls ServiceFunctions.frame_combine_columns.",
    },
    {
        "id": "median",
        "label": "Median of a numeric column",
        "service_method": "frame_median",
        "needs": ["column"],
        "description": "Calls ServiceFunctions.frame_median.",
    },
]

_METHODS_BY_ID = {item["id"]: item for item in EXPLORE_METHODS}


def _json_safe(value):
    """Turn numpy / pandas values into JSON-friendly Python types."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if math.isnan(value) or math.isinf(value):
            return None
        return float(value)
    if hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except (ValueError, AttributeError):
            pass
    return value


def serialize_result(result):
    """
    Convert whatever ServiceFunctions returned into a dashboard-friendly payload.
    kind tells the UI how to render: table, pairs, list, stats, or value.
    """
    if isinstance(result, pd.DataFrame):
        records = []
        for row in result.to_dict("records"):
            records.append({str(key): _json_safe(value) for key, value in row.items()})
        return {
            "kind": "table",
            "columns": [str(column) for column in result.columns],
            "rows": records,
            "count": len(records),
        }

    if isinstance(result, pd.Series):
        pairs = []
        for key, value in result.items():
            if isinstance(key, tuple):
                key = " | ".join(str(part) for part in key)
            pairs.append({"label": str(key), "value": _json_safe(value)})
        return {"kind": "pairs", "items": pairs, "count": len(pairs)}

    if isinstance(result, (list, tuple, np.ndarray, pd.Index)):
        if isinstance(result, tuple) and len(result) == 2 and all(isinstance(part, (int, np.integer)) for part in result):
            return {
                "kind": "stats",
                "rows": int(result[0]),
                "columns": int(result[1]),
            }
        values = [_json_safe(item) for item in list(result)]
        return {"kind": "list", "items": values, "count": len(values)}

    if isinstance(result, dict):
        return {"kind": "object", "data": result}

    return {"kind": "value", "value": _json_safe(result)}


def run_service_method(frame, method_id, params=None):
    """Look up a catalog method and call the matching ServiceFunctions helper."""
    spec = _METHODS_BY_ID.get(method_id)
    if spec is None:
        raise ValueError(f"Unknown inspect method: {method_id}")

    params = params or {}
    helper = getattr(ServiceFunctions, spec["service_method"])
    needs = spec["needs"]

    if "n" in needs:
        result = helper(frame, params.get("n", 10))
    elif needs == ["column", "column2"]:
        result = helper(frame, params.get("column"), params.get("column2"))
    elif needs == ["column", "ascending"]:
        result = helper(frame, params.get("column"), params.get("ascending", True))
    elif needs == ["column"]:
        result = helper(frame, params.get("column"))
    else:
        result = helper(frame)

    payload = serialize_result(result)
    payload["method"] = method_id
    payload["label"] = spec["label"]
    payload["service_method"] = spec["service_method"]
    return payload
