import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score


DATASET = "data/factory_process_data.csv"
MODEL_DIR = "models/root_cause"
MODEL_PATH = os.path.join(MODEL_DIR, "root_cause_model.pkl")


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
    print("CELLGUARD - ROOT CAUSE AI")
    print("=" * 60)

    # Load dataset
    df = pd.read_csv(DATASET)

    # Keep only defective samples
    df = df[df["defect_status"] == "Defect"].copy()

    X = df[FEATURES]
    y = df["defect_type"]

    print(f"\nDefective samples: {len(df)}")
    print(f"Features: {FEATURES}")
    print("\nTarget distribution:")
    print(y.value_counts())

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    # Random Forest
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    print("\nTraining Root Cause AI...")
    model.fit(X_train, y_train)

    # Evaluation
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("\n" + "=" * 60)
    print("MODEL RESULTS")
    print("=" * 60)

    print(f"\nAccuracy: {accuracy:.3f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    # Feature importance
    importance = pd.Series(
        model.feature_importances_,
        index=FEATURES,
    ).sort_values(ascending=False)

    print("\nFeature Importance:")
    print(importance)

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    print("\n" + "=" * 60)
    print("ROOT CAUSE MODEL SAVED")
    print("=" * 60)
    print(f"Model: {MODEL_PATH}")


if __name__ == "__main__":
    main()