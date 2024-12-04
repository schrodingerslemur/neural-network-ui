import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import pickle
import base64

def upload_and_process_file(file_type="csv", prompt="Select a file"):
    """
    Returns None if failed
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Set file types based on expected file_type
    file_types = {
        "csv": [("CSV Files", "*.csv"), ("All Files", "*.*")],
        "pickle": [("Pickle Files", "*.pkl"), ("All Files", "*.*")]
    }

    if file_type not in file_types:
        messagebox.showerror("Invalid File Type", f"Unsupported file type: {file_type}")
        return None

    # Open file dialog
    file_path = filedialog.askopenfilename(
        title=prompt,
        filetypes=file_types[file_type]
    )

    if file_path:
        try:
            if file_type == "csv":
                # Ensure the file ends with .csv
                if not file_path.lower().endswith('.csv'):
                    messagebox.showerror("Invalid File", "Please upload a CSV file.")
                    return None
                df = pd.read_csv(file_path)
                print(f"DataFrame for {prompt} created successfully!")
                print(df.head())
                return df

            elif file_type == "pickle":
                # Ensure the file ends with .pkl
                if not file_path.lower().endswith('.pkl'):
                    messagebox.showerror("Invalid File", "Please upload a Pickle (.pkl) file.")
                    return None
                with open(file_path, 'rb') as f:
                    obj = pickle.load(f)
                print(f"Pickle file for {prompt} loaded successfully!")
                return obj

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {e}")
            return None
    else:
        print("File upload canceled.")
        return None


# Specialized upload functions
def uploadInput(app):
    df = upload_and_process_file(file_type="csv", prompt="Select Input Data CSV")
    if df is not None:
        app.train_dict["data"]["input"] = df.values.tolist()
        app.inputUploaded = True
        print("Input DataFrame stored in app.inputDF.")

def uploadEvalInput(app):
    df = upload_and_process_file(file_type="csv", prompt="Select Input Data CSV")
    if df is not None:
        app.eval_dict["data"]["input"] = df.values.tolist()
        app.evalInputUploaded = True
        print("Input DataFrame stored in app.inputDF.")


def uploadLabel(app):
    df = upload_and_process_file(file_type="csv", prompt="Select Label Data CSV")
    if df is not None:
        app.train_dict["data"]["label"] = df.values.tolist()
        app.labelUploaded = True
        print("Label DataFrame stored in app.labelDF.")


def uploadModel(app):
    model = upload_and_process_file(file_type="pickle", prompt="Select Model File (Pickle)")
    if model is not None:
        print(type(model))
        model = pickle.dumps(model)
        print(type(model))
        model = base64.b64encode(model).decode('utf-8')
        app.model = model
        app.eval_dict["state"] = app.model
        app.modelUploaded = True
        print("Model successfully loaded and stored in app.model.")
