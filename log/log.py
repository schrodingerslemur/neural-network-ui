import logging
import io

# Function to setup logging and capture output
def setup_logging():
    # Create a StringIO object to capture logs
    log_capture = io.StringIO()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,  # Set the log level
        format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
        handlers=[
            logging.StreamHandler(log_capture)  # Capture logs in log_capture
        ]
    )
    return log_capture

"""
Implementation: 
def onAppStart(app):
    app.logCapture = setup_logging()  # Setup logging and capture output
    app.logs = ""  # Initialize a variable to store logs

def onStep(app):
    # Update logs dynamically
    app.logs = app.logCapture.getvalue()

def redrawAll(app):
    # Draw logs at a specific location
    drawLabel(app.logs, 10, app.height - 50, align="left", size=12, fill="black")
"""

# Example usage
if __name__ == "__main__":
    # Set up logging
    log_capture = setup_logging()

    # Log some messages
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")

    # Retrieve logged messages
    log_output = log_capture.getvalue()
    print("Captured Logs:")
    print(log_output)
