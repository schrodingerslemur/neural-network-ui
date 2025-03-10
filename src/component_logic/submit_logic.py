from cmu_graphics import *
import json
import base64
import tkinter as tk
import pandas as pd

from tkinter import filedialog
from app.neural_network.net_main import neural_main

from util.fix_utils import fixActivations

def submitTrain(app):
    print("Submit train button pressed.")

    # Train model
    try:
        fixActivations(app)
        json_string = json.dumps(app.train_dict)
        train_output = neural_main(json_string)
        train_output = json.loads(train_output)
        encoded_pickle_data = train_output['pickled_data']
        pickle_data = base64.b64decode(encoded_pickle_data)

        # tkinter root window (hidden)
        root = tk.Tk()
        root.withdraw()  # Hide root window

        # save location in file
        save_path = filedialog.asksaveasfilename(
            title="Save Pickle File",
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")],
        )

        if save_path:
            # save pickl to chosen file
            with open(save_path, "wb") as f:
                f.write(pickle_data)
            print(f"Pickle file saved to {save_path}")
            app.showMessage(f"Pickle file saved to {save_path}")
        else:
            print("Save operation canceled.")
            app.showMessage("Save operation canceled.")

    except Exception as e:
        app.showMessage(f"An error occured: ({e})")
        print(e)

def submitEval(app):
    try:
        print("Submit eval button pressed")
        fixActivations(app)
        json_string = json.dumps(app.eval_dict)
        eval_output = neural_main(json_string)
        eval_output = json.loads(eval_output)
        eval_output = eval_output["output"]

        # Convert eval_output (list) to a DataFrame
        eval_df = pd.DataFrame(eval_output)

        app.showMessage('SUCCESSFUL Evaluation!')

        root = tk.Tk()
        root.withdraw()  # Hide root window

        # Save location in file
        save_path = filedialog.asksaveasfilename(
            title="Save Output File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if save_path:
            # Save DataFrame as CSV to the chosen file
            eval_df.to_csv(save_path, index=False)
            print(f"CSV file saved to {save_path}")
            app.showMessage(f"CSV file saved to {save_path}")
        else:
            print("Save operation canceled.")
            app.showMessage("Save operation canceled.")

    except Exception as e:
        app.showMessage(f"An error occurred: ({e})")
        print(e)
