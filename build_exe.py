import PyInstaller.__main__
import os
import shutil

# This script packages the Smart Attendance System into a single EXE
# It handles hidden imports for dlib and face_recognition

def build():
    print("Starting Build Process...")
    
    # Clean previous builds
    if os.path.exists('build'): shutil.rmtree('build')
    if os.path.exists('dist'): shutil.rmtree('dist')
    
    PyInstaller.__main__.run([
        'main.py',
        '--name=SmartAttendanceSystem',
        '--onefile',
        '--windowed',
        '--icon=NONE', # Add an .ico path here if you have one
        '--add-data=attendance_manager.py;.',
        '--add-data=face_capture.py;.',
        '--add-data=face_recognize.py;.',
        '--add-data=face_train.py;.',
        '--add-data=surveillance_extension.py;.',
        '--hidden-import=face_recognition_models',
        '--hidden-import=dlib',
        '--collect-all=face_recognition',
        '--collect-all=face_recognition_models',
    ])
    
    print("\n" + "="*30)
    print("BUILD COMPLETE!")
    print("Your executable is in the 'dist' folder.")
    print("="*30)

if __name__ == "__main__":
    build()
