import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import pickle
import base64
import torch
from data.image import preprocess_image, uploadImages
from PIL import Image
import zipfile
from io import BytesIO

def upload_and_process_file(file_types, prompt="Select a file"):
    """
    Universal function to handle various file types: csv, pickle, numpy, torch, image, and zip.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open file dialog
    file_path = filedialog.askopenfilename(
        title=prompt,
        filetypes=file_types
    )

    if file_path:
        # try:
        # CSV
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
            print(f"CSV file loaded successfully! Shape: {df.shape}")
            return torch.tensor(df.values, dtype=torch.float32)

        # Pickle
        elif file_path.lower().endswith('.pkl'):
            with open(file_path, 'rb') as f:
                obj = pickle.load(f)
            print(f"Pickle file loaded successfully!")
            return obj

        # Torch
        elif file_path.lower().endswith('.pt'):
            tensor = torch.load(file_path)
            print(f"Torch file loaded successfully! Shape: {tensor.shape}")
            return tensor

        # Numpy
        elif file_path.lower().endswith('.npy'):
            np_array = np.load(file_path)
            print(f"Numpy file loaded successfully! Shape: {np_array.shape}")
            return torch.tensor(np_array, dtype=torch.float32)

        # Image
        elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            tensor = preprocess_image(file_path)  # Preprocess single image
            print(f"Image file processed successfully! Shape: {tensor.shape}")
            return tensor.unsqueeze(0)  # Add batch dimension

        # Zip
        elif file_path.lower().endswith('.zip'):
            batch = []
            with zipfile.ZipFile(file_path, 'r') as archive:
                for file_name in archive.namelist():
                    if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        with archive.open(file_name) as img_file:
                            img = Image.open(BytesIO(img_file.read())).convert('RGB')  # Handle as BytesIO
                            batch.append(preprocess_image(img))
            batch_tensor = torch.stack(batch)
            print(f"Processed {len(batch)} images from zip into a batch tensor. Shape: {batch_tensor.shape}")
            return batch_tensor

        else:
            messagebox.showerror("Invalid File", "Unsupported file type.")
            return None

    #     except Exception as e:
    #         messagebox.showerror("Error", f"Failed to process file: {e}")
    #         return None
    # else:
    #     print("File upload canceled.")
    #     return None


# Specialized upload functions
def uploadInput(app):
    tensor = upload_and_process_file(
        file_types=[("CSV Files", "*.csv"), ("Numpy Files", "*.npy"), ("Torch Files", "*.pt"), ("Image Files", "*.jpg;*.jpeg;*.png;*.bmp"), ("Zip Files", "*.zip"), ("All Files", "*.*")],
        prompt="Select Input Data File, Image, or Zip"
    )
    if tensor is not None:
        app.train_dict["data"]["input"] = tensor.tolist() if isinstance(tensor, torch.Tensor) else tensor
        app.inputUploaded = True
        print("Input data stored successfully.")

def uploadEvalInput(app):
    tensor = upload_and_process_file(
        file_types=[("CSV Files", "*.csv"), ("Numpy Files", "*.npy"), ("Torch Files", "*.pt"), ("Image Files", "*.jpg;*.jpeg;*.png;*.bmp"), ("Zip Files", "*.zip"), ("All Files", "*.*")],
        prompt="Select Evaluation Input Data File, Image, or Zip"
    )
    if tensor is not None:
        app.eval_dict["data"]["input"] = tensor.tolist() if isinstance(tensor, torch.Tensor) else tensor
        app.evalInputUploaded = True
        print("Evaluation input data stored successfully.")

def uploadLabel(app):
    tensor = upload_and_process_file(
        file_types=[("CSV Files", "*.csv"), ("Numpy Files", "*.npy"), ("Torch Files", "*.pt"), ("All Files", "*.*")],
        prompt="Select Label Data File"
    )
    if tensor is not None:
        app.train_dict["data"]["label"] = tensor.tolist() if isinstance(tensor, torch.Tensor) else tensor
        app.labelUploaded = True
        print("Label data stored successfully.")

def uploadModel(app):
    model = upload_and_process_file(
        file_types=[("Pickle Files", "*.pkl"), ("Torch Files", "*.pt"), ("All Files", "*.*")],
        prompt="Select Model File (Pickle or Torch)"
    )
    if model is not None:
        if isinstance(model, torch.nn.Module):
            torch.save(model, "temp_model.pt")  # Temporarily save PyTorch model
            with open("temp_model.pt", "rb") as f:
                model_bytes = f.read()
        elif not isinstance(model, bytes):
            model_bytes = pickle.dumps(model)
        else:
            model_bytes = model

        encoded_model = base64.b64encode(model_bytes).decode('utf-8')
        app.model = encoded_model
        app.eval_dict["state"] = app.model
        app.modelUploaded = True
        print("Model successfully loaded and stored.")
