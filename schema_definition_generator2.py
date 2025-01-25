import os
import pandas as pd
from tkinter import Tk, filedialog, messagebox, Toplevel, Label, Button, Frame, ttk
from datetime import datetime

def select_files():
    """Open a file dialog to select multiple CSV or XLSX files."""
    Tk().withdraw()  # Hide the root window
    return filedialog.askopenfilenames(title="Select CSV/XLSX files", 
                                       filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")])

def save_schema(dataframe):
    """Save the schema definition CSV with a timestamped filename in a user-selected folder."""
    Tk().withdraw()
    folder_selected = filedialog.askdirectory(title="Select Folder to Save Schema")
    if not folder_selected:
        messagebox.showwarning("No Folder Selected", "Please select a folder to save the schema.")
        return None

    timestamp = datetime.now().strftime("%m%d%H%M")
    file_name = f"schema_definition_{timestamp}.csv"
    save_path = os.path.join(folder_selected, file_name)

    try:
        dataframe.to_csv(save_path, index=False)
        messagebox.showinfo("Success", f"Schema saved to {save_path}")
        return save_path
    except Exception as e:
        messagebox.showerror("Error Saving File", f"Failed to save schema: {e}")
        return None

def generate_schema(files):
    """Generate a schema definition dataframe from multiple CSV/XLSX files."""
    schema_data = []

    for file_path in files:
        try:
            if file_path.endswith(".csv"):
                data = pd.read_csv(file_path)
            elif file_path.endswith(".xlsx"):
                data = pd.read_excel(file_path)
            else:
                continue

            total_rows = len(data)
            if total_rows == 0:
                continue  # Skip empty files

            for idx, column in enumerate(data.columns, start=1):
                col_data = data[column]
                data_type = str(col_data.dtypes)
                if "int" in data_type or "float" in data_type:
                    data_type = "Numeric"
                elif "object" in data_type:
                    data_type = "Text"
                elif "datetime" in data_type:
                    data_type = "DateTime"
                
                missing_count = col_data.isnull().sum()
                missing_percentage = (missing_count / total_rows) * 100

                schema_data.append({
                    "File Name": os.path.basename(file_path),
                    "Column Name": column,
                    "Column Order": idx,
                    "Data Type": data_type,
                    "Missing Count": missing_count,
                    "Missing Percentage": f"{missing_percentage:.2f}%",
                    "Total Rows": total_rows
                })

        except Exception as e:
            messagebox.showerror("Error Processing File", f"Error processing {file_path}: {e}")

    return pd.DataFrame(schema_data)

def show_preview(dataframe):
    """Show a preview of the schema definition in a new window."""
    preview_window = Toplevel()
    preview_window.title("Schema Preview")
    preview_window.geometry("800x600")

    frame = Frame(preview_window)
    frame.pack(fill="both", expand=True)

    tree = ttk.Treeview(frame, columns=list(dataframe.columns), show="headings")
    tree.pack(fill="both", expand=True, side="left")

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    for _, row in dataframe.iterrows():
        tree.insert("", "end", values=list(row))

def main():
    root = Tk()
    root.title("Schema Definition Generator")
    root.geometry("400x200")

    def start_process():
        files = select_files()
        if not files:
            messagebox.showwarning("No Files Selected", "Please select at least one file to process.")
            return

        schema_df = generate_schema(files)

        if schema_df.empty:
            messagebox.showwarning("No Data", "No valid data found in the selected files.")
            return

        show_preview(schema_df)
        save_schema(schema_df)

    Label(root, text="Schema Definition Generator", font=("Arial", 16)).pack(pady=10)
    Button(root, text="Select and Process Files", command=start_process, width=30).pack(pady=10)
    Button(root, text="Exit", command=root.quit, width=30).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
