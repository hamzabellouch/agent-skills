---
name: yolo-object-detection
metadata:
  category: Computer Vision and Spatial AI
description: >-
  Deploy state-of-the-art YOLO models (YOLOv8, YOLOv10, YOLO11) for real-time object detection, instance segmentation, and pose estimation.
  Triggers when training custom YOLO models, exporting to TensorRT FP16/INT8, running ONNX Runtime inference, executing ByteTrack multi-object tracking,
  or building high-throughput FastAPI/Triton inference services.
compatibility: Python (>= 3.9), Ultralytics (>= 8.1.0), PyTorch (>= 2.1), TensorRT (>= 8.6), ONNX Runtime GPU
---

# YOLO Object Detection & Tracking

End-to-end production pipelines for custom training, TensorRT quantization, multi-object tracking (ByteTrack), and real-time inference serving with YOLO.

---

## 1. Pipeline Architecture

```text
+---------------------+      +------------------------------+      +---------------------------+
| Custom Dataset      | ---> | YOLO Model Training          | ---> | Export to TensorRT        |
| (Roboflow / COCO)   |      | (PyTorch / Ultralytics)      |      | (FP16 / INT8 Calibration) |
+---------------------+      +------------------------------+      +---------------------------+
                                                                                 |
                                                                                 v
+---------------------+      +------------------------------+      +---------------------------+
| Stream Output       | <--- | Real-Time Multi-Object       | <--- | TensorRT Engine           |
| (Bounding Boxes/IDs)|      | Tracking (ByteTrack / BoT)   |      | High-Throughput Inference |
+---------------------+      +------------------------------+      +---------------------------+
```

---

## 2. Custom Dataset Definition & Model Training (`train_yolo.py`)

### Dataset YAML Config (`dataset.yaml`)

```yaml
path: /data/datasets/manufacturing_defects
train: images/train
val: images/val
test: images/test

names:
  0: scratch
  1: dent
  2: crack
```

### PyTorch Training Pipeline (`train_yolo.py`)

```python
from ultralytics import YOLO
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_custom_yolo():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    # Load baseline pre-trained YOLO model (e.g. YOLOv8x or YOLO11x)
    model = YOLO("yolov8x.pt")

    # Execute Distributed Training
    results = model.train(
        data="dataset.yaml",
        epochs=100,
        imgsz=640,
        batch=32,
        device=device,
        workers=8,
        optimizer="AdamW",
        lr0=0.001,
        weight_decay=0.0005,
        val=True,
        save=True,
        project="yolo_defects_project",
        name="experiment_v1"
    )

    # Validate trained model
    metrics = model.val()
    logger.info(f"mAP50-95: {metrics.box.map}")
    logger.info(f"mAP50: {metrics.box.map50}")

if __name__ == "__main__":
    train_custom_yolo()
```

---

## 3. TensorRT Export & INT8 Quantization (`export_tensorrt.py`)

Convert PyTorch `.pt` weights into high-performance NVIDIA TensorRT `.engine` models.

```python
from ultralytics import YOLO

def export_to_tensorrt():
    model = YOLO("yolo_defects_project/experiment_v1/weights/best.pt")

    # Export to TensorRT FP16 for maximum GPU throughput
    model.export(
        format="engine",
        imgsz=640,
        half=True,        # Enable FP16 Precision
        dynamic=False,     # Static shape for max performance
        workspace=4,       # 4GB GPU Workspace memory for engine building
        device=0
    )
    print("Successfully exported model to TensorRT Engine format.")

if __name__ == "__main__":
    export_to_tensorrt()
```

---

## 4. Multi-Object Tracking Pipeline with ByteTrack (`track_video.py`)

Combine YOLO object detection with ByteTrack to assign consistent IDs across video frames.

```python
import cv2
from ultralytics import YOLO
import numpy as np

def run_realtime_tracking(video_path: str, engine_path: str):
    # Load TensorRT Engine Model
    model = YOLO(engine_path, task="detect")

    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Execute Detection & Tracking using ByteTrack
        results = model.track(
            source=frame,
            persist=True,
            tracker="bytetrack.yaml", # Built-in ByteTrack config
            conf=0.4,
            iou=0.5,
            verbose=False
        )

        # Render Bounding Boxes with Track IDs
        annotated_frame = results[0].plot()

        # Extract Tracking Bounding Boxes and Object IDs
        if results[0].boxes and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            cls_ids = results[0].boxes.cls.int().cpu().numpy()

            for box, track_id, cls_id in zip(boxes, track_ids, cls_ids):
                x1, y1, x2, y2 = map(int, box)
                # Process individual tracked object (e.g. ROI cropping)

        cv2.imshow("Real-Time YOLO ByteTrack", annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_realtime_tracking("input_feed.mp4", "best.engine")
```

---

## 5. FastAPI High-Throughput Batch Serving (`serve_yolo.py`)

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from ultralytics import YOLO
import cv2
import numpy as np
import io
from PIL import Image

app = FastAPI(title="YOLO Real-Time Inference API", version="1.0.0")

# Load TensorRT Model Engine
MODEL = YOLO("best.engine", task="detect")

@app.post("/detect")
async def detect_objects(file: UploadFile = File(...), confidence: float = 0.5):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file format")

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    frame = np.array(image)

    # Run TensorRT Inference
    results = MODEL.predict(source=frame, conf=confidence, verbose=False)
    
    detections = []
    for box in results[0].boxes:
        coords = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        label = MODEL.names[cls_id]

        detections.append({
            "label": label,
            "confidence": round(conf, 4),
            "bbox": [round(c, 2) for c in coords]
        })

    return {"count": len(detections), "detections": detections}
```

---

## 6. Optimization Checklist for Production

1. **Resolution Sizing**: Match export resolution (`imgsz=640`) strictly with inference stream dimensions to prevent CPU resize overhead.
2. **TensorRT Engine Reuse**: Cache build engine files (`.engine`); avoid re-building engine files on container restart.
3. **Batching**: Group incoming API image frames into batch sizes of 4, 8, or 16 (`MODEL.predict(source=[f1, f2, f3, f4])`) for higher GPU throughput.
