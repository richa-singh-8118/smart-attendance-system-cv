import cv2
import os
import time

def _open_camera():
    """
    Try to open the webcam using multiple backends.
    Returns a working VideoCapture or None.
    """
    backends = [
        (cv2.CAP_ANY,  "AUTO"),
        (cv2.CAP_MSMF, "MSMF"),
        (cv2.CAP_DSHOW,"DSHOW"),
    ]
    for idx in range(2):           # camera indices 0 and 1
        for backend, name in backends:
            try:
                cap = cv2.VideoCapture(idx, backend)
                if cap.isOpened():
                    # Read a few warm-up frames
                    ok = False
                    for _ in range(10):
                        ret, frame = cap.read()
                        if ret and frame is not None and frame.size > 0:
                            ok = True
                            break
                        time.sleep(0.1)
                    if ok:
                        print(f"[Camera] Opened camera {idx} via {name}")
                        return cap
                cap.release()
            except Exception as e:
                print(f"[Camera] {name} idx={idx} failed: {e}")
    return None


def capture_faces(user_name, num_images=5, dataset_folder='dataset'):
    """
    Captures face images from the webcam for a given user.
    Saves images to dataset/<user_name>/ for training.
    """
    user_folder = os.path.join(dataset_folder, user_name)
    os.makedirs(user_folder, exist_ok=True)

    cap = _open_camera()
    if cap is None:
        print("[Capture] ERROR: No working camera found. Check that no other app is using it.")
        return False

    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print("[Capture] ERROR: Failed to load Haar cascade.")
        cap.release()
        return False

    count = 0
    no_face_streak = 0
    MAX_NO_FACE = 500   # ~50 sec

    print(f"[Capture] Ready. Sit ~50-80 cm from camera. Good lighting is key.")

    while count < num_images:
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            print("[Capture] Bad frame — retrying...")
            time.sleep(0.1)
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)      # improves contrast in dim light

        # Very permissive detection
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=2,
            minSize=(50, 50),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        display = frame.copy()

        if len(faces) >= 1:
            no_face_streak = 0
            # Pick the largest face
            x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]

            cv2.rectangle(display, (x, y), (x+w, y+h), (0, 220, 0), 2)
            cv2.putText(display,
                        f"  Capturing {count+1}/{num_images} ...",
                        (x, max(y - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 0), 2)

            img_path = os.path.join(user_folder, f"{user_name}_{count+1}.jpg")
            cv2.imwrite(img_path, frame)
            count += 1
            time.sleep(0.6)

        else:
            no_face_streak += 1
            cv2.putText(display,
                        "No face — move closer / improve lighting",
                        (10, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 60, 255), 2)
            if no_face_streak > MAX_NO_FACE:
                print("[Capture] Timed out — no face detected.")
                break

        cv2.putText(display,
                    f"Saved: {count}/{num_images}   |   Q = cancel",
                    (10, display.shape[0] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        cv2.imshow("Face Capture", display)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[Capture] Cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if count == num_images:
        print(f"[Capture] Success — {num_images} images saved for '{user_name}'.")
        return True

    print(f"[Capture] Incomplete — {count}/{num_images} images saved.")
    return False


if __name__ == "__main__":
    name = input("Enter name: ").strip()
    capture_faces(name)
