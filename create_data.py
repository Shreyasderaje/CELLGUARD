import pandas as pd
import numpy as np

np.random.seed(42)

causes = [
    ("Crack", "High vibration"),
    ("Burn mark", "High temperature"),
    ("Deformation", "High pressure"),
    ("Scratch", "High machine speed"),
    ("Porosity", "Unstable temperature")
]

rows = []

for i in range(500):
    defect_type, cause = causes[np.random.randint(len(causes))]

    temperature = np.random.normal(200, 20)
    pressure = np.random.normal(70, 10)
    machine_speed = np.random.normal(1200, 150)
    vibration = np.random.normal(5, 1)

    if cause == "High vibration":
        vibration += 4
    elif cause == "High temperature":
        temperature += 50
    elif cause == "High pressure":
        pressure += 25
    elif cause == "High machine speed":
        machine_speed += 400
    elif cause == "Unstable temperature":
        temperature += np.random.choice([-50, 50])

    rows.append([
        f"CELL-{i+1:04d}",
        f"BATCH-{(i//50)+1:03d}",
        f"M{(i%5)+1:02d}",
        f"2026-10-{(i%7)+1:02d} {(i%24):02d}:00:00",
        round(temperature, 2),
        round(pressure, 2),
        round(machine_speed, 2),
        round(vibration, 2),
        defect_type,
        1
    ])

df = pd.DataFrame(rows, columns=[
    "cell_id", "batch_id", "machine_id", "timestamp",
    "temperature", "pressure", "machine_speed", "vibration",
    "defect_type", "defect_present"
])

df.to_csv("data/synthetic/factory_process_data.csv", index=False)

print("Factory dataset created successfully!")
print("Rows:", len(df))
