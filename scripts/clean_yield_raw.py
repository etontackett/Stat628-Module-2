#!/usr/bin/env python3
"""Check and clean cranberry yield raw data files.

Inputs:
- cranberry-data-group6/data_longterm/LTYielddata2024.csv
- cranberry-data-group6/data_acute/Acute HS-Yield_RawData 2024.xlsx

Outputs (under cleaned_data/):
- longterm_yield_clean.csv
- acute_yield_clean_all.csv
- acute_yield_clean.csv (A0/A0C removed)
- yield_cleaning_report.md
"""

from __future__ import annotations

import csv
import re
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "cranberry-data-group6"
OUT_DIR = ROOT / "cleaned_data"

LT_PATH = DATA_ROOT / "data_longterm" / "LTYielddata2024.csv"
ACUTE_PATH = DATA_ROOT / "data_acute" / "Acute HS-Yield_RawData 2024.xlsx"


NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


LONGTERM_SET_MAP = {
    ("St", 1): 7,
    ("St", 5): 7,
    ("St", 2): 8,
    ("St", 6): 8,
    ("St", 3): 9,
    ("St", 7): 9,
    ("St", 4): 10,
    ("St", 8): 10,
    ("MQ", 9): 11,
    ("MQ", 13): 11,
    ("MQ", 10): 12,
    ("MQ", 14): 12,
    ("MQ", 11): 13,
    ("MQ", 15): 13,
    ("MQ", 12): 14,
    ("MQ", 16): 14,
}

LONGTERM_PAIR_MAP = {
    ("St", 1): 5,
    ("St", 5): 1,
    ("St", 2): 6,
    ("St", 6): 2,
    ("St", 3): 7,
    ("St", 7): 3,
    ("St", 4): 8,
    ("St", 8): 4,
    ("MQ", 9): 13,
    ("MQ", 13): 9,
    ("MQ", 10): 14,
    ("MQ", 14): 10,
    ("MQ", 11): 15,
    ("MQ", 15): 11,
    ("MQ", 12): 16,
    ("MQ", 16): 12,
}


@dataclass
class CheckStats:
    rows: int = 0
    arithmetic_issues: int = 0
    missing_value_issues: int = 0
    duplicate_key_issues: int = 0
    pairing_issues: int = 0


def col_index(cell_ref: str) -> int | None:
    match = re.match(r"([A-Z]+)", cell_ref or "")
    if not match:
        return None
    value = 0
    for char in match.group(1):
        value = value * 26 + (ord(char) - 64)
    return value - 1


def parse_xlsx_sheet_rows(path: Path, sheet_name: str) -> list[list[str]]:
    with zipfile.ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", NS):
                text = "".join(t.text or "" for t in si.findall(".//a:t", NS))
                shared_strings.append(text)

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
            values: dict[int, str] = {}
            for cell in row.findall("a:c", NS):
                idx = col_index(cell.attrib.get("r", ""))
                if idx is None:
                    continue
                cell_type = cell.attrib.get("t")
                v = cell.find("a:v", NS)
                if v is None:
                    inline = cell.find("a:is/a:t", NS)
                    txt = inline.text if inline is not None else ""
                else:
                    txt = v.text or ""
                    if cell_type == "s":
                        try:
                            txt = shared_strings[int(txt)]
                        except (ValueError, IndexError):
                            pass
                values[idx] = txt
            if values:
                width = max(values) + 1
                rows.append([values.get(i, "") for i in range(width)])
        return rows


def to_float(value: str) -> float | None:
    text = (value or "").strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def normalize_cultivar(value: str) -> str:
    text = (value or "").strip()
    if text in {"Stevens", "ST", "St"}:
        return "St"
    if text in {"MQ", "Mullica Queen", "MullicaQueen", "Molluca Queen"}:
        return "MQ"
    return text


def pct(numer: float, denom: float) -> float | None:
    if denom == 0:
        return None
    return numer / denom


def write_csv(path: Path, rows: Iterable[dict[str, object]], columns: list[str]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def clean_longterm() -> tuple[list[dict[str, object]], CheckStats]:
    stats = CheckStats()
    rows: list[list[str]] = []
    with LT_PATH.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows.extend(reader)

    header_idx = next(
        i for i, r in enumerate(rows) if r and r[0].strip() == "Cultivar"
    )
    body = [r for r in rows[header_idx + 1 :] if len(r) >= 9 and r[0].strip()]

    cleaned: list[dict[str, object]] = []
    for source_row, row in enumerate(body, start=header_idx + 2):
        cultivar = normalize_cultivar(row[0])
        heat_trt = row[1].strip()
        plot_id = int(float(row[2]))

        rotten_count = to_float(row[3])
        rotten_weight_g = to_float(row[4])
        healthy_count = to_float(row[5])
        healthy_weight_g = to_float(row[6])
        total_count = to_float(row[7])
        total_weight_g = to_float(row[8])

        stats.rows += 1
        if None in [
            rotten_count,
            rotten_weight_g,
            healthy_count,
            healthy_weight_g,
            total_count,
            total_weight_g,
        ]:
            stats.missing_value_issues += 1
            continue

        if abs((rotten_count + healthy_count) - total_count) > 1e-6:
            stats.arithmetic_issues += 1
        if abs((rotten_weight_g + healthy_weight_g) - total_weight_g) > 0.05:
            stats.arithmetic_issues += 1

        set_id = LONGTERM_SET_MAP.get((cultivar, plot_id))
        pair_plot_id = LONGTERM_PAIR_MAP.get((cultivar, plot_id))
        is_control = 1 if heat_trt.lower() == "control" else 0

        cleaned.append(
            {
                "experiment": "longterm",
                "source_row": source_row,
                "cultivar": cultivar,
                "heat_trt": heat_trt,
                "is_control": is_control,
                "set_id": set_id,
                "plot_id": plot_id,
                "paired_plot_id": pair_plot_id,
                "rotten_count": int(rotten_count),
                "rotten_weight_g": rotten_weight_g,
                "healthy_count": int(healthy_count),
                "healthy_weight_g": healthy_weight_g,
                "total_count": int(total_count),
                "total_weight_g": total_weight_g,
                "pct_rotten_count": pct(rotten_count, total_count),
                "pct_rotten_weight": pct(rotten_weight_g, total_weight_g),
            }
        )

    key_counts = Counter((r["cultivar"], r["plot_id"]) for r in cleaned)
    stats.duplicate_key_issues = sum(c - 1 for c in key_counts.values() if c > 1)

    by_set = defaultdict(set)
    for r in cleaned:
        by_set[(r["cultivar"], r["set_id"])].add(r["is_control"])
    stats.pairing_issues = sum(1 for s in by_set.values() if s != {0, 1})

    cleaned.sort(key=lambda r: (r["cultivar"], r["plot_id"]))
    return cleaned, stats


def parse_acute_treatment(treatment: str) -> tuple[str, int]:
    """Return (heat_level, is_control) for acute treatment labels."""
    t = treatment.strip().upper()
    if t in {"A", "B", "C", "D", "A0"}:
        return t, 0
    if t in {"AC", "BC", "CC", "DC", "A0C"}:
        return t[:-1], 1
    if t.endswith("C") and len(t) > 1:
        return t[:-1], 1
    return t, 0


def clean_acute() -> tuple[list[dict[str, object]], list[dict[str, object]], CheckStats]:
    stats = CheckStats()
    all_rows = parse_xlsx_sheet_rows(ACUTE_PATH, "Acute Heat stress")
    header_idx = next(
        i
        for i, r in enumerate(all_rows)
        if len(r) > 3 and r[1].strip() == "Cultivar" and r[2].strip() == "Treatment"
    )
    body = [
        (i, r)
        for i, r in enumerate(all_rows[header_idx + 1 :], start=header_idx + 2)
        if len(r) >= 10 and r[1].strip() and r[2].strip() and r[3].strip()
    ]

    cleaned_all: list[dict[str, object]] = []
    for source_row, row in body:
        cultivar = normalize_cultivar(row[1])
        treatment_raw = row[2].strip()
        replicate = int(float(row[3]))

        rotten_count = to_float(row[4])
        rotten_weight_g = to_float(row[5])
        healthy_count = to_float(row[6])
        healthy_weight_g = to_float(row[7])
        total_count = to_float(row[8])
        total_weight_g = to_float(row[9])
        observations = row[10].strip() if len(row) > 10 else ""

        stats.rows += 1
        if None in [
            rotten_count,
            rotten_weight_g,
            healthy_count,
            healthy_weight_g,
            total_count,
            total_weight_g,
        ]:
            stats.missing_value_issues += 1
            continue

        if abs((rotten_count + healthy_count) - total_count) > 1e-6:
            stats.arithmetic_issues += 1
        if abs((rotten_weight_g + healthy_weight_g) - total_weight_g) > 0.05:
            stats.arithmetic_issues += 1

        heat_level, is_control = parse_acute_treatment(treatment_raw)

        cleaned_all.append(
            {
                "experiment": "acute",
                "source_row": source_row,
                "cultivar": cultivar,
                "treatment_raw": treatment_raw,
                "heat_level": heat_level,
                "is_control": is_control,
                "replicate": replicate,
                "rotten_count": int(rotten_count),
                "rotten_weight_g": rotten_weight_g,
                "healthy_count": int(healthy_count),
                "healthy_weight_g": healthy_weight_g,
                "total_count": int(total_count),
                "total_weight_g": total_weight_g,
                "pct_rotten_count": pct(rotten_count, total_count),
                "pct_rotten_weight": pct(rotten_weight_g, total_weight_g),
                "drop_a0": 1 if heat_level == "A0" else 0,
                "observations": observations,
            }
        )

    key_counts = Counter(
        (r["cultivar"], r["treatment_raw"], r["replicate"]) for r in cleaned_all
    )
    stats.duplicate_key_issues = sum(c - 1 for c in key_counts.values() if c > 1)

    pair_map: defaultdict[tuple[str, int, str], set[int]] = defaultdict(set)
    for r in cleaned_all:
        pair_map[(r["cultivar"], r["replicate"], r["heat_level"])].add(r["is_control"])
    stats.pairing_issues = sum(1 for s in pair_map.values() if s != {0, 1})

    cleaned_all.sort(key=lambda r: (r["cultivar"], r["heat_level"], r["replicate"], r["is_control"]))
    cleaned_no_a0 = [r for r in cleaned_all if r["drop_a0"] == 0]
    return cleaned_all, cleaned_no_a0, stats


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    lt_clean, lt_stats = clean_longterm()
    acute_all, acute_no_a0, acute_stats = clean_acute()

    lt_columns = [
        "experiment",
        "source_row",
        "cultivar",
        "heat_trt",
        "is_control",
        "set_id",
        "plot_id",
        "paired_plot_id",
        "rotten_count",
        "rotten_weight_g",
        "healthy_count",
        "healthy_weight_g",
        "total_count",
        "total_weight_g",
        "pct_rotten_count",
        "pct_rotten_weight",
    ]
    acute_columns = [
        "experiment",
        "source_row",
        "cultivar",
        "treatment_raw",
        "heat_level",
        "is_control",
        "replicate",
        "rotten_count",
        "rotten_weight_g",
        "healthy_count",
        "healthy_weight_g",
        "total_count",
        "total_weight_g",
        "pct_rotten_count",
        "pct_rotten_weight",
        "drop_a0",
        "observations",
    ]

    n_lt = write_csv(OUT_DIR / "longterm_yield_clean.csv", lt_clean, lt_columns)
    n_acute_all = write_csv(
        OUT_DIR / "acute_yield_clean_all.csv", acute_all, acute_columns
    )
    n_acute = write_csv(OUT_DIR / "acute_yield_clean.csv", acute_no_a0, acute_columns)

    report = OUT_DIR / "yield_cleaning_report.md"
    report.write_text(
        "\n".join(
            [
                "# Yield Raw Data: check and cleaning report",
                "",
                "## Input files",
                f"- {LT_PATH}",
                f"- {ACUTE_PATH}",
                "",
                "## Cleaning rules",
                "- Keep only data rows (remove title/header/blank rows).",
                "- Normalize cultivar labels to `St` and `MQ`.",
                "- Convert count/weight fields to numeric.",
                "- Validate arithmetic consistency:",
                "  - `rotten_count + healthy_count == total_count`",
                "  - `rotten_weight_g + healthy_weight_g ~= total_weight_g` (tolerance 0.05 g)",
                "- Derive `pct_rotten_count` and `pct_rotten_weight`.",
                "- Acute experiment: parse control status from treatment label suffix `C`.",
                "- Acute experiment: mark A0/A0C rows with `drop_a0=1` and provide a separate file with A0 removed.",
                "",
                "## Long-term yield checks",
                f"- Data rows processed: {lt_stats.rows}",
                f"- Missing value issues: {lt_stats.missing_value_issues}",
                f"- Arithmetic issues: {lt_stats.arithmetic_issues}",
                f"- Duplicate key issues (`cultivar+plot_id`): {lt_stats.duplicate_key_issues}",
                f"- Pairing issues by set (`OTC` + `Control`): {lt_stats.pairing_issues}",
                f"- Output rows: {n_lt}",
                "",
                "## Acute yield checks",
                f"- Data rows processed: {acute_stats.rows}",
                f"- Missing value issues: {acute_stats.missing_value_issues}",
                f"- Arithmetic issues: {acute_stats.arithmetic_issues}",
                f"- Duplicate key issues (`cultivar+treatment_raw+replicate`): {acute_stats.duplicate_key_issues}",
                f"- Pairing issues (`cultivar+replicate+heat_level` requires treatment+control): {acute_stats.pairing_issues}",
                f"- Output rows (`acute_yield_clean_all.csv`): {n_acute_all}",
                f"- Output rows (`acute_yield_clean.csv`, A0 removed): {n_acute}",
                "",
                "## Output files",
                f"- {OUT_DIR / 'longterm_yield_clean.csv'}",
                f"- {OUT_DIR / 'acute_yield_clean_all.csv'}",
                f"- {OUT_DIR / 'acute_yield_clean.csv'}",
                f"- {report}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote: {OUT_DIR / 'longterm_yield_clean.csv'} ({n_lt} rows)")
    print(f"Wrote: {OUT_DIR / 'acute_yield_clean_all.csv'} ({n_acute_all} rows)")
    print(f"Wrote: {OUT_DIR / 'acute_yield_clean.csv'} ({n_acute} rows)")
    print(f"Wrote: {report}")


if __name__ == "__main__":
    main()
