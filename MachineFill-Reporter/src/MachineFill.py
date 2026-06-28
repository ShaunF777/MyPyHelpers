import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
from typing import Dict, Optional
import sys
import json
import tempfile
from datetime import date, timedelta

def get_base_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent

def get_output_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path.cwd()
    return Path(__file__).parent.parent

def get_appdata_path() -> Path:
    appdata = Path.home() / "AppData" / "Local" / "MachineFillReporter"
    appdata.mkdir(parents=True, exist_ok=True)
    return appdata

BASE_PATH = get_base_path()
OUTPUT_PATH = get_output_path()
APPDATA_PATH = get_appdata_path()
DATA_PATH = BASE_PATH / "data" / "NavOilBay_mock.csv"
ASSETS_DIR = OUTPUT_PATH / "assets"
REPORTS_DIR = OUTPUT_PATH / "Machinefill-Reports"
CHARTS_TEMP_DIR = Path(tempfile.gettempdir()) / "MachineFillReporter" / "charts"
CHARTS_TEMP_DIR.mkdir(parents=True, exist_ok=True)
SETTINGS_FILE = APPDATA_PATH / "machinefill_settings.json"

DEFAULT_OIL_COLORS = {
    "ACX30": "#1f77b4",
    "15W40": "#ff7f0e",
    "68HYD": "#2ca02c",
    "85W140": "#d62728"
}
DEFAULT_COLOR = "#7f7f7f"

def load_settings() -> Dict:
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"colors": dict(DEFAULT_OIL_COLORS), "logo_path": None}

def save_settings(settings: Dict) -> None:
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def load_colors() -> Dict[str, str]:
    return load_settings().get("colors", dict(DEFAULT_OIL_COLORS))

def save_colors(colors: Dict[str, str]) -> None:
    settings = load_settings()
    settings["colors"] = colors
    save_settings(settings)

def load_logo_path() -> Optional[Path]:
    logo_path = load_settings().get("logo_path")
    if logo_path and Path(logo_path).exists():
        return Path(logo_path)
    return None

def save_logo_path(path: str) -> None:
    settings = load_settings()
    settings["logo_path"] = path
    save_settings(settings)

OIL_COLORS = load_colors()

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


def generate_pie_chart(machine_df: pd.DataFrame, fleet_number: str, output_dir: Path = CHARTS_TEMP_DIR) -> Path:
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
                    logo_path = load_logo_path() or (BASE_PATH / "assets" / "Thungela logo.png")
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
                
                chart_path = CHARTS_TEMP_DIR / f"chart_{fleet_number}.png"
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
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from tkcalendar import DateEntry

    class MachineFillGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("MachineFill Reporter")
            self.root.geometry("560x540")
            self.root.resizable(False, False)

            self.csv_path = tk.StringVar(value=str(OUTPUT_PATH))
            self.logo_path = tk.StringVar(value="")
            self.status_text = tk.StringVar(value="Ready")

            self.oil_colors = load_colors()
            self.color_vars = {}
            self.color_buttons = {}
            for key, val in self.oil_colors.items():
                self.color_vars[key] = tk.StringVar(value=val)

            today = date.today()
            self.default_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            self.default_end = today.strftime("%Y-%m-%d")

            self._build_ui()

        def _build_ui(self):
            pad = {"padx": 10, "pady": 4}

            file_frame = ttk.LabelFrame(self.root, text="Step 1. Select .csv file")
            file_frame.pack(fill="x", **pad)

            ttk.Entry(file_frame, textvariable=self.csv_path, width=50).pack(side="left", padx=(10, 4), pady=6)
            ttk.Button(file_frame, text="Browse", command=self.browse_csv).pack(side="left", padx=(0, 10), pady=6)

            logo_frame = ttk.LabelFrame(self.root, text="Step 2. Select Company Logo")
            logo_frame.pack(fill="x", **pad)

            ttk.Entry(logo_frame, textvariable=self.logo_path, width=50).pack(side="left", padx=(10, 4), pady=6)
            ttk.Button(logo_frame, text="Browse", command=self.browse_logo).pack(side="left", padx=(0, 10), pady=6)

            date_frame = ttk.LabelFrame(self.root, text="Step 3. Customise report dates")
            date_frame.pack(fill="x", **pad)

            ttk.Label(date_frame, text="Begin Date:").pack(side="left", padx=(10, 4))
            self.start_cal = DateEntry(date_frame, width=12, date_pattern="yyyy-mm-dd")
            self.start_cal.pack(side="left", padx=(0, 16))
            self.start_cal.set_date(self.default_start)

            ttk.Label(date_frame, text="End Date:").pack(side="left", padx=(0, 4))
            self.end_cal = DateEntry(date_frame, width=12, date_pattern="yyyy-mm-dd")
            self.end_cal.pack(side="left")
            self.end_cal.set_date(self.default_end)

            ttk.Button(date_frame, text="Clear Dates", command=self.clear_dates).pack(side="left", padx=(16, 0))

            color_frame = ttk.LabelFrame(self.root, text="Step 4. Change colors")
            color_frame.pack(fill="x", **pad)

            for i, (key, var) in enumerate(self.color_vars.items()):
                ttk.Label(color_frame, text=key + ":").grid(row=0, column=i * 2, padx=(8, 2), pady=4)
                color_btn = tk.Button(color_frame, textvariable=var, bg=var.get(), width=8,
                                      command=lambda k=key: self.pick_color(k))
                color_btn.grid(row=0, column=i * 2 + 1, padx=(0, 8), pady=4)
                self.color_buttons[key] = color_btn

            action_frame = ttk.Frame(self.root)
            action_frame.pack(fill="x", **pad)

            ttk.Button(action_frame, text="Generate Report", command=self.generate_reports).pack(side="left", padx=(10, 6))
            ttk.Button(action_frame, text="Open Output Folder", command=self.open_output_folder).pack(side="left", padx=6)

            status_frame = ttk.LabelFrame(self.root, text="Status")
            status_frame.pack(fill="both", expand=True, **pad)

            self.status_display = tk.Text(status_frame, height=8, width=62, state="disabled", wrap="word")
            self.status_display.pack(padx=4, pady=4)

        def log(self, message):
            self.status_display.config(state="normal")
            self.status_display.insert("end", message + "\n")
            self.status_display.see("end")
            self.status_display.config(state="disabled")
            self.root.update_idletasks()

        def browse_csv(self):
            path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if path:
                self.csv_path.set(path)
                self._detect_csv_dates(path)

        def _detect_csv_dates(self, path):
            try:
                df = pd.read_csv(path, usecols=["TimeStamp"])
                df["TimeStamp"] = pd.to_datetime(df["TimeStamp"])
                if not df.empty:
                    min_ts = df["TimeStamp"].min()
                    max_ts = df["TimeStamp"].max()
                    self.start_cal.set_date(min_ts)
                    self.end_cal.set_date(max_ts)
                    self.log(f"CSV date range: {min_ts.strftime('%Y-%m-%d')} to {max_ts.strftime('%Y-%m-%d')}")
            except Exception as e:
                self.log(f"Could not detect CSV dates: {e}")

        def browse_logo(self):
            path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
            if path:
                self.logo_path.set(path)
                save_logo_path(path)
                self.log(f"Logo set: {path}")

        def clear_dates(self):
            self.start_cal.set_date(self.default_start)
            self.end_cal.set_date(self.default_end)

        def pick_color(self, key):
            from tkinter import colorchooser
            current = self.color_vars[key].get()
            result = colorchooser.askcolor(initialcolor=current, title=f"Pick color for {key}")
            if result[1]:
                self.color_vars[key].set(result[1])
                self.oil_colors[key] = result[1]
                OIL_COLORS[key] = result[1]
                save_colors(self.oil_colors)
                self.color_buttons[key].config(bg=result[1])
                self.log(f"Color saved: {key} = {result[1]}")

        def generate_reports(self):
            csv_path = Path(self.csv_path.get())
            if not csv_path.exists():
                messagebox.showerror("Error", f"CSV file not found:\n{csv_path}")
                return

            start = self.start_cal.get() or None
            end = self.end_cal.get() or None

            self.log(f"Loading: {csv_path.name}")
            try:
                df = load_and_sort_data(csv_path, start_date=start, end_date=end)
            except Exception as e:
                self.log(f"ERROR loading data: {e}")
                messagebox.showerror("Error", str(e))
                return

            if df.empty:
                self.log("No data found in the selected date range.")
                messagebox.showwarning("No Data", "No data found for the selected criteria.")
                return

            machine_groups = get_machine_groups(df)
            self.log(f"Found {len(machine_groups)} fleet(s)")

            all_timestamps = pd.concat([group["Timestamp"] for group in machine_groups.values()])
            min_date = all_timestamps.min()
            max_date = all_timestamps.max()
            min_str = min_date.strftime("%Y-%m-%d %H:%M")
            max_str = max_date.strftime("%Y-%m-%d %H:%M")
            start_str = self.start_cal.get() or min_date.strftime("%Y-%m-%d")
            end_str = self.end_cal.get() or max_date.strftime("%Y-%m-%d")
            days_diff = (max_date - min_date).days

            self.log("Generating pie charts...")
            for fleet_number in sorted(machine_groups.keys()):
                generate_pie_chart(machine_groups[fleet_number], fleet_number)
                self.log(f"  Chart: {fleet_number}")

            self.log("Generating PDF report...")
            csv_stem = csv_path.stem
            pdf_name = f"{csv_stem}_{days_diff}Days_{end_str}.pdf"
            pdf_path = REPORTS_DIR / pdf_name
            export_to_pdf(machine_groups, pdf_path, min_date=min_str, max_date=max_str)
            self.log(f"  PDF saved: {pdf_path}")
            self.log(f"  Output folder: {REPORTS_DIR}")

            self.log("Done!")
            messagebox.showinfo("Success", f"Report generated!\n\n{pdf_name}\n\nSaved to:\n{REPORTS_DIR}")

        def open_output_folder(self):
            import subprocess
            folder = str(REPORTS_DIR)
            subprocess.Popen(f'explorer "{folder}"')

    root = tk.Tk()
    app = MachineFillGUI(root)
    root.mainloop()