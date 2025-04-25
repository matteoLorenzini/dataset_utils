import tkinter as tk
from tkinter import ttk, messagebox
from list_records_download import main as cli_main
import sys
import threading

# Define endpoints and verbs with descriptive labels
ENDPOINTS = {
    "a": "CulturaItalia (https://www.culturaitalia.it/oaiProviderCI/OAIHandler)",
    "b": "Example Endpoint 1 (https://example1.com/oai)",
    "c": "Example Endpoint 2 (https://example2.com/oai)"
}

VERBS = {
    "1": "Identify",
    "2": "ListIdentifiers",
    "3": "ListMetadataFormats",
    "4": "ListSets",
    "5": "ListRecords"
}

def run_script():
    # Disable the Run button while the script is running
    run_button.config(state=tk.DISABLED)
    progress_bar.start()

    def task():
        # Get selected values from the GUI
        endpoint_key = endpoint_var.get().split(":")[0].strip()
        verb_key = verb_var.get().split(":")[0].strip()
        dataset_name = dataset_name_entry.get()
        output_file = output_file_entry.get()
        test = test_var.get()
        save_xml = save_xml_var.get()
        save_csv = save_csv_var.get()

        # Validate inputs
        if not endpoint_key or not verb_key or not output_file:
            messagebox.showerror("Error", "Please fill in all required fields.")
            progress_bar.stop()
            run_button.config(state=tk.NORMAL)
            return

        if not save_xml and not save_csv:
            messagebox.showerror("Error", "Please select at least one output format (XML or CSV).")
            progress_bar.stop()
            run_button.config(state=tk.NORMAL)
            return

        # Build the command-line arguments
        args = [
            "list_records_download.py",
            "-e", endpoint_key,
            "-v", verb_key
        ]
        if dataset_name:
            args.append(dataset_name)
        args.append(output_file)
        if test:
            args.append("--test")
        if save_xml:
            args.append("--save-xml")
        if save_csv:
            args.append("--save-csv")

        # Run the script with the provided arguments
        try:
            sys.argv = args
            cli_main()
            messagebox.showinfo("Success", "Operation completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            progress_bar.stop()
            run_button.config(state=tk.NORMAL)

    # Run the task in a separate thread to keep the GUI responsive
    threading.Thread(target=task).start()

# Create the main window
root = tk.Tk()
root.title("OAI-PMH Data Fetcher")

# Endpoint selection
tk.Label(root, text="Select Endpoint:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
endpoint_var = tk.StringVar()
endpoint_dropdown = ttk.Combobox(root, textvariable=endpoint_var, state="readonly")
endpoint_dropdown["values"] = [f"{key}: {value}" for key, value in ENDPOINTS.items()]
endpoint_dropdown.grid(row=0, column=1, padx=5, pady=5)

# Verb selection
tk.Label(root, text="Select Verb:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
verb_var = tk.StringVar()
verb_dropdown = ttk.Combobox(root, textvariable=verb_var, state="readonly")
verb_dropdown["values"] = [f"{key}: {value}" for key, value in VERBS.items()]
verb_dropdown.grid(row=1, column=1, padx=5, pady=5)

# Dataset name
tk.Label(root, text="Dataset Name (optional):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
dataset_name_entry = tk.Entry(root)
dataset_name_entry.grid(row=2, column=1, padx=5, pady=5)

# Output file
tk.Label(root, text="Output File:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
output_file_entry = tk.Entry(root)
output_file_entry.grid(row=3, column=1, padx=5, pady=5)

# Test mode checkbox
test_var = tk.BooleanVar()
test_checkbox = tk.Checkbutton(root, text="Test Mode (limit to 20 records)", variable=test_var)
test_checkbox.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)

# Save as XML checkbox
save_xml_var = tk.BooleanVar()
save_xml_checkbox = tk.Checkbutton(root, text="Save as XML", variable=save_xml_var)
save_xml_checkbox.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)

# Save as CSV checkbox
save_csv_var = tk.BooleanVar()
save_csv_checkbox = tk.Checkbutton(root, text="Save as CSV", variable=save_csv_var)
save_csv_checkbox.grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=5)

# Progress bar
progress_bar = ttk.Progressbar(root, mode="indeterminate")
progress_bar.grid(row=7, column=0, columnspan=2, pady=10)

# Run button
run_button = tk.Button(root, text="Run", command=run_script)
run_button.grid(row=8, column=0, columnspan=2, pady=10)

# Start the GUI event loop
root.mainloop()