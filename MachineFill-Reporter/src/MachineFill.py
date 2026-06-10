import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
from typing import Dict, Optional

DATA_PATH = Path(__file__).parent.parent / "data" / "IFS_KTK025_log_2026.06.04.csv"
ASSETS_DIR = Path(__file__).parent.parent / "assets"
REPORTS_DIR = Path(__file__).parent.parent / "reports"

OIL_COLORS = {
    "ACX30": "#1f77b4",
    "15W40": "#ff7f0e",
    "68HYD": "#2ca02c",
    "85W140": "#d62728"
}
DEFAULT_COLOR = "#7f7f7f"

START_DATE: Optional[str] = None
END_DATE: Optional[str] = None


def parse_liters(value) -> float:
    if pd.isna(value):
        return 0.0
    if isinstance(value, str):
        return float(value.replace("Ltr", "").strip())
    return float(value)


def load_and_sort_data(filepath: Path = DATA_PATH, start_date: Optional[str] = START_DATE, end_date: Optional[str] = END_DATE) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    
    df = df.rename(columns={
        "TimeStamp": "Timestamp",
        "Fluid_Transaction": "Oil Type",
        "Liters_Dispensed": "Liters",
        "Name": "Attendant",
        "COY Number": "Coynumber"
    })
    
    desired_cols = ["Timestamp", "FleetNumber", "Oil Type", "Liters", "Attendant", "Coynumber"]
    df = df[desired_cols].copy()
    
    df["FleetNumber"] = df["FleetNumber"].str.strip()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Liters"] = df["Liters"].apply(parse_liters)
    df["Attendant"] = df["Attendant"].fillna("")
    df["Coynumber"] = df["Coynumber"].fillna("")
    df["Attendant"] = df["Attendant"].where(df["Attendant"] != "", df["Coynumber"])
    df = df[df["Liters"] > 0]
    
    if start_date:
        df = df[df["Timestamp"] >= start_date]
    if end_date:
        df = df[df["Timestamp"] <= end_date]
    
    df = df.sort_values(by=["FleetNumber", "Timestamp"], ascending=[True, True]).reset_index(drop=True)
    
    return df


def get_machine_groups(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    return {fleet: group for fleet, group in df.groupby("FleetNumber", sort=False)}


def print_transaction_summary(df: pd.DataFrame) -> None:
    summary = df.groupby("FleetNumber").size().reset_index(name="Total Transactions")
    print("Transaction Summary by Fleet Number:")
    for _, row in summary.iterrows():
        print(f"  {row['FleetNumber']}: {row['Total Transactions']}")


def generate_pie_chart(machine_df: pd.DataFrame, fleet_number: str, output_dir: Path = ASSETS_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    
    oil_totals = machine_df.groupby("Oil Type")["Liters"].sum()
    oil_totals = oil_totals[oil_totals > 0]
    
    if oil_totals.empty:                
        # Handle case where there's no consumption data
        print(f"No consumption data for {fleet_number}")
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, "No consumption data", ha='center', va='center')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        output_path = output_dir / f"chart_{fleet_number}.png"
        fig.savefig(output_path)
        plt.close(fig)
        return output_path
    

    def get_color_key(oil_type: str) -> str:
        key = oil_type.replace(" Oil", "").replace(" ", "").replace("-", "")
        if key == "HYD68":
            key = "68HYD"
        return key
    
    colors = [OIL_COLORS.get(get_color_key(ot), DEFAULT_COLOR) for ot in oil_totals.index]
    
    labels = [f"{ot} - {round(l, 1)}Ltr" for ot, l in zip(oil_totals.index, oil_totals.values)]
    
    fig, ax = plt.subplots(figsize=(6.2, 4.8)) #Width, Hight - graph shape rectangular
    #Radius of 0.95 is big enough for all to see, and leaves ample space for labels
    #Startangle of 135 first slice starts at the TopLeft
    ax.pie(oil_totals.values, labels=labels, colors=colors, startangle=135, radius=0.95)
    
    output_path = output_dir / f"chart_{fleet_number}.png"
    fig.savefig(output_path)
    plt.close(fig)
    
    return output_path


def generate_html_report(machine_groups: Dict[str, pd.DataFrame], output_dir: Path = REPORTS_DIR, min_date: Optional[str] = None, max_date: Optional[str] = None) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_filename = DATA_PATH.name
    
    sections = []
    
    for fleet_number, machine_df in sorted(machine_groups.items()):
        generate_pie_chart(machine_df, fleet_number)
        
        oil_totals = machine_df.groupby("Oil Type")["Liters"].sum()
        total_liters = oil_totals.sum()
        percentages = (oil_totals / total_liters * 100).round(1)
        
        summary_rows = ""
        for oil_type, liters, pct in zip(oil_totals.index, oil_totals.values, percentages):
            summary_rows += f"<tr><td>{oil_type}</td><td>{round(liters, 1)} Ltr</td><td>{pct}%</td></tr>\n"
        
        tx_rows = ""
        for _, row in machine_df.iterrows():
            tx_rows += f"<tr><td>{row['Timestamp'].strftime('%Y-%m-%d %H:%M')}</td><td>{row['Attendant']}</td><td>{row['Coynumber']}</td><td>{row['Oil Type']}</td><td>{round(row['Liters'], 1)} Ltr</td></tr>\n"
        
        section = f"""
        <h2 style='text-align:center'>Summerised oil consumption for FleetNumber : {fleet_number}</h2>
        <div class="flex-container">
            <div class="chart-col">
                <img src="../assets/chart_{fleet_number}.png" alt="Chart for {fleet_number}">
            </div>
            <div class="summary-col">
                <table class="summary-table">
                    <tr><th>Oil Type</th><th>Total-Consumed</th><th>Percentage</th></tr>
                    {summary_rows}
                </table>
            </div>
        </div>
        <table class="transaction-table">
            <tr><th>Timestamp</th><th>Attendant</th><th>Coynumber</th><th>Oil Type</th><th>Liters</th></tr>
            {tx_rows}
        </table>
        """
        sections.append(section)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Oil Consumption Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; display: flex; align-items: center; }}
        .logo {{ width: 204px; height: 59px; margin-right: 20px; }}
        .header-content {{ flex: 1; text-align: center; }}
        .flex-container {{ display: flex; margin: 20px 0; }}
        .chart-col {{ flex: 1; text-align: center; }}
        .summary-col {{ flex: 2; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .summary-table {{ margin-left: 20px; }}
        .transaction-table {{ margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <img src="../assets/Thungela logo.png" alt="Company Logo" class="logo">
        <div class="header-content">
            <h1>{csv_filename} Report</h1>
            <p>Date Range: {min_date} to {max_date}</p>
        </div>
    </div>
    {''.join(sections)}
</body>
</html>
"""
    
    output_path = output_dir / "consumption_report.html"
    output_path.write_text(html_content)
    
    return output_path


def export_to_pdf(machine_groups: Dict[str, pd.DataFrame], output_path: Path, min_date: Optional[str] = None, max_date: Optional[str] = None) -> Path:
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with PdfPages(output_path) as pdf:
            for page_idx, (fleet_number, machine_df) in enumerate(sorted(machine_groups.items())):
                fig = plt.figure(figsize=(11, 8.5)) #Creates a new page (figure) sized like US Letter (landscape)
                fig.patch.set_facecolor('white')
                
                if page_idx == 0:   
                #Adds a dark banner bar w'out ticks and spine at the top (only on page 1)
                #Argument list [left, bottom, width, height]
                #All values are fractions of the Figure size (range 0.0 to 1.0).
                #They define where the Axes sits inside the Figure and how big it is.
                    ax_banner = fig.add_axes([0.0, 0.87, 1.0, 0.12], facecolor='#2c3e50')
                    ax_banner.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)
                    for spine in ax_banner.spines.values():
                        spine.set_visible(False)
                    logo_path = ASSETS_DIR / "Thungela logo.png"
                    if logo_path.exists():      #Argument list [left, bottom, width, height]
                        ax_logo = fig.add_axes([0.02, 0.89, 0.18, 0.07])
                        img = plt.imread(logo_path)
                        ax_logo.imshow(img)
                        ax_logo.axis('off')
                    #Argument list [left, bottom] All values are fractions of the Figure size (range 0.0 to 1.0)
                    fig.text(0.35, 0.95, f"{DATA_PATH.name} Report", ha='left', va='top', fontsize=16, fontweight='bold', color='white')
                    fig.text(0.35, 0.91, f"Date Range: {min_date} to {max_date}", ha='left', va='top', fontsize=10, color='white')
                
                plt.figtext(0.5, 0.84 if page_idx == 0 else 0.94, f"Summarised oil consumption for FleetNumber : {fleet_number}", ha='center', fontsize=14, fontweight='bold')
                
                oil_totals = machine_df.groupby("Oil Type")["Liters"].sum()
                total_liters = oil_totals.sum()
                percentages = (oil_totals / total_liters * 100).round(1)
                
                chart_path = ASSETS_DIR / f"chart_{fleet_number}.png"
                if chart_path.exists():
                    #Argument list [left, bottom, width, height]fractions of the Figure size (range 0.0 to 1.0)
                    ax_img = fig.add_axes([0.02, 0.26 if page_idx == 0 else 0.38, 0.54, 0.66])
                    img = plt.imread(chart_path)
                    ax_img.imshow(img)
                    ax_img.axis('off')
                
                ax_table = fig.add_axes([0.58, 0.66 if page_idx == 0 else 0.76, 0.35, 0.18])
                ax_table.axis('off')
                table_data = [[oil_type, f"{round(liters, 1)} Ltr", f"{pct}%"] for oil_type, liters, pct in zip(oil_totals.index, oil_totals.values, percentages)]
                table_data.insert(0, ["Oil Type", "Total", "Percentage"])
                table = ax_table.table(cellText=table_data, loc='center', cellLoc='center')
                table.auto_set_font_size(False)
                table.set_fontsize(8)
                table.scale(1, 1.2)
                
                tx_data = []
                for _, row in machine_df.iterrows():
                    tx_data.append([
                        row['Timestamp'].strftime('%Y-%m-%d %H:%M'),
                        str(row['Attendant']),
                        str(row['Oil Type']),
                        f"{round(row['Liters'], 1)} Ltr"
                    ])
                
                ax_tx = fig.add_axes([0.05, 0.05, 0.90, 0.25])
                ax_tx.axis('off')
                tx_headers = ["Timestamp", "Attendant", "Oil Type", "Liters"]
                tx_table_data = [tx_headers] + tx_data
                tx_table = ax_tx.table(cellText=tx_table_data, loc='center', cellLoc='center')
                tx_table.auto_set_font_size(False)
                tx_table.set_fontsize(7)
                tx_table.scale(1, 1.2)
                
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
        
        return output_path
        
    except PermissionError:
        print(f"WARNING: Could not write to {output_path}. Please close the PDF file if it's open and try again.")
        raise
    except Exception as e:
        print(f"WARNING: Could not generate PDF report: {e}")
        raise


if __name__ == "__main__":
    df = load_and_sort_data()
    print_transaction_summary(df)
    machine_groups = get_machine_groups(df)
    
    all_timestamps = pd.concat([group["Timestamp"] for group in machine_groups.values()])
    min_date = all_timestamps.min().strftime("%Y-%m-%d %H:%M")
    max_date = all_timestamps.max().strftime("%Y-%m-%d %H:%M")
    
    report_path = generate_html_report(machine_groups, min_date=min_date, max_date=max_date)
    print(f"\nHTML Report generated: {report_path}")
    
    pdf_path = REPORTS_DIR / "machine_consumption_summary.pdf"
    pdf_path = export_to_pdf(machine_groups, pdf_path, min_date=min_date, max_date=max_date)
    print(f"PDF Report generated: {pdf_path}")