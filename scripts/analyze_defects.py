import pandas as pd

FILE = "data/factory_process_data.csv"

df = pd.read_csv(FILE)

process_columns = [
    "current",
    "voltage",
    "temperature",
    "pressure",
    "welding_time",
    "speed"
]

print("=" * 60)
print("CELLGUARD DEFECT PROCESS ANALYSIS")
print("=" * 60)

for defect in df["defect_type"].unique():

    if defect == "None":
        continue

    defect_data = df[df["defect_type"] == defect]

    print(f"\nDEFECT: {defect}")
    print("-" * 40)

    print(f"Number of samples: {len(defect_data)}")

    for column in process_columns:
        print(
            f"{column:15s}: "
            f"{defect_data[column].mean():.2f}"
        )

print("\nAnalysis completed.")