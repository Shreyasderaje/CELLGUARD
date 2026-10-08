from ultralytics import YOLO


DATASET = "data/raw/weld_defect/data.yaml"
MODEL = "yolo11n.pt"


def main():
    model = YOLO(MODEL)

    model.train(
        data=DATASET,
        epochs=10,
        imgsz=640,
        batch=8,
        device=0,
        project="models/defect_detector",
        name="cellguard_yolo",
    )


if __name__ == "__main__":
    main()