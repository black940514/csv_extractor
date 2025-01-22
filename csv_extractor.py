import os
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, messagebox, Button, Label, Frame, StringVar
from tkinter.ttk import Progressbar
import threading

def select_files():
    """Open a file dialog to select multiple CSV or XLSX files."""
    files = filedialog.askopenfilenames(title="Select CSV/XLSX files", 
                                        filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")])
    return files

def select_folder():
    """Open a folder dialog to select the save directory."""
    folder = filedialog.askdirectory(title="Select Save Folder")
    return folder

def process_files(file_paths, save_folder, progress_var, progress_label):
    """Process each file by extracting 20 rows and saving with a new name."""
    total_files = len(file_paths)
    for idx, file_path in enumerate(file_paths, 1):
        try:
            # Read the file
            if file_path.endswith(".csv"):
                data = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                data = pd.read_excel(file_path)
            else:
                print(f"Unsupported file format: {file_path}")
                continue

            # Extract 20 rows
            sampled_data = data.head(20)

            # Generate new filename
            base_name = os.path.basename(file_path)
            name, ext = os.path.splitext(base_name)
            new_name = f"{name}_example{ext}"
            save_path = os.path.join(save_folder, new_name)

            # Save the sampled data
            sampled_data.to_csv(save_path, index=False) if ext == ".csv" else sampled_data.to_excel(save_path, index=False)
            print(f"Saved: {save_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
        finally:
            progress_var.set((idx / total_files) * 100)
            progress_label.config(text=f"Processing {idx}/{total_files} files...")

    messagebox.showinfo("Processing Complete", "All files have been processed and saved.")

def visualize_data(file_paths):
    """Generate visualizations for the selected files."""
    for file_path in file_paths:
        try:
            if file_path.endswith(".csv"):
                data = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                data = pd.read_excel(file_path)
            else:
                continue

            plt.figure()
            data.head(20).plot(kind="bar", figsize=(10, 6), title=f"Visualization of {os.path.basename(file_path)}")
            plt.show()
        except Exception as e:
            print(f"Error visualizing {file_path}: {e}")

def start_processing(file_paths_var, save_folder_var, progress_var, progress_label):
    file_paths = file_paths_var.get().split("||")
    save_folder = save_folder_var.get()

    if not file_paths or file_paths == ['']:
        messagebox.showwarning("No Files Selected", "Please select at least one file to process.")
        return

    if not save_folder:
        messagebox.showwarning("No Folder Selected", "Please select a folder to save the processed files.")
        return

    threading.Thread(target=process_files, args=(file_paths, save_folder, progress_var, progress_label)).start()

def main():
    # Create the main application window
    root = Tk()
    root.title("CSV/XLSX Batch Processor")
    root.geometry("500x300")

    # Variables
    file_paths_var = StringVar()
    save_folder_var = StringVar()
    progress_var = StringVar()
    progress_var.set(0)

    # File selection frame
    file_frame = Frame(root)
    file_frame.pack(pady=10, padx=10, fill="x")

    Label(file_frame, text="Selected Files:").grid(row=0, column=0, sticky="w")
    Label(file_frame, textvariable=file_paths_var, wraplength=400, anchor="w", justify="left").grid(row=1, column=0, sticky="w")

    Button(file_frame, text="Select Files", command=lambda: file_paths_var.set("||".join(select_files()))).grid(row=0, column=1, padx=5)

    # Save folder frame
    folder_frame = Frame(root)
    folder_frame.pack(pady=10, padx=10, fill="x")

    Label(folder_frame, text="Save Folder:").grid(row=0, column=0, sticky="w")
    Label(folder_frame, textvariable=save_folder_var, wraplength=400, anchor="w", justify="left").grid(row=1, column=0, sticky="w")

    Button(folder_frame, text="Select Folder", command=lambda: save_folder_var.set(select_folder())).grid(row=0, column=1, padx=5)

    # Progress frame
    progress_frame = Frame(root)
    progress_frame.pack(pady=10, padx=10, fill="x")

    Label(progress_frame, text="Progress:").pack(anchor="w")
    progress_bar = Progressbar(progress_frame, variable=progress_var, maximum=100)
    progress_bar.pack(fill="x", padx=5, pady=5)

    progress_label = Label(progress_frame, text="Waiting to start...")
    progress_label.pack(anchor="w")

    # Buttons frame
    button_frame = Frame(root)
    button_frame.pack(pady=20, fill="x")

    Button(button_frame, text="Start Processing", 
           command=lambda: start_processing(file_paths_var, save_folder_var, progress_var, progress_label)).pack(side="left", padx=5)

    Button(button_frame, text="Visualize Data", 
           command=lambda: visualize_data(file_paths_var.get().split("||"))).pack(side="left", padx=5)

    Button(button_frame, text="Exit", command=root.quit).pack(side="left", padx=5)

    root.mainloop()

if __name__ == "__main__":
    main()
