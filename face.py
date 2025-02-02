import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os

# Ensure the screenshots directory exists
os.makedirs("static/screenshots", exist_ok=True)
os.makedirs("static/reference", exist_ok=True)

def load_reference_images():
    """Load four predefined reference images and detect faces."""
    reference_paths = {
        "Sarthak": "static/reference/sarthak.jpg",
        "Shriram": "static/reference/shriram.jpg",
        "Nimith": "static/reference/nimith.jpg",
        "Brinda": "static/reference/brinda.jpg"
    }
    
    reference_faces = {}
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    for name, path in reference_paths.items():
        try:
            reference_img = cv2.imread(path)
            if reference_img is None:
                print(f"Could not load image: {path}")
                continue
                
            gray_ref = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_ref, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
            
            if len(faces) > 0:
                x, y, w, h = faces[0]  # Considering only the first detected face
                reference_faces[name] = gray_ref[y:y+h, x:x+w]
        except Exception as e:
            print(f"Error processing reference image {path}: {str(e)}")
    
    return reference_faces

def compare_faces(reference_face, detected_face):
    """Compares two face images using SSIM."""
    try:
        detected_face_resized = cv2.resize(detected_face, (reference_face.shape[1], reference_face.shape[0]))
        similarity_score = ssim(reference_face, detected_face_resized)
        return similarity_score
    except Exception as e:
        print(f"Error comparing faces: {str(e)}")
        return 0.0

def recognize_faces():
    """Captures video and matches detected faces with four preloaded reference images."""
    reference_faces = load_reference_images()
    if not reference_faces:
        print("No reference faces loaded.")
        return {"success": False, "error": "No reference faces loaded"}
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return {"success": False, "error": "Could not access camera"}
    
    last_recognized = None
    screenshot_taken = False
    screenshot_path = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        
        for (x, y, w, h) in faces:
            detected_face = gray_frame[y:y+h, x:x+w]
            best_match = "Unknown"
            best_score = 0.0
            
            for name, ref_face in reference_faces.items():
                similarity = compare_faces(ref_face, detected_face)
                if similarity > best_score:
                    best_score = similarity
                    best_match = name if similarity > 0.5 else "Unknown"
            
            color = (0, 255, 0) if best_match != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, best_match, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            
            if best_match != "Unknown" and not screenshot_taken:
                screenshot_path = f"static/screenshots/{best_match.lower()}_detected.jpg"
                cv2.imwrite(screenshot_path, frame)
                screenshot_taken = True
                last_recognized = best_match
        
        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or screenshot_taken:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if screenshot_taken:
        return {"success": True, "name": last_recognized, "screenshot": screenshot_path}
    return {"success": False, "error": "No face was recognized"}