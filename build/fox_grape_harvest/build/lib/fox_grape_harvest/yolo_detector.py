"""
YOLO 葡萄检测模块
加载预训练 YOLO 模型（ultralytics .pt / .onnx），对 RGB 图像进行推理。
"""
import numpy as np
import cv2


class YoloDetector:
    """YOLO 目标检测封装，支持 ultralytics YOLOv8/YOLOv11."""

    def __init__(self, model_path: str, confidence: float = 0.5, target_class: str = "grape"):
        """
        初始化检测器。
        Args:
            model_path: .pt 或 .onnx 模型文件路径
            confidence: 检测置信度阈值
            target_class: 目标类别名称（如 "grape"）
        """
        self.confidence = confidence
        self.target_class = target_class
        self.model_path = model_path
        self.model = None
        self.class_names = []
        self._load_model()

    def _load_model(self):
        """加载 YOLO 模型（延迟导入避免依赖缺失崩溃）。"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            # 获取类别名
            if hasattr(self.model, 'names'):
                self.class_names = self.model.names
            elif hasattr(self.model, 'model') and hasattr(self.model.model, 'names'):
                self.class_names = self.model.model.names
            else:
                self.class_names = {}
            print(f"[YOLO] 模型已加载: {self.model_path}")
            print(f"[YOLO] 类别: {self.class_names}")
        except ImportError:
            print("[YOLO] ⚠ ultralytics 未安装，将使用 OpenCV DNN 回退模式")
            self._load_opencv_dnn()
        except Exception as e:
            print(f"[YOLO] ❌ 加载失败: {e}")
            raise

    def _load_opencv_dnn(self):
        """回退: 使用 OpenCV DNN 加载 ONNX 模型。"""
        try:
            self.net = cv2.dnn.readNetFromONNX(self.model_path)
            print(f"[YOLO] OpenCV DNN 加载 ONNX: {self.model_path}")
            # ONNX 模型无类别名，预设
            self.class_names = {0: self.target_class}
        except Exception as e:
            print(f"[YOLO] ❌ OpenCV DNN 也失败: {e}")
            raise

    def detect(self, cv_image: np.ndarray):
        """
        在 RGB 图像上检测目标。
        Args:
            cv_image: BGR 格式图像 (H, W, 3)
        Returns:
            list[dict]: 每个检测结果包含:
                - 'bbox': [x1, y1, x2, y2] 像素坐标
                - 'center': (cx, cy) 中心点像素
                - 'confidence': float
                - 'class_name': str
                - 'class_id': int
        """
        results = []
        if self.model is not None:
            # ultralytics 模式
            predictions = self.model(cv_image, verbose=False)
            boxes = predictions[0].boxes
            if boxes is not None and len(boxes) > 0:
                for box in boxes:
                    conf = float(box.conf[0])
                    if conf < self.confidence:
                        continue
                    cls_id = int(box.cls[0])
                    cls_name = self.class_names.get(cls_id, str(cls_id))
                    if cls_name != self.target_class:
                        continue
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    results.append({
                        'bbox': [x1, y1, x2, y2],
                        'center': (cx, cy),
                        'confidence': conf,
                        'class_name': cls_name,
                        'class_id': cls_id,
                    })
        else:
            # OpenCV DNN 回退
            results = self._detect_opencv(cv_image)

        return results

    def _detect_opencv(self, cv_image):
        """OpenCV DNN ONNX 推理回退。"""
        results = []
        if not hasattr(self, 'net'):
            return results

        # ONNX 前处理（假设 YOLOv8 格式）
        blob = cv2.dnn.blobFromImage(cv_image, 1/255.0, (640, 640), swapRB=True, crop=False)
        self.net.setInput(blob)
        try:
            out = self.net.forward()[0]  # shape: (84, 8400)
            out = out.transpose()
            for det in out:
                conf = float(det[4])
                if conf < self.confidence:
                    continue
                # 类别概率
                scores = det[5:]
                cls_id = int(np.argmax(scores))
                cls_conf = float(scores[cls_id])
                if cls_conf * conf < self.confidence:
                    continue
                cls_name = self.class_names.get(cls_id, str(cls_id))
                if cls_name != self.target_class:
                    continue

                # 反算到原图坐标
                xc, yc, w, h = det[:4]
                h_img, w_img = cv_image.shape[:2]
                x1 = int((xc - w/2) * w_img / 640)
                y1 = int((yc - h/2) * h_img / 640)
                x2 = int((xc + w/2) * w_img / 640)
                y2 = int((yc + h/2) * h_img / 640)
                results.append({
                    'bbox': [x1, y1, x2, y2],
                    'center': ((x1+x2)//2, (y1+y2)//2),
                    'confidence': conf * cls_conf,
                    'class_name': cls_name,
                    'class_id': cls_id,
                })
        except Exception as e:
            print(f"[YOLO] ONNX 推理异常: {e}")

        return results

    def draw_detections(self, cv_image: np.ndarray, detections: list) -> np.ndarray:
        """在图像上绘制检测结果（调试用途）。"""
        img = cv_image.copy()
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            cx, cy = det['center']
            conf = det['confidence']
            # 画框
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # 画中心点
            cv2.circle(img, (cx, cy), 4, (0, 0, 255), -1)
            # 标签
            label = f"{det['class_name']}: {conf:.2f}"
            cv2.putText(img, label, (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return img
