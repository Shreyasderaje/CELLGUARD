import joblib
import pandas as pd


MODEL_PATH = "models/risk_predictor/risk_model.pkl"

FEATURES = [
    "current",
    "voltage",
    "temperature",
    "pressure",
    "welding_time",
    "speed",
]


def predict_risk(process_data):

    model = joblib.load(MODEL_PATH)

    row = pd.DataFrame([process_data])[FEATURES]

    probability = model.predict_proba(row)[0][1]

    risk_percentage = probability * 100

    if risk_percentage >= 70:
        risk_level = "HIGH"
    elif risk_percentage >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    importances = pd.Series(
        model.feature_importances_,
        index=FEATURES,
    ).sort_values(ascending=False)

    contributors = []

    for feature in importances.index[:3]:

        contributors.append({
            "parameter": feature,
            "importance": round(
                float(importances[feature]),
                3
            ),
            "value": round(
                float(process_data[feature]),
                2
            ),
        })

    return {
        "risk_probability": round(risk_percentage, 2),
        "risk_level": risk_level,
        "contributors": contributors,
    }


if __name__ == "__main__":

    sample = {
        "current": 230,
        "voltage": 27,
        "temperature": 120,
        "pressure": 4.2,
        "welding_time": 2.8,
        "speed": 12,
    }

    result = predict_risk(sample)

    print("\nCELLGUARD RISK ENGINE")
    print("=" * 45)

    print(
        f"Defect Risk : "
        f"{result['risk_probability']:.2f}%"
    )

    print(
        f"Risk Level  : "
        f"{result['risk_level']}"
    )

    print("\nTop Contributors:")

    for item in result["contributors"]:
        print(
            f"{item['parameter']}: "
            f"{item['value']} "
            f"(importance={item['importance']})"
        )