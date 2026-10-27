import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from MachineFill import load_and_sort_data, get_machine_groups, _get_csv_filename

EXPECTED_COLS = ["Timestamp", "FleetNumber", "Oil Type", "Liters", "Attendant", "Coynumber"]

def check(csv_path: Path, expected_rows: int):
    df = load_and_sort_data(csv_path)
    assert list(df.columns) == EXPECTED_COLS, f"columns: {list(df.columns)}"
    assert len(df) == expected_rows, f"rows: {len(df)}"
    assert str(df["Timestamp"].dtype).startswith("datetime64")
    assert df["Liters"].dtype.kind in "fi"
    assert df["Liters"].gt(0).all()
    assert df.attrs.get("source_filename") == csv_path.name, f"source_filename attr: {df.attrs.get('source_filename')}"

    groups = get_machine_groups(df)
    derived = _get_csv_filename(groups)
    assert derived == csv_path.name, f"derived filename: {derived} != {csv_path.name}"

    print(f"OK {csv_path.name}: rows={len(df)} cols={list(df.columns)} source_filename={derived}")
    print(df.head())
    print()

check(Path(__file__).parent.parent / "data" / "FixNulNav_KTK025_LubeTruck_log.csv", 22)
check(Path(__file__).parent.parent / "data" / "NullChars-Nav_KTK025_LubeTruck_log.csv", 22)
