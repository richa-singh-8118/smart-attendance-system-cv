# Smart Attendance System — Face Recognition

A modular, production-oriented Python application that automates employee
attendance tracking via real-time face recognition, and can be extended
into broader surveillance and safety monitoring scenarios.

---

### 🌐 [Live Web Dashboard](https://smart-attendance-system-cv.streamlit.app/)
*(Deploy your `app_web.py` to Streamlit Cloud to activate this link!)*

---

## Key Highlights

### 1 · Modular Architecture
Four independent, interchangeable components:

| Module | Responsibility |
|---|---|
| `face_capture.py` | Webcam-based user registration — captures training images |
| `face_train.py` | Encodes captured images with `dlib` / `face_recognition` |
| `face_recognize.py` | Live recognition with liveness detection (blink verification) |
| `attendance_manager.py` | Thread-safe CSV attendance logging |
| `surveillance_extension.py` | Standalone safety / monitoring extension (see §3) |
| `main.py` | Tkinter GUI dashboard wiring all modules together |

### 2 · Automated Attendance Logging
`attendance_manager.py` writes a date-stamped CSV (`database/Attendance_YYYY-MM-DD.csv`) with:
- **Timestamp** — exact `HH:MM:SS` of first verified recognition
- **Location tagging** — configurable zone string (e.g. "Office – Main Gate")
- **Late detection** — compares arrival time against a configurable threshold (default `09:15:00`); records `On Time` or `Late`
- **Duplicate guard** — each person is marked at most once per day

CSV columns: `Name | Time | Date | Location | Status`

### 3 · Surveillance & Safety Extension
`surveillance_extension.py` demonstrates how the same webcam pipeline can
power real-world monitoring scenarios:

| Capability | Description |
|---|---|
| **Motion detection** | Background-subtraction (MOG2) flags movement in any zone |
| **Crowd alerting** | Triggers when simultaneous face count exceeds configurable threshold |
| **Intruder alerting** | Unrecognised faces are logged + JPEG evidence saved to `database/surveillance_logs/evidence/` |
| **Zone-based access control** | `check_access_violation()` hook for whitelist / DB integration |
| **Daily audit log** | All events written to `database/surveillance_logs/Surveillance_YYYY-MM-DD.csv` |

Designed for extension to RTSP camera streams, IoT sensor triggers,
e-mail/SMS alert dispatch, and integration with NVR/VMS platforms.

---

## Project Structure

```
Smart Attendance System/
├── main.py                    # Tkinter GUI (Registration · Training · Recognition · Surveillance)
├── face_capture.py            # Webcam face-image capture
├── face_train.py              # dlib encoding + pickle serialisation
├── face_recognize.py          # Real-time recognition with liveness check
├── attendance_manager.py      # CSV attendance logger
├── surveillance_extension.py  # Safety / monitoring extension module
├── requirements.txt
├── dataset/                   # Auto-created: raw user images
└── database/
    ├── encodings.pickle        # Trained face encodings
    ├── Attendance_YYYY-MM-DD.csv
    ├── unknown_faces/          # Snapshots of unrecognised faces
    └── surveillance_logs/      # Motion / crowd / intruder event logs
        └── evidence/           # JPEG evidence captures
```

---

## Setup

### Requirements
Python 3.7+ · Windows users need MSVC C++ Build Tools + CMake for `dlib`.

```bash
pip install -r requirements.txt
```

> **dlib trouble on Windows?**  
> `pip install cmake` then install a precompiled dlib wheel matching your Python version.

### Run

```bash
python main.py
```

---

## Workflow

1. **Register** — enter a name → *Capture Faces* (webcam opens, captures 5 images)
2. **Train** — click *Train Database* (extracts dlib encodings, saves to `database/`)
3. **Recognise** — click *Start Recognition App*; blink once to verify liveness →
   attendance is auto-logged
4. **Surveillance** — set a zone label → *Start Surveillance* for lightweight
   motion + crowd + intruder monitoring (no dlib required)
5. **Dashboard** — run `streamlit run app_web.py` to view analytics and evidence.

---

## 🚀 Deployment

### Web Dashboard
1. Push this repo to GitHub.
2. Sign in to [Streamlit Cloud](https://share.streamlit.io).
3. Click "New App" and select this repository.
4. Set the main file path to `app_web.py`.
5. Your dashboard is now live!

### Windows Executable
Run `python build_exe.py` to generate a standalone `.exe` in the `dist/` folder.

