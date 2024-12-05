from PIL import Image
import torch
import torchvision.transforms as transforms
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import os

def preprocess_image(image_path, target_size=(224, 224)):
    transform = transforms.Compose([
        transforms.Resize(target_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Example: ImageNet normalization
    ])
    img = Image.open(image_path).convert('RGB')  # Ensure 3 channels
    tensor = transform(img)
    return tensor

def uploadImages(app, target_size=(224, 224)):
    """
    Upload single or batch images for CNNs. Returns a batch tensor.
    """
    root = tk.Tk()
    root.withdraw()  # Hide root window

    file_path = filedialog.askopenfilename(
        title="Select Image(s) or Zip File",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp"), ("Zip Files", "*.zip"), ("All Files", "*.*")]
    )

    if file_path:
        try:
            if file_path.lower().endswith('.zip'):
                # Handle zip file
                batch = []
                with zipfile.ZipFile(file_path, 'r') as archive:
                    for file in archive.namelist():
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                            with archive.open(file) as img_file:
                                img = Image.open(img_file).convert('RGB')
                                batch.append(preprocess_image(img, target_size))
                batch_tensor = torch.stack(batch)
                print(f"Processed {len(batch)} images into a batch tensor. Shape: {batch_tensor.shape}")
                return batch_tensor

            elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                # Handle single image
                tensor = preprocess_image(file_path, target_size)
                print(f"Processed single image into a tensor. Shape: {tensor.shape}")
                return tensor.unsqueeze(0)  # Add batch dimension

            else:
                messagebox.showerror("Invalid File", "Please upload a valid image or zip file.")
                return None

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {e}")
            return None
    else:
        print("File upload canceled.")
        return None
