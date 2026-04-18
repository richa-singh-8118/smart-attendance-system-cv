"""
surveillance_extension.py
--------------------------
Extension module demonstrating how the Smart Attendance System can be adapted
for real-world monitoring applications such as:
  - Perimeter / entry-point surveillance
  - Safety zone access-control logging
  - Crowd & motion anomaly detection
  - Intruder alerting with evidence capture

This module is intentionally decoupled from the core attendance pipeline so it
can be swapped, expanded, or integrated with external alerting services
(e-mail, SMS, RTSP streams, IoT sensors) without touching the attendance logic.
"""

import cv2
import os
import time
import csv
from datetime import datetime


# ---------------------------------------------------------------------------
# Configuration (override via constructor kwargs for production deployments)
# ---------------------------------------------------------------------------
DEFAULT_ZONE       = "Restricted Zone - Server Room"
DEFAULT_LOG_FOLDER = "database/surveillance_logs"
CROWD_THRESHOLD    = 3          # flag if more than N faces detected simultaneously
MOTION_SENSITIVITY = 500        # minimum contour area to count as motion
UNKNOWN_SAVE_COOLDOWN = 5       # seconds between unknown-face saves


class SurveillanceMonitor:
    """
    Wraps OpenCV camera feed with safety/surveillance analytics.
    Works standalone OR alongside FaceRecognizer for enriched monitoring.
    """

    def __init__(
        self,
        known_names: list = None,
        zone: str = DEFAULT_ZONE,
        log_folder: str = DEFAULT_LOG_FOLDER,
        crowd_threshold: int = CROWD_THRESHOLD,
    ):
        self.known_names       = known_names or []
        self.zone              = zone
        self.log_folder        = log_folder
        self.crowd_threshold   = crowd_threshold
        self._last_unknown_ts  = 0
        self._bg_subtractor    = cv2.createBackgroundSubtractorMOG2(
            history=200, varThreshold=50, detectShadows=False
        )
        self._face_cascade     = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        os.makedirs(self.log_folder, exist_ok=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _log_event(self, event_type: str, detail: str):
        """Append a timestamped row to the daily surveillance CSV."""
        now      = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        log_path = os.path.join(self.log_folder, f"Surveillance_{date_str}.csv")
        file_exists = os.path.isfile(log_path)
        with open(log_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Date", "Time", "Event", "Detail", "Zone"])
            writer.writerow([date_str, time_str, event_type, detail, self.zone])

    def _save_evidence(self, frame, label: str):
        """Save a JPEG snapshot as surveillance evidence."""
        evidence_dir = os.path.join(self.log_folder, "evidence")
        os.makedirs(evidence_dir, exist_ok=True)
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(evidence_dir, f"{label}_{ts}.jpg")
        cv2.imwrite(path, frame)
        return path

    # ------------------------------------------------------------------
    # Detection routines
    # ------------------------------------------------------------------

    def detect_motion(self, frame) -> bool:
        """Returns True when significant motion is detected in the frame."""
        fg_mask = self._bg_subtractor.apply(frame)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return any(cv2.contourArea(c) > MOTION_SENSITIVITY for c in contours)

    def detect_faces(self, frame):
        """Returns list of (x, y, w, h) bounding boxes for all detected faces."""
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        return faces if len(faces) > 0 else []

    def handle_unknown_face(self, frame, face_box):
        """Logs and optionally saves evidence of an unrecognised face."""
        now = time.time()
        if now - self._last_unknown_ts > UNKNOWN_SAVE_COOLDOWN:
            path = self._save_evidence(frame, "intruder")
            self._log_event("INTRUDER_ALERT", f"Unknown face detected. Evidence: {os.path.basename(path)}")
            self._last_unknown_ts = now
            return True
        return False

    def handle_crowd_event(self, frame, face_count: int):
        """Logs a crowd-density alert when face count exceeds threshold."""
        self._log_event("CROWD_ALERT", f"{face_count} faces detected simultaneously")
        self._save_evidence(frame, "crowd_alert")

    def check_access_violation(self, name: str, frame):
        """
        Placeholder for zone-based access-control logic.
        In production, replace `allowed_names` with a DB/API lookup.
        """
        allowed_names = self.known_names  # all trained persons are 'authorised' by default
        if name not in allowed_names and name != "Unknown":
            self._log_event("ACCESS_VIOLATION", f"{name} attempted entry to {self.zone}")
            self._save_evidence(frame, f"access_violation_{name}")
            return True
        return False

    # ------------------------------------------------------------------
    # Standalone surveillance loop (runs without face_recognition lib)
    # ------------------------------------------------------------------

    def start_monitoring(self):
        """
        Lightweight surveillance loop using only OpenCV (no dlib required).
        Detects motion, counts faces, flags crowds, and logs everything.
        Press 'q' to quit.
        """
        cap = cv2.VideoCapture(0)
        print(f"[SurveillanceMonitor] Monitoring zone: '{self.zone}'. Press Q to quit.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            overlay = frame.copy()

            # --- Motion Detection ---
            motion_detected = self.detect_motion(frame)
            if motion_detected:
                cv2.putText(overlay, "MOTION DETECTED", (10, 30),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 165, 255), 2)

            # --- Face / Crowd Detection ---
            faces = self.detect_faces(frame)
            face_count = len(faces)

            for (x, y, w, h) in faces:
                cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 255), 2)
                cv2.putText(overlay, "Face", (x, y - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

            if face_count > self.crowd_threshold:
                self.handle_crowd_event(frame, face_count)
                cv2.putText(overlay, f"CROWD ALERT ({face_count} faces)", (10, 65),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)

            # --- Zone label & stats ---
            cv2.putText(overlay, f"Zone: {self.zone}", (10, frame.shape[0] - 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
            cv2.putText(overlay, datetime.now().strftime("%Y-%m-%d  %H:%M:%S"),
                        (10, frame.shape[0] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

            cv2.imshow("Surveillance Monitor", overlay)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()
        print("[SurveillanceMonitor] Monitoring stopped.")


# ---------------------------------------------------------------------------
# Quick standalone test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    monitor = SurveillanceMonitor(zone="Main Entrance - Building A")
    monitor.start_monitoring()
