import os
import cv2
import face_recognition
import pickle

def train_system(dataset_folder='dataset', db_folder='database'):
    """
    Scans the dataset folder for user images.
    Extracts face encodings using dlib and face_recognition.
    Saves the known encodings and names to a pickle file.
    """
    known_encodings = []
    known_names = []
    
    if not os.path.exists(dataset_folder):
        print(f"Error: Dataset folder '{dataset_folder}' not found!")
        return False
        
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        
    print("Processing images and extracting encodings...")
    
    valid_extensions = ('.jpg', '.jpeg', '.png')
    
    # Walk through the dataset directory
    for root, dirs, files in os.walk(dataset_folder):
        for file in files:
            if file.lower().endswith(valid_extensions):
                path = os.path.join(root, file)
                # The name is taken from the subfolder directory name
                name = os.path.basename(root)
                
                # Load image using cv2
                image = cv2.imread(path)
                if image is None:
                    continue
                    
                # Convert from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Detect face locations
                boxes = face_recognition.face_locations(rgb_image)
                
                if not boxes:
                    print(f"Warning: No face found in {path}. Skipping.")
                    continue
                    
                # Compute face encodings
                encodings = face_recognition.face_encodings(rgb_image, boxes)
                
                # Add each encoding to our list (usually there's only 1 face per image ideally)
                for encoding in encodings:
                    known_encodings.append(encoding)
                    known_names.append(name)
                    
    total_users = len(set(known_names))
    total_encodings = len(known_encodings)
    print(f"Extracted {total_encodings} encodings for {total_users} user(s).")
    
    if total_encodings == 0:
        print("No valid encodings extracted. Training failed.")
        return False
        
    # Save the encodings and names to a pickle file
    data = {"encodings": known_encodings, "names": known_names}
    encodings_path = os.path.join(db_folder, "encodings.pickle")
    
    with open(encodings_path, "wb") as f:
        pickle.dump(data, f)
        
    print(f"Training complete. Data saved to {encodings_path}")
    return True

if __name__ == "__main__":
    train_system()
