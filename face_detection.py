import os
import cv2
from mtcnn import MTCNN

detector = MTCNN()

def detect_faces(image_path, output_folder):
    image = cv2.imread(image_path)
    
    results = detector.detect_faces(image)
    print(f"Processing: {image_path}, Faces Detected: {len(results)}")

    if len(results) > 0:
        for i, result in enumerate(results):
            x, y, width, height = result['box']
            face = image[y:y + height, x:x + width]
            face_name = os.path.join(output_folder, f"face_{i}_{os.path.basename(image_path)}")
            cv2.imwrite(face_name, face)
            print(f"Saved face: {face_name}")

def process_faces(input_folder, output_folder):
    print(f"Processing folder: {input_folder}")
    for root, _, files in os.walk(input_folder):
        for image_name in files:
            image_path = os.path.join(root, image_name)
            if os.path.isfile(image_path) and image_path.endswith(".png"):
                print(f"Found image: {image_path}")  
                relative_path = os.path.relpath(root, input_folder)
                save_path = os.path.join(output_folder, relative_path)

                os.makedirs(save_path, exist_ok=True)
                detect_faces(image_path, save_path)

if __name__ == "__main__":
    base_input_folder = "extracted_frames"
    base_output_folder = "faces"

    for dataset in ["train", "test", "validation"]:
        for category in ["fake", "real"]:
            input_path = os.path.join(base_input_folder, dataset, category)
            output_path = os.path.join(base_output_folder, dataset, category)
            process_faces(input_path, output_path)