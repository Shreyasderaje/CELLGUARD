import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


DATASET = "data/factory_process_data.csv"
MODEL_DIR = "models/risk_predictor"
MODEL_PATH = os.path.join(MODEL_DIR, "risk_model.pkl")

FEATURES = [
    "current",
    "voltage",
    "temperature",
    "pressure",
    "welding_time",
    "speed",
]


def main():

    print("=" * 60)
    print("CELLGUARD - DEFECT RISK PREDICTOR")
    print("=" * 60)

    df = pd.read_csv(DATASET)

    X = df[FEATURES]
    y = (df["defect_status"] == "Defect").astype(int)

    print(f"\nTotal samples: {len(df)}")
    print("\nClass distribution:")
    print(y.value_counts())

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    print("\nTraining risk predictor...")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("\n" + "=" * 60)
    print("RISK MODEL RESULTS")
    print("=" * 60)

    print(f"\nAccuracy: {accuracy:.3f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            target_names=["Normal", "Defect"],
            zero_division=0,
        )
    )

    importance = pd.Series(
        model.feature_importances_,
        index=FEATURES,
    ).sort_values(ascending=False)

    print("\nFeature Importance:")
    print(importance)

    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print("\n" + "=" * 60)
    print("RISK MODEL SAVED")
    print("=" * 60)
    print(f"Model: {MODEL_PATH}")


if __name__ == "__main__":
    main()