#!/usr/bin/env python3
"""Cross-check yield rows against 4-channel and HOBO sensor data."""

from __future__ import annotations

import csv
import datetime as dt
import re
import zipfile
import xml.etree.ElementTree as ET
from bisect import bisect_left
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "cranberry-data-group6"
OUT_DIR = ROOT / "cleaned_data"

OVERVIEW_PATH = DATA_ROOT / "data_mixed" / "Listofdates_HeatStressTreatments2024.xlsx"
LT_YIELD_CLEAN = OUT_DIR / "longterm_yield_clean.csv"
ACUTE_YIELD_CLEAN_ALL = OUT_DIR / "acute_yield_clean_all.csv"
ACUTE_YIELD_CLEAN = OUT_DIR / "acute_yield_clean.csv"

ACUTE_4CH_DIR = DATA_ROOT / "data_acute" / "4 Channel Sensors"
ACUTE_HOBO_DIR = DATA_ROOT / "data_acute" / "HOBO RH Sensors"
LT_4CH_DIR = DATA_ROOT / "data_longterm" / "4 Channel Sensors"
LT_HOBO_DIR = DATA_ROOT / "data_longterm" / "HOBO Sensors"

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

# Deterministic aliases for known naming inconsistencies in overview metadata.
FILENAME_ALIASES: dict[tuple[str, str], dict[str, str]] = {
    ("Acute", "4 channel"): {
        "set2acute20240807": "set2acute20240807a",
        "set6acute20240807": "set6acute20240807a",
    },
    ("LongTerm", "HOBO sensor"): {
        "3202400618": "320240618",
    },
}


@dataclass(frozen=True)
class OverviewRow:
    stress_type: str
    test: str
    cultivar: str
    sensor: str
    plot: str
    experiment_date: str
    start_raw: str
    end_raw: str
    file_name: str
    channel_var: str


def norm_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())


def norm_cultivar(value: str) -> str:
    text = (value or "").strip()
    lower = text.lower()
    if lower.startswith("st") or lower.startswith("stev"):
        return "St"
    if text.upper() == "MQ" or "mul" in lower or "moll" in lower:
        return "MQ"
    return text


def parse_plot(plot: str) -> tuple[str, int] | None:
    m = re.match(r"\s*(otc|control)\s*([0-9]+)\s*$", (plot or "").strip(), re.I)
    if not m:
        return None
    return m.group(1).capitalize(), int(m.group(2))


def parse_excel_time_fraction(value: str) -> dt.time | None:
    value = (value or "").strip()
    if value == "":
        return None
    try:
        frac = float(value)
    except ValueError:
        return None
    seconds = round(frac * 24 * 3600)
    seconds = max(0, min(seconds, 24 * 3600 - 1))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return dt.time(h, m, s)


def parse_yyyymmdd(value: str) -> dt.date | None:
    digits = re.sub(r"[^0-9]", "", (value or ""))
    if len(digits) != 8:
        return None
    try:
        return dt.date(int(digits[0:4]), int(digits[4:6]), int(digits[6:8]))
    except ValueError:
        return None


def acute_expected_tests(heat_level: str) -> list[str]:
    heat_level = heat_level.upper()
    if heat_level == "A0":
        return ["A0"]
    if heat_level == "A":
        return ["A1", "A2", "A3", "A4"]
    if heat_level == "B":
        return ["B1", "B2", "B3"]
    if heat_level == "C":
        return ["C1", "C2"]
    if heat_level == "D":
        return ["D1"]
    return []


def col_index(cell_ref: str) -> int | None:
    m = re.match(r"([A-Z]+)", cell_ref or "")
    if not m:
        return None
    out = 0
    for ch in m.group(1):
        out = out * 26 + ord(ch) - 64
    return out - 1


def parse_xlsx_sheet_rows(path: Path, sheet_name: str) -> list[list[str]]:
    with zipfile.ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in root.findall("a:si", NS):
                shared_strings.append(
                    "".join(t.text or "" for t in si.findall(".//a:t", NS))
                )

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
                vals[idx] = txt
            if vals:
                width = max(vals) + 1
                rows.append([vals.get(i, "") for i in range(width)])
        return rows


def read_overview_rows() -> list[OverviewRow]:
    rows = parse_xlsx_sheet_rows(OVERVIEW_PATH, "Heat stress")
    body = [r for r in rows[1:] if len(r) >= 10 and r[0].strip()]
    return [
        OverviewRow(
            stress_type=r[0].strip(),
            test=r[1].strip(),
            cultivar=norm_cultivar(r[2].strip()),
            sensor=r[3].strip(),
            plot=r[4].strip(),
            experiment_date=r[5].strip(),
            start_raw=r[6].strip(),
            end_raw=r[7].strip(),
            file_name=r[8].strip(),
            channel_var=r[9].strip(),
        )
        for r in body
    ]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def resolve_file_path(
    stress_type: str,
    sensor: str,
    file_name: str,
    file_lookup: dict[str, Path],
) -> tuple[Path | None, str]:
    """Resolve overview file reference to an existing path.

    Returns:
        (path, status), where status in {"exact", "alias", "unresolved"}.
    """
    norm_ref = norm_text(file_name)
    if norm_ref in file_lookup:
        return file_lookup[norm_ref], "exact"

    alias_map = FILENAME_ALIASES.get((stress_type, sensor), {})
    alias_target = alias_map.get(norm_ref)
    if alias_target is not None and alias_target in file_lookup:
        return file_lookup[alias_target], "alias"

    # Common typo: extra 0 in YYYYMMDD chunk (e.g., 202400618 -> 20240618).
    if "202400" in norm_ref:
        typo_fixed = norm_ref.replace("202400", "20240")
        if typo_fixed in file_lookup:
            return file_lookup[typo_fixed], "alias"

    # Safe heuristic: if only one file extends the reference with 1-2 suffix chars,
    # treat it as a naming typo (e.g., Set2_Acute20240807 -> Set2_Acute20240807a).
    candidates = [
        key
        for key in file_lookup
        if key.startswith(norm_ref) and 1 <= (len(key) - len(norm_ref)) <= 2
    ]
    if len(candidates) == 1:
        return file_lookup[candidates[0]], "alias"

    return None, "unresolved"


def parse_sensor_timestamps(path: Path, sensor_kind: str) -> list[dt.datetime]:
    # sensor_kind in {"acute_4ch", "acute_hobo"}
    timestamps: list[dt.datetime] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header_skipped = False
        for row in reader:
            if not row:
                continue
            if not header_skipped:
                # First non-empty row is metadata/header label.
                header_skipped = True
                continue

            if sensor_kind == "acute_4ch":
                # 2nd column looks like 07/10/24 12:30:00 PM
                if len(row) < 2:
                    continue
                text = row[1].strip()
                if text == "":
                    continue
                try:
                    ts = dt.datetime.strptime(text, "%m/%d/%y %I:%M:%S %p")
                except ValueError:
                    continue
                timestamps.append(ts)
            else:
                # 2nd column looks like 07/10/2024 12:00:00
                if len(row) < 2:
                    continue
                text = row[1].strip()
                if text == "":
                    continue
                try:
                    ts = dt.datetime.strptime(text, "%m/%d/%Y %H:%M:%S")
                except ValueError:
                    continue
                timestamps.append(ts)
    return timestamps


def check_acute_window_has_data(
    timestamps: list[dt.datetime],
    date_str: str,
    start_raw: str,
    end_raw: str,
) -> bool:
    day = parse_yyyymmdd(date_str)
    t_start = parse_excel_time_fraction(start_raw)
    t_end = parse_excel_time_fraction(end_raw)
    if day is None or t_start is None or t_end is None:
        return False
    dt_start = dt.datetime.combine(day, t_start)
    dt_end = dt.datetime.combine(day, t_end)
    if dt_end < dt_start:
        dt_end = dt_end + dt.timedelta(days=1)

    if not timestamps:
        return False
    idx = bisect_left(timestamps, dt_start)
    if idx < len(timestamps) and timestamps[idx] <= dt_end:
        return True
    return False


def main() -> None:
    if not LT_YIELD_CLEAN.exists() or not ACUTE_YIELD_CLEAN_ALL.exists():
        raise FileNotFoundError("Run scripts/clean_yield_raw.py first.")

    overview = read_overview_rows()
    lt_rows = read_csv_rows(LT_YIELD_CLEAN)
    acute_rows_all = read_csv_rows(ACUTE_YIELD_CLEAN_ALL)
    acute_rows_no_a0 = read_csv_rows(ACUTE_YIELD_CLEAN)

    file_index = {
        ("Acute", "4 channel"): {
            norm_text(p.stem): p for p in ACUTE_4CH_DIR.glob("*.csv")
        },
        ("Acute", "HOBO sensor"): {
            norm_text(p.stem): p for p in ACUTE_HOBO_DIR.glob("*.csv")
        },
        ("LongTerm", "4 channel"): {
            norm_text(p.stem): p for p in LT_4CH_DIR.glob("*.csv")
        },
        ("LongTerm", "HOBO sensor"): {
            norm_text(p.stem): p for p in LT_HOBO_DIR.glob("*.csv")
        },
    }

    # Keep only rows associated with 2024 data.
    ov_2024 = [
        r
        for r in overview
        if r.experiment_date.startswith("2024") or ("2024" in r.file_name)
    ]

    lt_lookup: dict[tuple[str, str], list[OverviewRow]] = defaultdict(list)
    acute_lookup: dict[tuple[str, str, str, str], list[OverviewRow]] = defaultdict(list)
    for r in ov_2024:
        if r.stress_type == "LongTerm":
            # LongTerm cultivar column in overview has known inconsistencies.
            lt_lookup[(r.sensor, norm_text(r.plot))].append(r)
        elif r.stress_type == "Acute":
            acute_lookup[(r.cultivar, r.test, r.sensor, norm_text(r.plot))].append(r)

    timestamp_cache: dict[tuple[str, Path], list[dt.datetime]] = {}

    def get_timestamps(sensor_kind: str, path: Path) -> list[dt.datetime]:
        key = (sensor_kind, path)
        if key not in timestamp_cache:
            vals = parse_sensor_timestamps(path, sensor_kind)
            vals.sort()
            timestamp_cache[key] = vals
        return timestamp_cache[key]

    # 1) Long-term: each yield row should map to both sensors in overview with existing files.
    lt_missing_overview: list[str] = []
    lt_missing_files: list[str] = []
    lt_row_flags: dict[tuple[str, str, int], dict[str, int | str]] = {}
    for row in lt_rows:
        cultivar = row["cultivar"]
        plot_id = int(row["plot_id"])
        is_control = int(row["is_control"])
        heat_trt = row["heat_trt"]
        lt_key = (cultivar, heat_trt, plot_id)
        lt_row_flags[lt_key] = {
            "source_row": row.get("source_row", ""),
            "missing_overview": 0,
            "missing_files": 0,
        }
        plot_label = f"{'Control' if is_control else 'OTC'}{plot_id}"
        for sensor in ("4 channel", "HOBO sensor"):
            hits = lt_lookup.get((sensor, norm_text(plot_label)), [])
            if not hits:
                lt_missing_overview.append(
                    f"{cultivar} plot {plot_label} missing overview rows for {sensor}"
                )
                lt_row_flags[lt_key]["missing_overview"] = 1
                continue
            idx = file_index[("LongTerm", sensor)]
            existing = 0
            for h in hits:
                resolved_path, _ = resolve_file_path(
                    h.stress_type, h.sensor, h.file_name, idx
                )
                if resolved_path is not None:
                    existing += 1
            if existing == 0:
                lt_missing_files.append(
                    f"{cultivar} plot {plot_label} overview has {sensor} rows but referenced files not found"
                )
                lt_row_flags[lt_key]["missing_files"] = 1

    # 2) Acute: each yield row should have expected pulses and both sensors with existing files.
    acute_missing_overview: list[str] = []
    acute_missing_files: list[str] = []
    acute_missing_window_data: list[str] = []
    acute_row_flags: dict[tuple[str, str, int], dict[str, int | str]] = {}

    for row in acute_rows_all:
        cultivar = row["cultivar"]
        treatment_raw = row["treatment_raw"]
        heat_level = row["heat_level"]
        rep = int(row["replicate"])
        is_control = int(row["is_control"])
        acute_key = (cultivar, treatment_raw, rep)
        acute_row_flags[acute_key] = {
            "source_row": row.get("source_row", ""),
            "missing_overview": 0,
            "missing_files": 0,
            "missing_window": 0,
        }
        plot_label = f"{'Control' if is_control else 'OTC'} {rep}"
        expected_tests = acute_expected_tests(heat_level)
        for test in expected_tests:
            for sensor in ("4 channel", "HOBO sensor"):
                hits = acute_lookup.get((cultivar, test, sensor, norm_text(plot_label)), [])
                if not hits:
                    acute_missing_overview.append(
                        f"{cultivar} {treatment_raw} rep{rep}: missing overview ({test}, {sensor}, {plot_label})"
                    )
                    acute_row_flags[acute_key]["missing_overview"] = 1
                    continue

                idx = file_index[("Acute", sensor)]
                sensor_kind = "acute_4ch" if sensor == "4 channel" else "acute_hobo"
                found_file = False
                has_window_data = False
                for h in hits:
                    p, _ = resolve_file_path(h.stress_type, h.sensor, h.file_name, idx)
                    if p is None:
                        continue
                    found_file = True
                    if check_acute_window_has_data(
                        get_timestamps(sensor_kind, p),
                        h.experiment_date,
                        h.start_raw,
                        h.end_raw,
                    ):
                        has_window_data = True
                if not found_file:
                    acute_missing_files.append(
                        f"{cultivar} {treatment_raw} rep{rep}: {test} {sensor} file not found"
                    )
                    acute_row_flags[acute_key]["missing_files"] = 1
                elif not has_window_data:
                    acute_missing_window_data.append(
                        f"{cultivar} {treatment_raw} rep{rep}: {test} {sensor} has no records inside window"
                    )
                    acute_row_flags[acute_key]["missing_window"] = 1

    # 3) Sensor-overview anomalies that explain gaps.
    anomaly_rows = []
    for r in ov_2024:
        if r.stress_type == "Acute":
            parsed = parse_plot(r.plot)
            if parsed is None:
                anomaly_rows.append(
                    f"Acute invalid plot label: test={r.test} cultivar={r.cultivar} plot={r.plot}"
                )
            else:
                _, num = parsed
                if num not in {1, 2, 3}:
                    anomaly_rows.append(
                        f"Acute unexpected plot index: test={r.test} cultivar={r.cultivar} plot={r.plot}"
                    )

    # 4) Count file references that don't exist.
    missing_file_refs = []
    resolution_status_counts = {"exact": 0, "alias": 0, "unresolved": 0}
    resolution_csv_rows: list[dict[str, str]] = []
    seen_file_refs: set[tuple[str, str, str]] = set()
    for r in ov_2024:
        key = (r.stress_type, r.sensor)
        idx = file_index.get(key)
        if idx is None:
            continue
        resolved_path, status = resolve_file_path(
            r.stress_type, r.sensor, r.file_name, idx
        )
        resolution_status_counts[status] += 1
        ref_key = (r.stress_type, r.sensor, r.file_name)
        if ref_key not in seen_file_refs:
            seen_file_refs.add(ref_key)
            resolution_csv_rows.append(
                {
                    "stress_type": r.stress_type,
                    "sensor": r.sensor,
                    "overview_file_ref": r.file_name,
                    "resolution_status": status,
                    "resolved_file_stem": resolved_path.stem if resolved_path else "",
                }
            )
        if resolved_path is None:
            missing_file_refs.append(
                f"{r.stress_type} | {r.sensor} | cultivar={r.cultivar} | test={r.test or '-'} | "
                f"plot={r.plot} | file={r.file_name}"
            )

    # Deduplicate lists while preserving order.
    def dedup(items: list[str]) -> list[str]:
        seen = set()
        out = []
        for x in items:
            if x in seen:
                continue
            seen.add(x)
            out.append(x)
        return out

    lt_missing_overview = dedup(lt_missing_overview)
    lt_missing_files = dedup(lt_missing_files)
    acute_missing_overview = dedup(acute_missing_overview)
    acute_missing_files = dedup(acute_missing_files)
    acute_missing_window_data = dedup(acute_missing_window_data)
    anomaly_rows = dedup(anomaly_rows)
    missing_file_refs = dedup(missing_file_refs)

    lt_flags_csv_path = OUT_DIR / "yield_sensor_flags_longterm.csv"
    with lt_flags_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "experiment",
                "cultivar",
                "heat_trt",
                "plot_id",
                "source_row",
                "missing_overview",
                "missing_files",
                "temp_model_usable",
            ],
        )
        writer.writeheader()
        for (cultivar, heat_trt, plot_id), flags in sorted(
            lt_row_flags.items(), key=lambda x: (x[0][0], x[0][2], x[0][1])
        ):
            missing_overview = int(flags["missing_overview"])
            missing_files = int(flags["missing_files"])
            writer.writerow(
                {
                    "experiment": "longterm",
                    "cultivar": cultivar,
                    "heat_trt": heat_trt,
                    "plot_id": plot_id,
                    "source_row": flags["source_row"],
                    "missing_overview": missing_overview,
                    "missing_files": missing_files,
                    "temp_model_usable": int((missing_overview + missing_files) == 0),
                }
            )

    acute_flags_csv_path = OUT_DIR / "yield_sensor_flags_acute.csv"
    with acute_flags_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "experiment",
                "cultivar",
                "treatment_raw",
                "replicate",
                "source_row",
                "missing_overview",
                "missing_files",
                "missing_window",
                "temp_model_usable",
            ],
        )
        writer.writeheader()
        for (cultivar, treatment_raw, rep), flags in sorted(
            acute_row_flags.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])
        ):
            missing_overview = int(flags["missing_overview"])
            missing_files = int(flags["missing_files"])
            missing_window = int(flags["missing_window"])
            writer.writerow(
                {
                    "experiment": "acute",
                    "cultivar": cultivar,
                    "treatment_raw": treatment_raw,
                    "replicate": rep,
                    "source_row": flags["source_row"],
                    "missing_overview": missing_overview,
                    "missing_files": missing_files,
                    "missing_window": missing_window,
                    "temp_model_usable": int(
                        (missing_overview + missing_files + missing_window) == 0
                    ),
                }
            )

    resolution_csv_path = OUT_DIR / "sensor_filename_resolution.csv"
    with resolution_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "stress_type",
                "sensor",
                "overview_file_ref",
                "resolution_status",
                "resolved_file_stem",
            ],
        )
        writer.writeheader()
        writer.writerows(
            sorted(
                resolution_csv_rows,
                key=lambda r: (
                    r["stress_type"],
                    r["sensor"],
                    r["overview_file_ref"],
                ),
            )
        )

    report_path = OUT_DIR / "yield_vs_sensors_crosscheck.md"
    report_lines = [
        "# Yield vs Sensor Cross-Check (4-channel + HOBO)",
        "",
        "This report validates whether each yield row is supported by sensor metadata/files.",
        "",
        "## Scope",
        "- Yield files: long-term and acute (all rows + A0-removed subset).",
        "- Sensor sources: 4 Channel + HOBO.",
        "- Metadata source: Listofdates_HeatStressTreatments2024.xlsx, filtered to 2024 rows only.",
        "",
        "## Summary",
        f"- Long-term yield rows checked: {len(lt_rows)}",
        f"- Acute yield rows checked (all): {len(acute_rows_all)}",
        f"- Acute yield rows checked (A0 removed): {len(acute_rows_no_a0)}",
        f"- Long-term missing overview mappings: {len(lt_missing_overview)}",
        f"- Long-term missing sensor files after mapping: {len(lt_missing_files)}",
        f"- Acute missing overview mappings: {len(acute_missing_overview)}",
        f"- Acute missing sensor files after mapping: {len(acute_missing_files)}",
        f"- Acute rows with file present but no samples in treatment window: {len(acute_missing_window_data)}",
        f"- Overview anomalies (plot coding issues): {len(anomaly_rows)}",
        f"- Missing file references in overview (2024 rows): {len(missing_file_refs)}",
        f"- Filename resolution status counts (row-level): {resolution_status_counts}",
        f"- Filename resolution output: {resolution_csv_path}",
        f"- Row-level sensor flags output: {lt_flags_csv_path}, {acute_flags_csv_path}",
        "",
    ]

    def append_section(title: str, items: list[str], max_items: int = 30) -> None:
        report_lines.append(f"## {title}")
        if not items:
            report_lines.append("- None")
            report_lines.append("")
            return
        for line in items[:max_items]:
            report_lines.append(f"- {line}")
        if len(items) > max_items:
            report_lines.append(f"- ... and {len(items) - max_items} more")
        report_lines.append("")

    append_section("Long-term missing overview mappings", lt_missing_overview)
    append_section("Long-term missing files", lt_missing_files)
    append_section("Acute missing overview mappings", acute_missing_overview)
    append_section("Acute missing files", acute_missing_files)
    append_section("Acute missing in-window sensor data", acute_missing_window_data)
    append_section("Overview anomalies", anomaly_rows)
    append_section("Overview missing file references (sample)", missing_file_refs)

    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Wrote: {report_path}")
    print(f"Long-term missing overview: {len(lt_missing_overview)}")
    print(f"Long-term missing files: {len(lt_missing_files)}")
    print(f"Acute missing overview: {len(acute_missing_overview)}")
    print(f"Acute missing files: {len(acute_missing_files)}")
    print(f"Acute missing in-window data: {len(acute_missing_window_data)}")
    print(f"Overview anomalies: {len(anomaly_rows)}")
    print(f"Overview missing file references: {len(missing_file_refs)}")
    print(f"Filename resolution CSV: {resolution_csv_path}")
    print(f"Row-level flag CSVs: {lt_flags_csv_path} , {acute_flags_csv_path}")


if __name__ == "__main__":
    main()
