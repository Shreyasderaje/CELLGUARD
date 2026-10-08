import csv
import random
from datetime import datetime, timedelta

NUM_ROWS = 5000

MACHINES = ["M01", "M02", "M03", "M04"]

DEFECT_TYPES = [
    "Porosity",
    "Crack",
    "Incomplete_Weld",
    "Burn_Through"
]


def generate_record(index):

    batch_id = f"B{index:05d}"

    machine_id = random.choice(MACHINES)

    timestamp = datetime(2026, 1, 1) + timedelta(minutes=index * 10)

    # Normal welding conditions
    current = random.gauss(190, 10)
    voltage = random.gauss(24.5, 1.0)
    temperature = random.gauss(85, 7)
    pressure = random.gauss(4.5, 0.3)
    welding_time = random.gauss(3.2, 0.25)
    speed = random.gauss(12, 1)

    defect_type = "None"

    # Around 15% of records are defective
    if random.random() < 0.15:

        defect_type = random.choice(DEFECT_TYPES)

        # Porosity
        if defect_type == "Porosity":
            current += random.uniform(20, 40)
            temperature += random.uniform(15, 30)
            pressure -= random.uniform(0.8, 1.5)

        # Crack
        elif defect_type == "Crack":
            temperature += random.uniform(20, 40)
            welding_time -= random.uniform(0.5, 1.0)

        # Incomplete weld
        elif defect_type == "Incomplete_Weld":
            current -= random.uniform(20, 40)
            welding_time -= random.uniform(0.5, 1.0)
            speed += random.uniform(2, 5)

        # Burn through
        elif defect_type == "Burn_Through":
            current += random.uniform(30, 50)
            voltage += random.uniform(2, 4)
            temperature += random.uniform(25, 45)

    defect_status = (
        "Defect" if defect_type != "None"
        else "Normal"
    )

    return [
        batch_id,
        machine_id,
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        round(current, 2),
        round(voltage, 2),
        round(temperature, 2),
        round(pressure, 2),
        round(welding_time, 2),
        round(speed, 2),
        defect_status,
        defect_type
    ]


headers = [
    "batch_id",
    "machine_id",
    "timestamp",
    "current",
    "voltage",
    "temperature",
    "pressure",
    "welding_time",
    "speed",
    "defect_status",
    "defect_type"
]


with open(
    "data/factory_process_data.csv",
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow(headers)

    for i in range(1, NUM_ROWS + 1):
        writer.writerow(generate_record(i))


print("----------------------------------------")
print("CELLGUARD Factory Data Generator")
print("----------------------------------------")
print(f"Generated records : {NUM_ROWS}")
print("Dataset           : data/factory_process_data.csv")
print("Data type         : SYNTHETIC")
print("----------------------------------------")
