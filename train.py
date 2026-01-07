import face_recognition
import os
import pickle

# Configuration
IMAGE_DIR = "student_images"
ENCODING_FILE = "encodings.pickle"

def generate_encodings():
    known_encodings = []
    known_names = []

    print(f"[INFO] Starting to process images in '{IMAGE_DIR}'...")

    # Loop through every image in the folder
    for filename in os.listdir(IMAGE_DIR):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            # 1. Extract Name from filename
            name = os.path.splitext(filename)[0].replace("_", " ")
            path = os.path.join(IMAGE_DIR, filename)

            # 2. Load the image
            image = face_recognition.load_image_file(path)

            # 3. Detect face and generate 128-d vector
            # We use 'hog' for CPU (faster for demo) or 'cnn' for GPU
            encodings = face_recognition.face_encodings(image)

            if len(encodings) > 0:
                known_encodings.append(encodings[0])
                known_names.append(name)
                print(f"[SUCCESS] Encoded: {name}")
            else:
                print(f"[WARNING] No face found in {filename}. Skipping.")

    # 4. Save the "Digital DNA" to a file
    data = {"encodings": known_encodings, "names": known_names}
    with open(ENCODING_FILE, "wb") as f:
        f.write(pickle.dumps(data))
    
    print(f"\n[DONE] Successfully saved {len(known_names)} student encodings to {ENCODING_FILE}")

if __name__ == "__main__":
    generate_encodings()