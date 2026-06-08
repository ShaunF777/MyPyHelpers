import csv
import random

# Define output file
filename = "random_machines.csv"

# Pools of machine attributes
plant_prefixes = ["KAD", "KDT", "KFH", "KHT", "KLB", "KMG", "KTD", "KTH", "KTK", "KWD", "KWL", "KWT", "OBEX", "ODT", "OFH", "OFL", "OHT", "PBC", "WT"]
models = [
    "HM400-2", "HD785-7", "TCM", "UTILEV UT25P", "EH3500", "WB93R-5", "WB93-5EO",
    "CAT16H", "CAT16M", "D375A-5", "D375A-6", "D475A-5EO", "WA500-3", "HM300-1",
    "HM300-2", "HM400-3R", "WD600-3", "EH1600", "730E-6", "CLARK C70", "WA800-3EO",
    "BOBCAT", "HD785-5", "VOLVO"
]
types = [
    "PUMP TRUCK", "DUMPER", "FORKLIFT", "DUMP TRUCK ELEC", "TLB", "GRADER",
    "TRACK DOZER", "TYRE HANDLER", "SERVICE TRUCK", "DIESEL BOWZER", "WHEEL DOZER",
    "CABLE REELER", "WATER TANKER", "EXCAVATOR HAMMER", "ELECTRIC DUMPER",
    "WHEEL LOADER", "BOBCAT"
]

def random_plant_no():
    prefix = random.choice(plant_prefixes)
    suffix = str(random.randint(1, 9999)).zfill(4)  # padded 4-digit suffix
    return prefix + suffix

# Generate CSV
with open(filename, "w", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["Row", "Plant no", "Model", "TYPE"])
    for row in range(1, 491):  # 490 rows
        plant_no = random_plant_no()
        model = random.choice(models)
        machine_type = random.choice(types)
        writer.writerow([row, plant_no, model, machine_type])

print(f"CSV file '{filename}' with 490 rows created.")
