import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def load_reference_images():
    """Load four predefined reference images and detect faces."""
    reference_paths = {
        "Sarthak": "sarthak.jpg",
        "Shriram": "shriram.jpg",
        "Nimith": "nimith.jpg",
        "Brinda": "brinda.jpg"
    }
    
    reference_faces = {}
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    for name, path in reference_paths.items():
        reference_img = cv2.imread(path)
        gray_ref = cv2.cvtColor(reference_img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_ref, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        
        if len(faces) > 0:
            x, y, w, h = faces[0]  # Considering only the first detected face
            reference_faces[name] = gray_ref[y:y+h, x:x+w]
    
    return reference_faces

def compare_faces(reference_face, detected_face):
    """Compares two face images using SSIM."""
    detected_face_resized = cv2.resize(detected_face, (reference_face.shape[1], reference_face.shape[0]))
    similarity_score = ssim(reference_face, detected_face_resized)
    return similarity_score

def recognize_faces():
    """Captures video and matches detected faces with four preloaded reference images."""
    reference_faces = load_reference_images()
    if not reference_faces:
        print("No reference faces loaded.")
        return
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)
    
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
        
        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recognize_faces()
