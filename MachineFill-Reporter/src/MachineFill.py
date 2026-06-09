import pandas as pd
from pathlib import Path
from typing import Dict

DATA_PATH = Path(__file__).parent.parent / "data" / "NavOilBay_mock.csv"


def load_and_sort_data(filepath: Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    
    df = df.rename(columns={
        "TimeStamp": "Timestamp",
        "Fluid_Transaction": "Oil Type",
        "Liters_Dispensed": "Liters",
        "Name": "Attendant"
    })
    
    desired_cols = ["Timestamp", "FleetNumber", "Oil Type", "Liters", "Attendant"]
    df = df[desired_cols].copy()
    
    df["FleetNumber"] = df["FleetNumber"].str.strip()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    
    df = df.sort_values(by=["FleetNumber", "Timestamp"], ascending=[True, True]).reset_index(drop=True)
    
    return df


def get_machine_groups(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    return {fleet: group for fleet, group in df.groupby("FleetNumber", sort=False)}


def print_transaction_summary(df: pd.DataFrame) -> None:
    summary = df.groupby("FleetNumber").size().reset_index(name="Total Transactions")
    print("Transaction Summary by Fleet Number:")
    for _, row in summary.iterrows():
        print(f"  {row['FleetNumber']}: {row['Total Transactions']}")


if __name__ == "__main__":
    df = load_and_sort_data()
    print_transaction_summary(df)
    machine_groups = get_machine_groups(df)