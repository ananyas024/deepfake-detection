import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from extract_frames import extract_frames  # Adjusted import
from face_detection import detect_faces  # Adjusted import
from predict_video import predict_faces  # Adjusted import

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "*"}})

# 🔹 Configurations
UPLOAD_FOLDER = "uploads"
EXTRACTED_FRAMES_FOLDER = "extracted_frames"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACTED_FRAMES_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # 🔹 Extract frames from the video
    extracted_folder = os.path.join(EXTRACTED_FRAMES_FOLDER, filename)
    extract_frames(filepath, extracted_folder, interval=30)

    # 🔹 Detect faces in extracted frames
    faces_folder = os.path.join("faces", filename)
    detect_faces(extracted_folder, faces_folder)

    # 🔹 Run prediction on detected faces
    model_paths = {
        "resnet": "resnet_model_94.79.pth",
        "efficientnet": "efficientnet_model_95.38.pth",
        "mobilenet": "mobilenet_model_92.71.pth"
    }
    prediction_result = predict_faces(faces_folder, model_paths)

    # Debugging Logs
    print(f" Debug: Prediction result = {prediction_result}")
    if not prediction_result:
        prediction_result = " Prediction failed. Please check logs."

    # 🔹 Return JSON response to frontend
    response_data = {
        "message": " Frames and faces processed successfully!",
        "video": filename,
        "prediction": prediction_result  
    }

    print(" Debug: Backend Response:", response_data)
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=False)