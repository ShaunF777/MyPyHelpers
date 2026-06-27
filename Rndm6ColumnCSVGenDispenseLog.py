import csv
import random
from datetime import datetime, timedelta

# === CONFIG ===
filename = "OilBay_mock.csv"
GenerateQTY = 200   # change this to any number of rows you want
begin_dt = datetime(2026, 5, 10, 6, 0)   # start date/time
end_dt   = datetime(2026, 6, 11, 20, 0)  # end date/time

# === DATA POOLS ===
fluid_types = ["15W40 Oil", "ACX30 Oil", "85W-140 Oil", "HYD 68 Oil"]

names_coy = [
    ("Emily White", 89647331), ("Isabella Brown", 34480657), ("Laura Johnson", 97587463),
    ("Noah Johnson", 96702775), ("Grace Roberts", 85735401), ("Henry Allen", 43780801),
    ("Lucas Young", 52724039), ("Charlotte Campbell", 23693565), ("Mia Nelson", 63955959),
    ("David Smith", 26305713), ("Mia Clark", 20905089), ("Grace White", 15387207),
    ("Sarah Young", 13187795), ("Lily Lewis", 13138584), ("Lucas Harris", 41486519),
    ("Henry Lewis", 96199972), ("Emma Phillips", 42464177), ("Olivia Young", 53144987),
    ("Michael Lewis", 28770724), ("Lily Davis", 92247255), ("Robert Mitchell", 34318744),
    ("William Adams", 18969804), ("James Carter", 24517618), ("John Baker", 16461063),
    ("Chloe Thomas", 17316322), ("Olivia Taylor", 96964921), ("Ethan Allen", 48515493),
    ("Lucas Mitchell", 83123285), ("Michael Phillips", 4947235), ("Mia Walker", 2956691),
    ("Isabella Harris", 76925647), ("William Smith", 37941481), ("George Campbell", 68680620),
    ("Lucas King", 34011183), ("Emily Thomas", 19462106), ("Jack Scott", 86281141),
    ("Chloe Taylor", 62218909), ("George Clark", 18850542), ("Daniel Anderson", 27457062)
]

fleet_numbers = [
    "KAD1563","KFH2040","KFH4717","KWT2553","KTH0064","PBC6761","KAD4059","KWL1100",
    "KDT2515","PBC8697","KLB0089","KLB6750","WT4451","KMG5700","KWT9620","OFL9573",
    "KMG5743","OHT2704","OBEX7239","OFH2006","OHT6089","OFH7803","KMG5993","KDT3034",
    "KWD3294","KWD5256","KTD5557","KDT8580","KMG1539","OHT8635"
]

# === TIME SPLITTING ===
total_seconds = (end_dt - begin_dt).total_seconds()
step_seconds = total_seconds / GenerateQTY

timestamps = [begin_dt + timedelta(seconds=i*step_seconds) for i in range(GenerateQTY)]

# === GENERATE CSV ===
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["TimeStamp","Fluid_Transaction","Liters_Dispensed","FleetNumber","Name","COY Number"])
    for ts in timestamps:
        # force transactions only between 06:00–20:00
        if ts.hour < 6: ts = ts.replace(hour=6, minute=0)
        if ts.hour > 20: ts = ts.replace(hour=20, minute=0)

        fluid = random.choice(fluid_types)
        liters = f"{random.uniform(1,600):.2f}Ltr"
        fleet = random.choice(fleet_numbers)
        name, coy = random.choice(names_coy)

        writer.writerow([ts.strftime("%Y-%m-%d %H:%M:%S"), fluid, liters, fleet, name, coy])

print(f"CSV file '{filename}' created with {GenerateQTY} rows.")
