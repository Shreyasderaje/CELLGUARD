import pandas as pd

FILE = "data/factory_process_data.csv"

df = pd.read_csv(FILE)

print("=" * 50)
print("CELLGUARD DATASET VALIDATION")
print("=" * 50)

print(f"Total records : {len(df)}")
print(f"Total columns : {len(df.columns)}")

print("\nColumns:")
for column in df.columns:
    print("-", column)

print("\nDefect distribution:")
print(df["defect_type"].value_counts())

print("\nMachine distribution:")
print(df["machine_id"].value_counts())

print("\nMissing values:")
print(df.isnull().sum())

print("\nProcess statistics:")
print(
    df[
        [
            "current",
            "voltage",
            "temperature",
            "pressure",
            "welding_time",
            "speed"
        ]
    ].describe()
)

print("\nDataset validation completed.")