from PIL import Image
from cmu_graphics import *
import torch
import torchvision.transforms as transforms
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile

from PIL import Image
import torchvision.transforms as transforms

def preprocess_image(image, target_size=(224, 224)):
    """
    Preprocesses an image file path or PIL.Image object for a CNN.
    :param image: File path to an image or PIL.Image.Image object
    :param target_size: Target size for resizing (default: 224x224)
    :return: Torch tensor of the processed image
    """
    transform = transforms.Compose([
        transforms.Resize(target_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # ImageNet normalization
    ])
    
    if isinstance(image, str):
        # If the input is a file path, open the image
        image = Image.open(image).convert('RGB')  # Ensure RGB format
    elif not isinstance(image, Image.Image):
        raise TypeError(f"Unsupported type for image: {type(image)}")
    
    return transform(image)


def uploadImages(app, target_size=(224, 224)):
    root = tk.Tk()
    root.withdraw()  # Hide root window

    # Prompt user to select a file
    file_path = filedialog.askopenfilename(
        title="Select Image(s) or Zip File",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp"), ("Zip Files", "*.zip"), ("All Files", "*.*")]
    )

    if not file_path:
        print("File upload canceled.")
        return None

    # try:
    if file_path.lower().endswith('.zip'):
        # Handle zip file
        batch = []
        with zipfile.ZipFile(file_path, 'r') as archive:
            for file in archive.namelist():
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    with archive.open(file) as img_file:
                        img = Image.open(img_file).convert('RGB')  # Convert image to RGB format
                        tensor = preprocess_image(img, target_size)
                        batch.append(tensor)
        if batch:
            batch_tensor = torch.stack(batch)  # Stack tensors into a single batch
            print(f"Processed {len(batch)} images into a batch tensor. Shape: {batch_tensor.shape}")
            return batch_tensor
        else:
            messagebox.showerror("Error", "No valid images found in the zip file.")
            return None

    elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
        # Handle single image
        img = Image.open(file_path).convert('RGB')  # Ensure image has 3 channels (RGB)
        tensor = preprocess_image(img, target_size)
        print(f"Processed single image into a tensor. Shape: {tensor.shape}")
        return tensor.unsqueeze(0)  # Add batch dimension

    #     else:
    #         messagebox.showerror("Invalid File", "Please upload a valid image or zip file.")
    #         return None

    # except Exception as e:
    #     messagebox.showerror("Error", f"Failed to process file: {e}")
    #     return None
