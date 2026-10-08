# CELLGUARD Factory Process Dataset

Synthetic manufacturing process data for the CELLGUARD
EV battery welding quality inspection system.

## Dataset

File: `factory_process_data.csv`

Records: 5000

## Features

| Feature | Description |
|---|---|
| batch_id | Manufacturing batch ID |
| machine_id | Welding machine ID |
| timestamp | Production timestamp |
| current | Welding current |
| voltage | Welding voltage |
| temperature | Welding temperature |
| pressure | Welding pressure |
| welding_time | Welding duration |
| speed | Welding speed |
| defect_status | Normal or Defect |
| defect_type | Type of welding defect |

## Defect Types

- Porosity
- Crack
- Incomplete_Weld
- Burn_Through

## Purpose

The dataset is used to correlate manufacturing process
conditions with detected welding defects.

This enables Root Cause Analysis and Future Defect Risk
Prediction in the CELLGUARD system.

## Data Type

This is SYNTHETIC data generated for hackathon
prototyping and demonstration.

It is not real factory or proprietary data.