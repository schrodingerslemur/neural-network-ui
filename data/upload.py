import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import pickle
import base64
import torch

def upload_and_process_file(file_types, prompt="Select a file"):
    """
    Universal function to handle various file types: csv, pickle, numpy, torch.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open file dialog
    file_path = filedialog.askopenfilename(
        title=prompt,
        filetypes=file_types
    )

    if file_path:
        try:
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

            else:
                messagebox.showerror("Invalid File", "Unsupported file type.")
                return None

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {e}")
            return None
    else:
        print("File upload canceled.")
        return None

# Specialized upload functions
def uploadInput(app):
    tensor = upload_and_process_file(
        file_types=[("CSV Files", "*.csv"), ("Numpy Files", "*.npy"), ("Torch Files", "*.pt"), ("All Files", "*.*")],
        prompt="Select Input Data File"
    )
    if tensor is not None:
        app.train_dict["data"]["input"] = tensor.tolist()
        app.inputUploaded = True
        print("Input tensor stored successfully.")

def uploadEvalInput(app):
    tensor = upload_and_process_file(
        file_types=[("CSV Files", "*.csv"), ("Numpy Files", "*.npy"), ("Torch Files", "*.pt"), ("All Files", "*.*")],
        prompt="Select Evaluation Input Data File"
    )
    if tensor is not None:
        app.eval_dict["data"]["input"] = tensor.tolist()
        app.evalInputUploaded = True
        print("Evaluation input tensor stored successfully.")

def uploadLabel(app):
    tensor = upload_and_process_file(
        file_types=[("CSV Files", "*.csv"), ("Numpy Files", "*.npy"), ("Torch Files", "*.pt"), ("All Files", "*.*")],
        prompt="Select Label Data File"
    )
    if tensor is not None:
        app.train_dict["data"]["label"] = tensor.tolist()
        app.labelUploaded = True
        print("Label tensor stored successfully.")

def uploadModel(app):
    model = upload_and_process_file(
        file_types=[("Pickle Files", "*.pkl"), ("Torch Files", "*.pt"), ("All Files", "*.*")],
        prompt="Select Model File (Pickle or Torch)"
    )
    if model is not None:
        if isinstance(model, torch.nn.Module):
            model = torch.save(model, "temp_model.pt")
        elif not isinstance(model, bytes):
            model = pickle.dumps(model)
        encoded_model = base64.b64encode(model).decode('utf-8')
        app.model = encoded_model
        app.eval_dict["state"] = app.model
        app.modelUploaded = True
        print("Model successfully loaded and stored.")
