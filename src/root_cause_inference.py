import joblib
import pandas as pd


MODEL_PATH = "models/root_cause/root_cause_model.pkl"

FEATURES = [
    "current",
    "voltage",
    "temperature",
    "pressure",
    "welding_time",
    "speed",
]

NORMAL_BASELINE = {
    "current": 190.0,
    "voltage": 24.5,
    "temperature": 85.0,
    "pressure": 4.5,
    "welding_time": 3.2,
    "speed": 12.0,
}


CAUSE_MAP = {
    "Burn_Through": {
        "current": "High welding current",
        "voltage": "High welding voltage",
        "temperature": "High welding temperature",
    },
    "Crack": {
        "temperature": "High welding temperature",
        "welding_time": "Short welding time",
    },
    "Incomplete_Weld": {
        "current": "Low welding current",
        "welding_time": "Short welding time",
        "speed": "High welding speed",
    },
    "Porosity": {
        "pressure": "Low welding pressure",
        "current": "High welding current",
        "temperature": "High welding temperature",
    },
}


def predict_root_cause(process_data):
    model = joblib.load(MODEL_PATH)

    row = pd.DataFrame([process_data])[FEATURES]

    prediction = model.predict(row)[0]
    probabilities = model.predict_proba(row)[0]

    confidence = max(probabilities)

    causes = CAUSE_MAP.get(prediction, {})

    deviations = []

    for feature, description in causes.items():
        value = float(process_data[feature])
        baseline = NORMAL_BASELINE[feature]

        if feature == "speed":
            abnormal = value > baseline * 1.10
        elif feature == "pressure":
            abnormal = value < baseline * 0.90
        else:
            abnormal = (
                value > baseline * 1.10
                or value < baseline * 0.90
            )

        if abnormal:
            deviations.append(
                {
                    "parameter": feature,
                    "description": description,
                    "value": value,
                    "baseline": baseline,
                }
            )

    if deviations:
        primary = deviations[0]
        explanation = (
            f"{primary['description']} may be contributing to "
            f"{prediction.replace('_', ' ')}. "
            f"Observed {primary['parameter']} = "
            f"{primary['value']:.2f}, compared with normal baseline "
            f"{primary['baseline']:.2f}."
        )
    else:
        explanation = (
            f"The process pattern resembles {prediction.replace('_', ' ')}, "
            f"but no major parameter deviation was detected against "
            f"the normal baseline."
        )

    return {
        "predicted_cause": prediction,
        "confidence": round(float(confidence), 3),
        "explanation": explanation,
        "evidence": deviations,
    }


if __name__ == "__main__":

    sample = {
        "current": 230,
        "voltage": 27,
        "temperature": 120,
        "pressure": 4.5,
        "welding_time": 3.2,
        "speed": 12,
    }

    result = predict_root_cause(sample)

    print("\nCELLGUARD ROOT CAUSE INFERENCE")
    print("=" * 45)
    print("Predicted cause :", result["predicted_cause"])
    print("Confidence      :", result["confidence"])
    print("Explanation     :", result["explanation"])
    print("Evidence        :", result["evidence"])