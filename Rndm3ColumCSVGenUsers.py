import csv
import random

# Define output file
filename = "random_data.csv"

# Sample names pool (expand as needed)
first_names = ["John","Maria","David","Emily","Michael","Sarah","Daniel","Laura",
               "James","Olivia","Robert","Sophia","William","Grace","Henry","Chloe",
               "George","Ella","Jack","Lily","Noah","Emma","Lucas","Ava","Mason",
               "Isabella","Ethan","Mia","Alexander","Charlotte"]
surnames = ["Smith","Johnson","Brown","Davis","Wilson","Taylor","Anderson","Thomas",
            "White","Harris","Martin","Clark","Lewis","Walker","Hall","Allen",
            "Young","King","Wright","Scott","Green","Baker","Adams","Nelson","Hill",
            "Campbell","Mitchell","Roberts","Carter","Phillips"]

def random_name():
    return f"{random.choice(first_names)} {random.choice(surnames)}"

def random_number():
    num = random.randint(1, 99999999)  # ensures not 00000000
    return f"{num:08d}"

# Generate CSV
with open(filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Names & Surname","Coy number","ID Card number"])
    for _ in range(400):
        writer.writerow([random_name(), random_number(), random_number()])

print(f"CSV file '{filename}' with 400 rows created.")
