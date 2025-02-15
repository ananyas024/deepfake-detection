import os
import cv2
from multiprocessing import Pool

def detect_faces_in_image(image_path, output_folder):
    print(f" Processing {image_path}...")
    image = cv2.imread(image_path)
    
    if image is None:
        print(f" Error: Could not read {image_path}")
        return
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    if face_cascade.empty():
        print(" Error: Failed to load Haar cascade. Check OpenCV installation.")
        return

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    print(f" Detected {len(faces)} faces in {os.path.basename(image_path)}")

    for i, (x, y, w, h) in enumerate(faces):
        face = image[y:y+h, x:x+w]
        face_name = os.path.join(output_folder, f"face_{i}_{os.path.basename(image_path)}")
        cv2.imwrite(face_name, face)
        print(f" Saved face: {face_name}")

def detect_faces(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_paths = [os.path.join(input_folder, img) for img in os.listdir(input_folder) if img.endswith(".jpg")]

    if not image_paths:
        print(f" Warning: No images found in {input_folder}")
        return

    print(f" Processing {len(image_paths)} frames for face detection...")

    args = [(image_path, output_folder) for image_path in image_paths]

    # Use multiprocessing to speed up detection
    with Pool(processes=4) as pool:
        pool.starmap(detect_faces_in_image, args)

if __name__ == "__main__":
    input_folder = "extracted_frames/test_video"
    output_folder = "faces/test_video"
    detect_faces(input_folder, output_folder)
