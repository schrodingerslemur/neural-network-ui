from cmu_graphics import *
import json
import base64
import tkinter as tk

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
    print("Submit eval button pressed")
    fixActivations(app)
    print('eval_dict', app.eval_dict)
    json_string = json.dumps(app.eval_dict)
    eval_output = neural_main(json_string)
    print(eval_output)
    app.showMessage('evaluation success BORATTTTTTTTTTTTT')