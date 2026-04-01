"""Face Detection Module using MediaPipe."""

from typing import List, Optional
import cv2
import mediapipe as mp
from src.models.data_models import Face, Expression
from src.utils.logger import Logger


class FaceDetectionModule:
    """Detects faces and analyzes facial expressions."""

    def __init__(self, enable_camera: bool = True):
        """Initialize face detection module.
        
        Args:
            enable_camera: Whether to enable camera access
        """
        self.enable_camera = enable_camera
        self.logger = Logger("FaceDetectionModule")
        self.camera = None
        self.face_detector = None
        self.is_camera_available = False
        self._initialize_detector()

    def _initialize_detector(self) -> None:
        """Initialize MediaPipe face detector."""
        try:
            mp_face_detection = mp.solutions.face_detection
            self.face_detector = mp_face_detection.FaceDetection(
                model_selection=0,
                min_detection_confidence=0.5
            )
            self.logger.info("Face detector initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize face detector: {e}")

    def start_camera(self) -> bool:
        """Start camera access.
        
        Returns:
            True if camera started successfully, False otherwise
        """
        try:
            if not self.enable_camera:
                self.logger.warning("Camera is disabled")
                return False

            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.logger.error("Failed to open camera")
                return False

            self.is_camera_available = True
            self.logger.info("Camera started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start camera: {e}")
            return False

    def stop_camera(self) -> None:
        """Stop camera access."""
        try:
            if self.camera:
                self.camera.release()
                self.is_camera_available = False
                self.logger.info("Camera stopped")
        except Exception as e:
            self.logger.error(f"Failed to stop camera: {e}")

    def detect_faces(self, frame: Optional[bytes] = None) -> List[Face]:
        """Detect faces in frame.
        
        Args:
            frame: Frame data (if None, captures from camera)
            
        Returns:
            List of detected faces
        """
        try:
            if frame is None:
                if not self.camera or not self.is_camera_available:
                    return []

                ret, frame = self.camera.read()
                if not ret:
                    return []

            # Convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect faces
            results = self.face_detector.process(frame_rgb)

            faces = []
            if results.detections:
                for idx, detection in enumerate(results.detections):
                    bbox = detection.location_data.relative_bounding_box
                    h, w, _ = frame.shape

                    # Convert to pixel coordinates
                    x = int(bbox.xmin * w)
                    y = int(bbox.ymin * h)
                    width = int(bbox.width * w)
                    height = int(bbox.height * h)

                    face = Face(
                        face_id=idx,
                        landmarks=[],  # Would extract from detection
                        bounding_box=(x, y, width, height),
                        confidence=detection.score[0] if detection.score else 0.0
                    )
                    faces.append(face)

            self.logger.info(f"Detected {len(faces)} faces")
            return faces

        except Exception as e:
            self.logger.error(f"Face detection failed: {e}")
            return []

    def get_facial_landmarks(self, face: Face) -> List[tuple]:
        """Get facial landmarks for a face.
        
        Args:
            face: Face object
            
        Returns:
            List of landmark coordinates
        """
        # Mock implementation - would extract from MediaPipe
        return face.landmarks

    def analyze_expression(self, face: Face) -> Optional[Expression]:
        """Analyze facial expression.
        
        Args:
            face: Face object
            
        Returns:
            Expression classification or None
        """
        try:
            # Mock implementation - would use actual expression analysis
            # In production, would use facial landmarks to classify expression
            return Expression(
                expression_type="neutral",
                confidence=0.8,
                intensity=0.5
            )

        except Exception as e:
            self.logger.error(f"Expression analysis failed: {e}")
            return None

    def is_camera_available(self) -> bool:
        """Check if camera is available.
        
        Returns:
            True if camera is available, False otherwise
        """
        return self.is_camera_available

    def get_model_info(self) -> dict:
        """Get information about face detection module.
        
        Returns:
            Dictionary with module information
        """
        return {
            "enable_camera": self.enable_camera,
            "is_camera_available": self.is_camera_available,
            "detector_initialized": self.face_detector is not None
        }
