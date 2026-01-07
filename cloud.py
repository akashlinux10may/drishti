import face_recognition
import cv2
import pickle
import numpy as np
from supabase import create_client, Client

# --- CONFIGURATION ---
SUPABASE_URL = "https://wiyrwciskmononuaaeih.supabase.co"
SUPABASE_KEY = "sb_publishable_SlQxcUZEN193jYnehQvLEg_f5fUlS8_"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# To prevent flooding the DB, let's keep track of who we already marked
marked_today = set()

# Load Encodings
with open("encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())

video_capture = cv2.VideoCapture(0)

print("[INFO] System Live. Scanning for students...")

while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(data["encodings"], face_encoding, tolerance=0.5)
        face_distances = face_recognition.face_distance(data["encodings"], face_encoding)
        best_match_index = np.argmin(face_distances)
        
        if matches[best_match_index]:
            name = data["names"][best_match_index]
            
            # --- CLOUD LOGGING LOGIC ---
            if name not in marked_today:
                print(f"[CLOUD] Marking attendance for {name}...")
                
                # Send to Supabase
                entry = {"student_name": name, "status": "Present"}
                supabase.table("attendance_logs").insert(entry).execute()
                
                marked_today.add(name)
                print(f"[SUCCESS] {name} logged to Dzire Cloud.")

    cv2.imshow('Drishti-AI Cloud Demo', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()