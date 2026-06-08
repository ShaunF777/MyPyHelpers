import csv
import random

first_names = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Daniel", "Matthew", "Anthony", "Mark",
    "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Emily", "Emma",
    "Olivia", "Sophia", "Isabella", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn",
    "Liam", "Noah", "Oliver", "Elijah", "Benjamin", "Lucas", "Mason", "Ethan",
    "Aiden", "Logan", "Maria", "Anna", "Grace", "Chloe", "Victoria", "Natalie"
]

last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin",
    "Thompson", "Young", "Allen", "King", "Wright", "Scott", "Green", "Baker",
    "Adams", "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner", "Phillips",
    "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Rogers",
    "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper", "Cox", "Ward"
]

def random_8digit():
    while True:
        n = random.randint(10000000, 99999999)
        if n != 0:
            return str(n)

def random_name():
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    return name[:30]

with open("SyntheticData.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Names & Surname", "Coy number", "ID Card number"])
    for _ in range(400):
        writer.writerow([random_name(), random_8digit(), random_8digit()])

print("SyntheticData.csv created with 400 rows.")
