---
name: opencv-computer-vision
metadata:
  category: Computer Vision and Spatial AI
description: >-
  Implement production-grade computer vision pipelines using OpenCV (C++ and Python) with CUDA acceleration.
  Triggers when processing real-time multi-threaded RTSP camera streams, zero-copy memory transfers, image pre-processing,
  contour analysis, optical flow tracking, feature detection/matching (ORB, SIFT), camera calibration, or 3D spatial pose estimation (PnP).
compatibility: OpenCV (>= 4.8.0 with CUDA support), Python (>= 3.9) / C++17, NumPy, CUDA (>= 11.8)
---

# OpenCV Computer Vision & Spatial AI

Production implementations for GPU-accelerated image processing, multi-threaded RTSP video streaming, feature tracking, camera calibration, and 3D spatial position estimation.

---

## 1. Computer Vision Architecture

```text
+-------------------+      +--------------------------------+      +---------------------------+
| RTSP IP Camera    | ---> | Multi-Threaded VideoReader     | ---> | CUDA GpuMat Memory Transfer|
| (1080p @ 60 FPS)  |      | (Thread-safe Queue Buffer)     |      | (Zero CPU-GPU copy bottleneck)|
+-------------------+      +--------------------------------+      +---------------------------+
                                                                                 |
                                                                                 v
+-------------------+      +--------------------------------+      +---------------------------+
| Spatial 3D Pose   | <--- | Feature Detection & PnP        | <--- | GPU Pre-processing        |
| (X, Y, Z, R, P, Y)|      | (SolvePnP / ArUco Marker)      |      | (Threshold, Blur, Contours)|
+-------------------+      +--------------------------------+      +---------------------------+
```

---

## 2. Multi-Threaded RTSP Stream Reader (`rtsp_reader.py`)

A non-blocking, thread-safe RTSP video ingest pipeline with automatic reconnect logic to prevent frame dropping.

```python
import cv2
import threading
import queue
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustVideoSubscriber:
    def __init__(self, rtsp_url: str, max_queue_size: int = 5):
        self.rtsp_url = rtsp_url
        self.frame_queue = queue.Queue(maxsize=max_queue_size)
        self.stopped = False
        self.cap = None
        self.thread = threading.Thread(target=self._update, daemon=True)

    def start(self):
        self._connect()
        self.thread.start()
        return self

    def _connect(self):
        logger.info(f"Connecting to RTSP stream: {self.rtsp_url}")
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Force minimal buffering latency

    def _update(self):
        while not self.stopped:
            if not self.cap or not self.cap.isOpened():
                logger.warning("Stream disconnected. Attempting reconnect...")
                time.sleep(2.0)
                self._connect()
                continue

            grabbed, frame = self.cap.read()
            if not grabbed:
                logger.warning("Failed to grab frame. Reconnecting...")
                self.cap.release()
                time.sleep(1.0)
                self._connect()
                continue

            # Drop oldest frame if queue is full to enforce real-time processing
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass

            self.frame_queue.put(frame)

    def read(self):
        """Fetch latest frame non-blocking."""
        try:
            return True, self.frame_queue.get(timeout=1.0)
        except queue.Empty:
            return False, None

    def stop(self):
        self.stopped = True
        if self.thread.is_alive():
            self.thread.join()
        if self.cap:
            self.cap.release()
        logger.info("RTSP subscriber stopped.")
```

---

## 3. CUDA GPU-Accelerated Image Pre-Processing (`gpu_pipeline.py`)

Use OpenCV's `cuda::GpuMat` interface to perform image filtering and thresholding on NVIDIA GPUs.

```python
import cv2
import numpy as np

def process_frame_cuda(cpu_frame: np.ndarray) -> np.ndarray:
    """Uploads frame to GPU, performs processing, and downloads result."""
    # 1. Upload CPU NumPy Mat to GPU GpuMat
    gpu_frame = cv2.cuda_GpuMat()
    gpu_frame.upload(cpu_frame)

    # 2. BGR to Grayscale on GPU
    gpu_gray = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2GRAY)

    # 3. Gaussian Blur on GPU
    gpu_filter = cv2.cuda.createGaussianFilter(cv2.CV_8UC1, cv2.CV_8UC1, (5, 5), 1.5)
    gpu_blurred = gpu_filter.apply(gpu_gray)

    # 4. Binary Thresholding on GPU
    _, gpu_thresh = cv2.cuda.threshold(gpu_blurred, 127, 255, cv2.THRESH_BINARY)

    # 5. Download result back to CPU memory
    output_frame = gpu_thresh.download()
    return output_frame
```

---

## 4. 3D Spatial Pose Estimation with SolvePnP (`spatial_pose.py`)

Compute the 3D position and orientation $(X, Y, Z)$ of a physical object relative to the camera lens.

```python
import cv2
import numpy as np

class SpatialPoseEstimator:
    def __init__(self, camera_matrix: np.ndarray, dist_coeffs: np.ndarray):
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs

        # Define 3D model points of a rectangular object in physical world space (in millimeters)
        self.model_3d_points = np.array([
            [-50.0, -25.0, 0.0],  # Top-left
            [ 50.0, -25.0, 0.0],  # Top-right
            [ 50.0,  25.0, 0.0],  # Bottom-right
            [-50.0,  25.0, 0.0]   # Bottom-left
        ], dtype=np.float32)

    def estimate_pose(self, image_2d_points: np.ndarray):
        """
        Calculates Rotation vector (rvec) and Translation vector (tvec).
        image_2d_points: Array of 4 detected corner pixels [[x1, y1], [x2, y2], ...]
        """
        success, rvec, tvec = cv2.solvePnP(
            self.model_3d_points,
            image_2d_points.astype(np.float32),
            self.camera_matrix,
            self.dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return None

        # Convert rotation vector to 3x3 rotation matrix
        rmat, _ = cv2.Rodrigues(rvec)

        # Distance from camera lens in millimeters
        distance_mm = np.linalg.norm(tvec)

        return {
            "x_mm": float(tvec[0][0]),
            "y_mm": float(tvec[1][0]),
            "z_mm": float(tvec[2][0]),
            "distance_mm": float(distance_mm),
            "rotation_matrix": rmat
        }
```

---

## 5. Feature Detection & Optical Flow Object Tracking (`feature_tracking.py`)

```python
import cv2
import numpy as np

class LucasKanadeTracker:
    def __init__(self):
        # Parameters for ShiTomasi corner detection
        self.feature_params = dict(
            maxCorners=100,
            qualityLevel=0.3,
            minDistance=7,
            blockSize=7
        )
        # Parameters for Lucas-Kanade optical flow
        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERMCRITERIA_EPS | cv2.TERMCRITERIA_COUNT, 10, 0.03)
        )
        self.old_gray = None
        self.p0 = None

    def track(self, frame: np.ndarray):
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.old_gray is None or self.p0 is None or len(self.p0) < 10:
            # Initialize keypoints to track
            self.p0 = cv2.goodFeaturesToTrack(frame_gray, mask=None, **self.feature_params)
            self.old_gray = frame_gray.copy()
            return frame

        # Calculate Optical Flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, self.p0, None, **self.lk_params)

        # Select good points
        if p1 is not None:
            good_new = p1[st == 1]
            good_old = self.p0[st == 1]

            # Draw vectors
            for new, old in zip(good_new, good_old):
                a, b = new.ravel()
                c, d = old.ravel()
                frame = cv2.line(frame, (int(a), int(b)), (int(c), int(d)), (0, 255, 0), 2)
                frame = cv2.circle(frame, (int(a), int(b)), 4, (0, 0, 255), -1)

            self.old_gray = frame_gray.copy()
            self.p0 = good_new.reshape(-1, 1, 2)

        return frame
```

---

## 6. Performance Benchmarks & Optimization

1. **Avoid Frequent CPU-GPU Transfers**: Maintain processing in `cuda::GpuMat` memory across sequential operations; convert back to CPU `np.ndarray` only when displaying or storing frames.
2. **Pre-allocated Output Buffers**: Pass existing arrays as output parameters (`cv2.cvtColor(src, code, dst=existing_mat)`) inside high-frequency loops to prevent memory re-allocations.
3. **Camera Matrix Calibration**: Always calibrate camera intrinsics using `cv2.calibrateCamera` with chessboard patterns prior to 3D spatial pose estimation tasks.
