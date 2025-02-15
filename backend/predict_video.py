import torch
from torchvision import transforms, models
from PIL import Image
import os
import torch.nn as nn

# Define ensemble model
class EnsembleModel(nn.Module):
    def __init__(self):
        super(EnsembleModel, self).__init__()

        # Load models
        self.resnet = models.resnet18()
        self.efficientnet = models.efficientnet_b0()
        self.mobilenet = models.mobilenet_v2()

        # Modify last layer for binary classification
        self.resnet.fc = nn.Linear(self.resnet.fc.in_features, 2)
        self.efficientnet.classifier[1] = nn.Linear(self.efficientnet.classifier[1].in_features, 2)
        self.mobilenet.classifier[1] = nn.Linear(self.mobilenet.classifier[1].in_features, 2)

    def forward(self, x):
        resnet_out = self.resnet(x)
        efficientnet_out = self.efficientnet(x)
        mobilenet_out = self.mobilenet(x)
        final_output = (resnet_out + efficientnet_out + mobilenet_out) / 3
        return final_output

def predict_faces(face_folder, model_paths):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = EnsembleModel().to(device)

    # Load trained weights
    try:
        model.resnet.load_state_dict(torch.load(model_paths["resnet"], map_location=device, weights_only=True))
        model.efficientnet.load_state_dict(torch.load(model_paths["efficientnet"], map_location=device, weights_only=True))
        model.mobilenet.load_state_dict(torch.load(model_paths["mobilenet"], map_location=device, weights_only=True))
    except FileNotFoundError as e:
        print(f"Error loading model weights: {e}")
        return " Error loading model weights. Please check logs."

    model.eval()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Collect all image paths
    image_paths = [os.path.join(face_folder, img) for img in os.listdir(face_folder) if img.lower().endswith((".jpg", ".jpeg", ".png"))]
    
    # Process images in batches
    batch_size = 32
    predictions = []
    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i:i + batch_size]
        batch_images = []
        
        for image_path in batch_paths:
            try:
                image = Image.open(image_path).convert("RGB")
                image = transform(image).unsqueeze(0).to(device)
                batch_images.append(image)
            except Exception as e:
                print(f"Error processing {image_path}: {e}")
        
        if batch_images:
            batch_images = torch.cat(batch_images, dim=0)
            with torch.no_grad():
                output = model(batch_images)
                batch_predictions = torch.argmax(output, dim=1).cpu().numpy()
                predictions.extend(batch_predictions)

    # Majority voting
    fake_count = predictions.count(1)
    real_count = predictions.count(0)

    print(f"Total frames analyzed: {len(predictions)}")
    print(f"Fake frames: {fake_count}, Real frames: {real_count}")
    
    if fake_count > real_count:
        result = " The video is a DEEPFAKE!"
    else:
        result = " The video is REAL."
    
    return result

if __name__ == "__main__":
    face_folder = "faces/test_video"
    model_paths = {
        "resnet": "backend/resnet_model_94.79.pth",
        "efficientnet": "backend/efficientnet_model_95.38.pth",
        "mobilenet": "backend/mobilenet_model_92.71.pth"
    }
    predict_faces(face_folder, model_paths)