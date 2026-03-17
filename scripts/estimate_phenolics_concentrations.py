#!/usr/bin/env python3
"""Estimate gallic acid concentrations from phenolics absorbance data.

Rules implemented from assignment:
1) For each (Date, rep), fit absorbance = m * concentration + b using standards.
2) For each non-standard sample: concentration_diluted = (absorbance - b) / m.
3) Multiply diluted concentration by 10 for undiluted juice concentration.
4) Output one row per non-standard sample in wide format with 3 concentration columns.
"""

from __future__ import annotations

import csv
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RAW_XLSX = (
    ROOT / "cranberry-data-group6" / "data_mixed" / "Phenolics_RawData.xlsx"
)
OUT_CSV = ROOT / "Phenolics_concentrations.csv"
SUMMARY_CSV = ROOT / "cleaned_data" / "phenolics_calibration_summary.csv"
REPORT_MD = ROOT / "cleaned_data" / "phenolics_concentrations_report.md"

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

STD_RE = re.compile(r"(?i)^std\d+$")


def col_index(cell_ref: str) -> int | None:
    m = re.match(r"([A-Z]+)", cell_ref or "")
    if not m:
        return None
    out = 0
    for ch in m.group(1):
        out = out * 26 + ord(ch) - 64
    return out - 1


def parse_sheet_rows(path: Path, sheet_name: str) -> list[list[str]]:
    with zipfile.ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", NS):
                txt = "".join(t.text or "" for t in si.findall(".//a:t", NS))
                shared_strings.append(txt)

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {
            node.attrib["Id"]: node.attrib["Target"]
            for node in rels.findall(
                "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
            )
        }

        target = None
        for sheet in workbook.findall("a:sheets/a:sheet", NS):
            if sheet.attrib["name"] == sheet_name:
                rid = sheet.attrib[
                    "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
                ]
                target = "xl/" + rel_map[rid]
                break
        if target is None:
            raise ValueError(f"Sheet not found: {sheet_name}")

        worksheet = ET.fromstring(archive.read(target))
        rows: list[list[str]] = []
        for row in worksheet.findall(".//a:sheetData/a:row", NS):
            vals: dict[int, str] = {}
            for cell in row.findall("a:c", NS):
                idx = col_index(cell.attrib.get("r", ""))
                if idx is None:
                    continue
                ctype = cell.attrib.get("t")
                v = cell.find("a:v", NS)
                if v is None:
                    inline = cell.find("a:is/a:t", NS)
                    txt = inline.text if inline is not None else ""
                else:
                    txt = v.text or ""
                    if ctype == "s":
                        try:
                            txt = shared_strings[int(txt)]
                        except (ValueError, IndexError):
                            pass
                vals[idx] = txt
            if vals:
                width = max(vals) + 1
                rows.append([vals.get(i, "") for i in range(width)])
        return rows


def as_float(value: str) -> float | None:
    text = (value or "").strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def main() -> None:
    rows = parse_sheet_rows(RAW_XLSX, "Absorbance Data")
    header = rows[0]
    body = [r for r in rows[1:] if len(r) >= 6 and r[1].strip()]

    # Build calibration lines by (Date, rep_idx), where rep_idx in {0,1,2}.
    calibration: dict[tuple[str, int], tuple[float, float]] = {}
    calibration_rows: list[dict[str, object]] = []
    for rep_idx in range(3):
        grouped: dict[str, list[tuple[float, float]]] = {}
        for r in body:
            sample_id = r[1].strip()
            if not STD_RE.match(sample_id):
                continue
            date = r[0].strip()
            x = as_float(r[2])  # Tube# for standards = true concentration
            y = as_float(r[3 + rep_idx])  # absorbance for current rep
            if x is None or y is None:
                continue
            grouped.setdefault(date, []).append((x, y))

        for date, pts in grouped.items():
            if len(pts) < 2:
                calibration[(date, rep_idx)] = (np.nan, np.nan)
                calibration_rows.append(
                    {
                        "Date": date,
                        "replicate": rep_idx + 1,
                        "n_standards": len(pts),
                        "slope_m": np.nan,
                        "intercept_b": np.nan,
                    }
                )
                continue
            xs = np.array([p[0] for p in pts], dtype=float)
            ys = np.array([p[1] for p in pts], dtype=float)
            m, b = np.polyfit(xs, ys, 1)
            calibration[(date, rep_idx)] = (float(m), float(b))
            calibration_rows.append(
                {
                    "Date": date,
                    "replicate": rep_idx + 1,
                    "n_standards": len(pts),
                    "slope_m": float(m),
                    "intercept_b": float(b),
                }
            )

    # Create output rows for non-standard samples only.
    out_rows: list[dict[str, object]] = []
    missing_calibration = 0
    for r in body:
        sample_id = r[1].strip()
        if STD_RE.match(sample_id):
            continue

        date = r[0].strip()
        out = {"Date": date, "Sample ID": sample_id, "Tube#": r[2].strip()}
        for rep_idx in range(3):
            m, b = calibration.get((date, rep_idx), (np.nan, np.nan))
            absorbance = as_float(r[3 + rep_idx])
            if absorbance is None or not np.isfinite(m) or m == 0:
                conc = np.nan
                if not np.isfinite(m) or m == 0:
                    missing_calibration += 1
            else:
                conc = ((absorbance - b) / m) * 10.0
            out[f"concentration_rep{rep_idx + 1}"] = conc
        out_rows.append(out)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Date",
                "Sample ID",
                "Tube#",
                "concentration_rep1",
                "concentration_rep2",
                "concentration_rep3",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Date", "replicate", "n_standards", "slope_m", "intercept_b"],
        )
        writer.writeheader()
        writer.writerows(calibration_rows)

    n_non_standard = len(out_rows)
    n_dates = len({r["Date"] for r in calibration_rows})
    n_cal_lines = len(calibration_rows)
    n_nan = sum(
        int(np.isnan(r[k]))
        for r in out_rows
        for k in ("concentration_rep1", "concentration_rep2", "concentration_rep3")
    )

    report_lines = [
        "# Phenolics Concentration Estimation Report",
        "",
        "Method: for each `Date x rep`, fit `absorbance = m * concentration + b` on standards,",
        "then estimate non-standard concentration by `((absorbance - b) / m) * 10`.",
        "",
        f"- Input: {RAW_XLSX}",
        f"- Output concentration file: {OUT_CSV}",
        f"- Calibration summary: {SUMMARY_CSV}",
        f"- Non-standard sample rows written: {n_non_standard}",
        f"- Dates with calibrations: {n_dates}",
        f"- Calibration lines fit: {n_cal_lines}",
        f"- Missing/NaN concentration cells: {n_nan}",
        f"- Missing-calibration encounters: {missing_calibration}",
        "",
        "Columns in output:",
        "- Date, Sample ID, Tube#, concentration_rep1, concentration_rep2, concentration_rep3",
        "",
    ]
    REPORT_MD.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"Wrote: {OUT_CSV} ({n_non_standard} rows)")
    print(f"Wrote: {SUMMARY_CSV} ({n_cal_lines} rows)")
    print(f"Wrote: {REPORT_MD}")
    print(f"NaN concentration cells: {n_nan}")


if __name__ == "__main__":
    main()
