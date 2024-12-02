import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

def upload_and_process_file(prompt="Select a file"):
    root = tk.Tk()
    root.withdraw() 

    file_path = filedialog.askopenfilename(
        title=prompt,
        filetypes=[("CSV Files", "*.csv")]
    )

    if file_path:
        try:
            if not file_path.lower().endswith('.csv'):
                messagebox.showerror("Invalid File", "Please upload a CSV file.")
                return None

            df = pd.read_csv(file_path)
            print(f"DataFrame for {prompt} created successfully!")
            print(df.head()) 
            return df
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")
            return None
    else:
        print("File upload canceled.")
        return None


def uploadInput(app):
    df = upload_and_process_file("Select Input Data CSV")
    if df is not None:
        app.inputDF = df  # store df 
        app.result["data"]["input"] = df.values.tolist()
        # print(app.result["input"])
        print("Input DataFrame stored in app.inputDF.")


def uploadLabel(app):
    df = upload_and_process_file("Select Label Data CSV")
    if df is not None:
        app.labelDF = df  # store 
        app.result["data"]["label"] = df.values.tolist()
        # print(app.result["label"])
        print("Label DataFrame stored in app.labelDF.")
