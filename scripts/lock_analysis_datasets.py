#!/usr/bin/env python3
"""Create locked analysis-ready datasets from cleaned yield + sensor flags."""

from __future__ import annotations

import csv
import hashlib
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "cleaned_data"

LT_CLEAN = CLEAN_DIR / "longterm_yield_clean.csv"
ACUTE_CLEAN = CLEAN_DIR / "acute_yield_clean.csv"  # A0/A0C already removed
LT_FLAGS = CLEAN_DIR / "yield_sensor_flags_longterm.csv"
ACUTE_FLAGS = CLEAN_DIR / "yield_sensor_flags_acute.csv"

LT_LOCKED = CLEAN_DIR / "longterm_yield_analysis_locked.csv"
ACUTE_LOCKED = CLEAN_DIR / "acute_yield_analysis_locked.csv"
MANIFEST = CLEAN_DIR / "analysis_dataset_manifest.md"

LOCK_VERSION = "v1_2026-03-05"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    lt_clean_rows = read_csv(LT_CLEAN)
    acute_clean_rows = read_csv(ACUTE_CLEAN)
    lt_flag_rows = read_csv(LT_FLAGS)
    acute_flag_rows = read_csv(ACUTE_FLAGS)

    lt_flags = {
        (r["cultivar"], r["heat_trt"], r["plot_id"]): r for r in lt_flag_rows
    }
    acute_flags = {
        (r["cultivar"], r["treatment_raw"], r["replicate"]): r for r in acute_flag_rows
    }

    lt_locked_rows: list[dict[str, str]] = []
    for row in lt_clean_rows:
        key = (row["cultivar"], row["heat_trt"], row["plot_id"])
        flags = lt_flags.get(key)
        if flags is None:
            raise KeyError(f"Missing long-term flags for key={key}")
        out = dict(row)
        out["include_in_yield_model"] = "1"
        out["include_in_temp_model"] = flags["temp_model_usable"]
        out["sensor_missing_overview"] = flags["missing_overview"]
        out["sensor_missing_files"] = flags["missing_files"]
        out["dataset_lock_version"] = LOCK_VERSION
        lt_locked_rows.append(out)

    acute_locked_rows: list[dict[str, str]] = []
    for row in acute_clean_rows:
        key = (row["cultivar"], row["treatment_raw"], row["replicate"])
        flags = acute_flags.get(key)
        if flags is None:
            raise KeyError(f"Missing acute flags for key={key}")
        out = dict(row)
        out["include_in_yield_model"] = "1"
        out["include_in_temp_model"] = flags["temp_model_usable"]
        out["sensor_missing_overview"] = flags["missing_overview"]
        out["sensor_missing_files"] = flags["missing_files"]
        out["sensor_missing_window"] = flags["missing_window"]
        out["dataset_lock_version"] = LOCK_VERSION
        acute_locked_rows.append(out)

    lt_columns = (
        list(lt_clean_rows[0].keys())
        + [
            "include_in_yield_model",
            "include_in_temp_model",
            "sensor_missing_overview",
            "sensor_missing_files",
            "dataset_lock_version",
        ]
    )
    acute_columns = (
        list(acute_clean_rows[0].keys())
        + [
            "include_in_yield_model",
            "include_in_temp_model",
            "sensor_missing_overview",
            "sensor_missing_files",
            "sensor_missing_window",
            "dataset_lock_version",
        ]
    )

    write_csv(LT_LOCKED, lt_locked_rows, lt_columns)
    write_csv(ACUTE_LOCKED, acute_locked_rows, acute_columns)

    lt_temp_usable = sum(int(r["include_in_temp_model"]) for r in lt_locked_rows)
    acute_temp_usable = sum(int(r["include_in_temp_model"]) for r in acute_locked_rows)

    manifest_lines = [
        "# Analysis Dataset Manifest",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Lock version: `{LOCK_VERSION}`",
        "",
        "## Inputs",
        f"- {LT_CLEAN}",
        f"- {ACUTE_CLEAN}",
        f"- {LT_FLAGS}",
        f"- {ACUTE_FLAGS}",
        "",
        "## Locked outputs",
        f"- {LT_LOCKED}",
        f"- rows: {len(lt_locked_rows)}",
        f"- include_in_yield_model=1 rows: {len(lt_locked_rows)}",
        f"- include_in_temp_model=1 rows: {lt_temp_usable}",
        f"- sha256: `{file_sha256(LT_LOCKED)}`",
        "",
        f"- {ACUTE_LOCKED}",
        f"- rows: {len(acute_locked_rows)}",
        f"- include_in_yield_model=1 rows: {len(acute_locked_rows)}",
        f"- include_in_temp_model=1 rows: {acute_temp_usable}",
        f"- sha256: `{file_sha256(ACUTE_LOCKED)}`",
        "",
        "## Notes",
        "- `acute_yield_clean.csv` already excludes A0/A0C.",
        "- `include_in_yield_model` keeps all rows in these locked files.",
        "- `include_in_temp_model` excludes rows with sensor mapping/file/window issues.",
        "",
    ]
    MANIFEST.write_text("\n".join(manifest_lines), encoding="utf-8")

    print(f"Wrote: {LT_LOCKED} ({len(lt_locked_rows)} rows)")
    print(f"Wrote: {ACUTE_LOCKED} ({len(acute_locked_rows)} rows)")
    print(f"Wrote: {MANIFEST}")


if __name__ == "__main__":
    main()
