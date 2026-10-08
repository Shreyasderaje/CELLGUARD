import pandas as pd

def explain_root_cause(defect_type, temperature, pressure, machine_speed, vibration):

    scores = {
        "High vibration": 0,
        "High temperature": 0,
        "High pressure": 0,
        "High machine speed": 0
    }

    if vibration > 7:
        scores["High vibration"] += 0.8

    if temperature > 230:
        scores["High temperature"] += 0.8

    if pressure > 90:
        scores["High pressure"] += 0.8

    if machine_speed > 1500:
        scores["High machine speed"] += 0.8

    if defect_type == "Crack":
        scores["High vibration"] += 0.2
    elif defect_type == "Burn mark":
        scores["High temperature"] += 0.2
    elif defect_type == "Deformation":
        scores["High pressure"] += 0.2
    elif defect_type == "Scratch":
        scores["High machine speed"] += 0.2
    elif defect_type == "Porosity":
        scores["High temperature"] += 0.2

    cause = max(scores, key=scores.get)
    confidence = min(scores[cause], 1.0)

    actions = {
        "High vibration": "Inspect machine vibration and check machine alignment.",
        "High temperature": "Check temperature control and cooling system.",
        "High pressure": "Inspect pressure settings and machine calibration.",
        "High machine speed": "Reduce machine speed and inspect tooling."
    }

    return {
        "probable_cause": cause,
        "confidence": round(confidence * 100, 1),
        "recommended_action": actions[cause]
    }


if __name__ == "__main__":

    df = pd.read_csv("data/synthetic/factory_process_data.csv")

    sample = df.iloc[0]

    result = explain_root_cause(
        sample["defect_type"],
        sample["temperature"],
        sample["pressure"],
        sample["machine_speed"],
        sample["vibration"]
    )

    print("\nCELLGUARD ROOT-CAUSE ANALYSIS")
    print("--------------------------------")
    print("Defect:", sample["defect_type"])
    print("Machine:", sample["machine_id"])
    print("Probable Cause:", result["probable_cause"])
    print("Confidence:", str(result["confidence"]) + "%")
    print("Corrective Action:", result["recommended_action"])
